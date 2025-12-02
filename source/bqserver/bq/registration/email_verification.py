"""
Email Verification System for Bisque Registration

This module provides email verification functionality for user registration.
Now uses the unified Bisque email service for all email operations.

Features:
- Unified SMTP configuration via bq.core.mail
- Secure verification token generation
- Email template rendering via unified service
- Optional email verification (configurable)
"""

import os
import logging
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

try:
    from tg import config

    TG_AVAILABLE = True
except ImportError:
    TG_AVAILABLE = False
    config = None

try:
    from bq.core.model import DBSession
    from bq.data_service.model.tag_model import Tag

    BQ_MODELS_AVAILABLE = True
except ImportError:
    BQ_MODELS_AVAILABLE = False
    DBSession = None
    Tag = None

try:
    from bq.core.mail import get_email_service, is_email_available

    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False
    get_email_service = None
    is_email_available = None

log = logging.getLogger("bq.registration.email")


def _to_bool(value):
    """Convert various truthy/falsy values to boolean"""
    if isinstance(value, str):
        value = value.lower()
    return value in [True, "true", "1", "yes", "on"]


class EmailVerificationError(Exception):
    """Custom exception for email verification errors"""

    pass


class EmailVerificationService:
    """Service for handling email verification using the unified email system"""

    def __init__(self):
        # Check if all required dependencies are available
        if not EMAIL_SERVICE_AVAILABLE:
            raise ImportError(
                "Unified email service not available - email verification disabled"
            )
        if not TG_AVAILABLE:
            raise ImportError("TurboGears not available - email verification disabled")
        if not BQ_MODELS_AVAILABLE:
            raise ImportError(
                "Bisque models not available - email verification disabled"
            )

        self.email_service = get_email_service()
        self.verification_enabled = self._is_verification_enabled()
        log.info(
            f"Email verification service initialized: self.email_service = {self.email_service}, verification_enabled = {self.verification_enabled}"
        )

    def _is_verification_enabled(self):
        """Check if email verification is enabled in configuration"""
        # Check environment variable first (for Docker/container deployments)
        # env_enabled = os.environ.get('BISQUE_EMAIL_VERIFICATION_ENABLED', 'false').lower()
        # if env_enabled in ['true', '1', 'yes', 'on']:
        #     return True

        # Check main Bisque configuration
        config_enabled = config.get(
            "bisque.registration.email_verification.enabled", False
        )
        if _to_bool(config_enabled):
            return True

        # Check legacy configurations for backward compatibility
        legacy_enabled = config.get(
            "registration.email_verification.enabled", False
        ) or config.get("email_verification.enabled", False)
        return _to_bool(legacy_enabled)

    def is_available(self):
        """Check if email verification is available (SMTP configured and verification enabled)"""
        available = self.email_service.is_available() and self.verification_enabled
        if not available:
            if not self.email_service.is_available():
                log.debug(
                    "Email verification unavailable: Email service not configured"
                )
            if not self.verification_enabled:
                log.debug(
                    "Email verification unavailable: verification disabled in config"
                )
        return available

    def validate_configuration(self):
        """Validate the current email verification configuration and return status"""
        status = {
            "available": False,
            "smtp_configured": self.email_service.is_available(),
            "verification_enabled": self.verification_enabled,
            "errors": [],
            "warnings": [],
        }

        # Check unified email service configuration
        if not self.email_service.is_available():
            config_summary = self.email_service.config.get_config_summary()
            if not config_summary.get("smtp_host"):
                status["errors"].append("SMTP host not configured")
            if not config_summary.get("default_from_email"):
                status["errors"].append("From email address not configured")
            if not config_summary["configured"]:
                status["errors"].append("Email service not properly configured")

        # Check verification enabled
        if not self.verification_enabled:
            status["warnings"].append(
                "Email verification is disabled - users will be auto-verified"
            )

        status["available"] = (
            self.email_service.is_available()
            and self.verification_enabled
            and len(status["errors"]) == 0
        )

        return status

    def test_smtp_connection(self):
        """Test SMTP connection using the unified email service"""
        if not self.email_service.is_available():
            return {"success": False, "error": "Email service not configured"}

        return self.email_service.test_connection()

    def generate_verification_token(self, email, username):
        """Generate a secure verification token"""
        # Create a secure random token
        random_token = secrets.token_urlsafe(32)

        # Add timestamp (use Unix timestamp for easier verification)
        timestamp = int(datetime.now(timezone.utc).timestamp())
        token_data = f"{random_token}:{email}:{username}:{timestamp}"

        # Hash the token data
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()

        return f"{random_token}.{timestamp}.{token_hash[:16]}"

    def verify_token(self, token, email, username, max_age_hours=24):
        """Verify a verification token"""
        try:
            log.info(
                f"Verifying token: {token} for email: {email}, username: {username}"
            )

            # Parse token - handle both old and new formats
            parts = token.split(".")

            if len(parts) == 3:
                # New format: random_token.timestamp.hash
                random_token, timestamp_str, token_hash = parts

                try:
                    timestamp = int(timestamp_str)
                except ValueError:
                    log.error(f"Invalid timestamp in token: {timestamp_str}")
                    return False

                # Check if token is not too old
                now = int(datetime.now(timezone.utc).timestamp())
                age_seconds = now - timestamp
                max_age_seconds = max_age_hours * 3600

                if age_seconds > max_age_seconds:
                    log.error(
                        f"Token expired - age: {age_seconds}s, max_age: {max_age_seconds}s"
                    )
                    return False

                if age_seconds < 0:
                    log.error(f"Token from future - age: {age_seconds}s")
                    return False

                # Verify the token hash
                token_data = f"{random_token}:{email}:{username}:{timestamp}"
                expected_hash = hashlib.sha256(token_data.encode()).hexdigest()[:16]

                log.info(f"New format - Token data: {token_data}")
                log.info(f"Expected hash: {expected_hash}, actual hash: {token_hash}")

                return expected_hash == token_hash

            elif len(parts) == 2:
                # Old format: random_token.hash - use fallback verification
                log.info(f"Using legacy token verification for old format token")
                random_token, token_hash = parts

                # For old tokens, check a reasonable time range (last 7 days)
                now = datetime.now(timezone.utc)

                # Check tokens generated within the last max_age_hours, but limit to reasonable range
                for hours_ago in range(
                    min(max_age_hours, 168)
                ):  # Max 7 days for old tokens
                    check_time = now - timedelta(hours=hours_ago)
                    # Check a few minute intervals to account for timestamp precision
                    for minute_offset in [0, 1, 2, 3, 4, 5]:
                        check_timestamp = (
                            check_time - timedelta(minutes=minute_offset)
                        ).isoformat()
                        token_data = (
                            f"{random_token}:{email}:{username}:{check_timestamp}"
                        )
                        expected_hash = hashlib.sha256(token_data.encode()).hexdigest()[
                            :16
                        ]

                        if expected_hash == token_hash:
                            log.info(
                                f"Legacy token verified with timestamp: {check_timestamp}"
                            )
                            return True

                log.error(f"Legacy token verification failed")
                return False
            else:
                log.error(
                    f"Token format invalid - expected 2 or 3 parts, got {len(parts)}"
                )
                return False

        except Exception as e:
            log.error(f"Error verifying token: {e}")
            import traceback

            log.error(traceback.format_exc())
            return False

    def send_verification_email(
        self, email, username, fullname, verification_token, base_url
    ):
        """Send verification email using the unified email service"""
        if not self.is_available():
            return {
                "success": False,
                "error": "Email verification service not available",
            }

        # Build verification URL - use verify_email endpoint with query parameters
        verification_url = f"{base_url}/registration/verify_email?token={verification_token}&email={email}"

        log.info(f"Generated verification URL for {email}: {verification_url}")

        # Use the unified email service template
        context = {
            "username": username,
            "fullname": fullname,
            "email": email,
            "verification_link": verification_url,
        }

        result = self.email_service.send_template_email(
            template_name="email_verification", to=email, context=context
        )

        if result["success"]:
            log.info(f"Verification email sent successfully to {email}")
            return {"success": True}
        else:
            log.error(
                f"Failed to send verification email to {email}: {result['error']}"
            )
            return {
                "success": False,
                "error": f"Failed to send verification email: {result['error']}",
            }

    def mark_user_as_verified(self, bq_user):
        """Mark a user's email as verified"""
        try:
            # Add email_verified tag
            verified_tag = Tag(parent=bq_user)
            verified_tag.name = "email_verified"
            verified_tag.value = "true"
            verified_tag.owner = bq_user
            DBSession.add(verified_tag)

            # Add verification timestamp
            verified_time_tag = Tag(parent=bq_user)
            verified_time_tag.name = "email_verified_at"
            verified_time_tag.value = datetime.now(timezone.utc).isoformat()
            verified_time_tag.owner = bq_user
            DBSession.add(verified_time_tag)

            DBSession.flush()
            log.info(f"User {bq_user.resource_name} marked as email verified")
            return {"success": True}

        except Exception as e:
            log.error(f"Failed to mark user as verified: {e}")
            return {"success": False, "error": f"Failed to mark user as verified: {e}"}

    def is_user_verified(self, bq_user):
        """Check if a user's email is verified"""
        try:
            log.info(
                f"Checking verification status for user: {bq_user.resource_name} (ID: {bq_user.id})"
            )

            verified_tag = (
                DBSession.query(Tag)
                .filter(
                    Tag.parent == bq_user,
                    Tag.resource_name == "email_verified",
                    Tag.resource_value == "true",
                )
                .first()
            )

            log.info(f"Email verified tag found: {verified_tag is not None}")
            if verified_tag:
                log.info(
                    f"Verification tag details: name={verified_tag.resource_name}, value={verified_tag.resource_value}"
                )

            return verified_tag is not None

        except Exception as e:
            log.error(f"Failed to check user verification status: {e}")
            import traceback

            log.error(traceback.format_exc())
            return False

    # Password Reset Methods
    def generate_password_reset_token(self, email, username):
        """Generate a password reset token"""
        try:
            import secrets
            import hashlib
            from datetime import datetime, timezone

            # Generate a secure token with timestamp
            timestamp = int(datetime.now(timezone.utc).timestamp())
            random_part = secrets.token_urlsafe(32)

            # Create token data
            token_data = f"{email}:{username}:{timestamp}:{random_part}"

            # Create a hash for verification
            token_hash = hashlib.sha256(token_data.encode()).hexdigest()

            # Return the complete token (data + hash)
            reset_token = f"{token_data}:{token_hash}"

            log.info(f"Generated password reset token for {username} ({email})")
            return reset_token

        except Exception as e:
            log.error(f"Failed to generate password reset token for {email}: {e}")
            return None

    def verify_password_reset_token(self, token, email, username, max_age_hours=24):
        """Verify a password reset token"""
        try:
            if not token or not email or not username:
                log.error(
                    "Missing token, email, or username for password reset verification"
                )
                return False

            # Split token into data and hash
            parts = token.split(":")
            if len(parts) != 5:
                log.error(
                    f"Password reset token format invalid - expected 5 parts, got {len(parts)}"
                )
                return False

            token_email, token_username, timestamp_str, random_part, token_hash = parts

            # Verify the token components match
            if token_email != email or token_username != username:
                log.error(
                    f"Password reset token email/username mismatch - expected {email}/{username}, got {token_email}/{token_username}"
                )
                return False

            # Verify timestamp is not too old
            try:
                from datetime import datetime, timezone, timedelta

                token_timestamp = int(timestamp_str)
                current_timestamp = int(datetime.now(timezone.utc).timestamp())
                age_hours = (current_timestamp - token_timestamp) / 3600

                if age_hours > max_age_hours:
                    log.error(
                        f"Password reset token expired - age: {age_hours:.1f} hours"
                    )
                    return False

                if age_hours < 0:
                    log.error(
                        f"Password reset token from future - age: {age_hours:.1f} hours"
                    )
                    return False

            except (ValueError, TypeError) as e:
                log.error(
                    f"Invalid timestamp in password reset token: {timestamp_str}: {e}"
                )
                return False

            # Verify hash
            import hashlib

            token_data = f"{token_email}:{token_username}:{timestamp_str}:{random_part}"
            expected_hash = hashlib.sha256(token_data.encode()).hexdigest()

            if expected_hash != token_hash:
                log.error("Password reset token hash verification failed")
                return False

            log.info(
                f"Password reset token verified successfully for {username} ({email})"
            )
            return True

        except Exception as e:
            log.error(f"Failed to verify password reset token: {e}")
            return False

    def send_password_reset_email(
        self, email, username, fullname, reset_token, base_url
    ):
        """Send a password reset email"""
        try:
            if not self.is_available():
                return {"success": False, "error": "Email service not available"}

            # Create reset URL
            reset_url = f"{base_url}/registration/reset_password?token={reset_token}&email={email}"

            # Email content
            subject = "Password Reset Request - Bisque"

            text_body = f"""
Hello {fullname},

You have requested a password reset for your Bisque account ({username}).

To reset your password, click the following link:
{reset_url}

This link will expire in 24 hours.

If you did not request this password reset, please ignore this email.

Best regards,
The Bisque Team
"""

            html_body = f"""
<html>
<body>
<h2>Password Reset Request</h2>
<p>Hello <strong>{fullname}</strong>,</p>
<p>You have requested a password reset for your Bisque account (<strong>{username}</strong>).</p>
<p>To reset your password, click the following link:</p>
<p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Reset Password</a></p>
<p>Or copy and paste this URL into your browser:</p>
<p><a href="{reset_url}">{reset_url}</a></p>
<p><strong>This link will expire in 24 hours.</strong></p>
<p>If you did not request this password reset, please ignore this email.</p>
<br>
<p>Best regards,<br>The Bisque Team</p>
</body>
</html>
"""

            # Send email
            result = self.email_service.send_email(
                to=email, subject=subject, body=text_body, html_body=html_body
            )
            if result["success"]:
                log.info(f"Password reset email sent successfully to {email}")
            else:
                log.error(
                    f"Failed to send password reset email to {email}: {result['error']}"
                )

            return result

        except Exception as e:
            log.error(f"Failed to send password reset email to {email}: {e}")
            return {"success": False, "error": str(e)}

    def reset_user_password(self, bq_user, new_password):
        """Reset a user's password"""
        try:
            # Get the TurboGears user associated with this BQUser
            from bq.core.model.auth import User
            from bq.core.model import DBSession

            # Find the TG user by username
            username = bq_user.resource_name
            tg_user = User.by_user_name(username)

            if not tg_user:
                log.error(f"TurboGears user not found for username: {username}")
                return {"success": False, "error": "User not found"}

            # Update the password
            tg_user.password = new_password
            DBSession.flush()

            log.info(f"Password reset successfully for user: {username}")
            return {"success": True}

        except Exception as e:
            log.error(f"Failed to reset password for user {bq_user.resource_name}: {e}")
            return {"success": False, "error": str(e)}

    def mark_user_as_unverified(self, bq_user):
        """Mark a user's email as unverified (e.g., when they change email)"""
        try:
            log.info(f"Marking user {bq_user.resource_name} as email unverified")

            # Remove verification tags
            verified_tag = (
                DBSession.query(Tag)
                .filter(Tag.parent == bq_user, Tag.resource_name == "email_verified")
                .first()
            )

            if verified_tag:
                DBSession.delete(verified_tag)
                log.info(f"Removed email_verified tag for user {bq_user.resource_name}")

            verified_time_tag = (
                DBSession.query(Tag)
                .filter(
                    Tag.parent == bq_user, Tag.resource_name == "email_verified_time"
                )
                .first()
            )

            if verified_time_tag:
                DBSession.delete(verified_time_tag)
                log.info(
                    f"Removed email_verified_time tag for user {bq_user.resource_name}"
                )

            # Remove any existing verification token to force new verification
            token_tag = (
                DBSession.query(Tag)
                .filter(Tag.parent == bq_user, Tag.name == "email_verification_token")
                .first()
            )

            if token_tag:
                DBSession.delete(token_tag)
                log.info(
                    f"Removed old verification token for user {bq_user.resource_name}"
                )

            DBSession.flush()
            log.info(f"User {bq_user.resource_name} marked as email unverified")
            return {"success": True}

        except Exception as e:
            log.error(f"Failed to mark user as unverified: {e}")
            return {
                "success": False,
                "error": f"Failed to mark user as unverified: {e}",
            }


# Global email verification service instance
_email_verification_service = None


def get_email_verification_service():
    """Get the global email verification service instance"""
    global _email_verification_service
    if _email_verification_service is None:
        try:
            _email_verification_service = EmailVerificationService()
        except ImportError as e:
            log.warning(f"Email verification service not available: {e}")
            _email_verification_service = False  # Mark as unavailable
    return (
        _email_verification_service
        if _email_verification_service is not False
        else None
    )


def is_email_verification_available():
    """Check if email verification service is available"""
    service = get_email_verification_service()
    return service is not None and service.is_available()
