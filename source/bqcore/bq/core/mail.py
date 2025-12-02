"""
Modern Unified Email Service for Bisque

This module provides a modern, centralized email service that replaces the deprecated
TurboMail system and unifies all email functionality across Bisque.

Features:
- Single SMTP configuration point
- Support for both HTML and plain text emails
- Template-based email composition
- Error handling and logging
- Environment variable and config file support
- Backward compatibility with existing configurations

Usage:
    from bq.core.mail import EmailService

    email_service = EmailService()
    email_service.send_email(
        to="user@example.com",
        subject="Welcome to Bisque",
        body="Welcome to our platform!",
        html_body="<h1>Welcome to our platform!</h1>"
    )
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr, formatdate
from typing import List, Optional, Dict, Any

try:
    from tg import config
except ImportError:
    config = None

log = logging.getLogger("bq.core.mail")


class EmailConfiguration:
    """Centralized email configuration management"""

    def __init__(self):
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_username = None
        self.smtp_password = None
        self.smtp_use_tls = True
        self.smtp_use_ssl = False
        self.smtp_timeout = 30
        self.default_from_email = None
        self.default_from_name = None
        self.admin_email = None

        self._load_configuration()

    def _load_configuration(self):
        """Load configuration from environment variables, then config files"""

        # # 1. Environment variables (highest priority)
        # if self._load_from_env():
        #     log.info("Email configuration loaded from environment variables")
        #     return

        # 2. Main Bisque configuration (site.cfg)
        if self._load_from_config():
            log.info("Email configuration loaded from site.cfg")
            log.info("Email configuration summary: %s", self.get_config_summary())
            return

        # 3. Legacy configuration fallback
        if self._load_legacy_config():
            log.info("Email configuration loaded from legacy settings")
            return

        log.warning(
            "No email configuration found - email functionality will be disabled"
        )

    def _load_from_env(self) -> bool:
        """Load configuration from environment variables"""
        env_vars = {
            "BISQUE_SMTP_HOST": "smtp_host",
            "BISQUE_SMTP_PORT": "smtp_port",
            "BISQUE_SMTP_USER": "smtp_username",
            "BISQUE_SMTP_PASSWORD": "smtp_password",
            "BISQUE_SMTP_TLS": "smtp_use_tls",
            "BISQUE_SMTP_SSL": "smtp_use_ssl",
            "BISQUE_SMTP_TIMEOUT": "smtp_timeout",
            "BISQUE_MAIL_FROM": "default_from_email",
            "BISQUE_MAIL_FROM_NAME": "default_from_name",
            "BISQUE_ADMIN_EMAIL": "admin_email",
        }

        found_config = False
        for env_var, attr_name in env_vars.items():
            value = os.environ.get(env_var)
            if value:
                found_config = True
                if attr_name in ["smtp_port", "smtp_timeout"]:
                    value = int(value)
                elif attr_name in ["smtp_use_tls", "smtp_use_ssl"]:
                    value = value.lower() in ("true", "1", "yes", "on")
                setattr(self, attr_name, value)

        # Require minimum configuration
        if (
            found_config
            and self.smtp_host
            and self.smtp_username
            and self.smtp_password
        ):
            return True
        return False

    def _load_from_config(self) -> bool:
        """Load configuration from TurboGears config (site.cfg)"""
        if config:
            return self._load_from_tg_config()
        else:
            # Fallback: load directly from config file when TG config not available
            return self._load_from_config_file()

    def _load_from_tg_config(self) -> bool:
        """Load configuration from TurboGears config object"""
        config_map = {
            "bisque.smtp.host": "smtp_host",
            "bisque.smtp.port": "smtp_port",
            "bisque.smtp.username": "smtp_username",
            "bisque.smtp.password": "smtp_password",
            "bisque.smtp.tls": "smtp_use_tls",
            "bisque.smtp.ssl": "smtp_use_ssl",
            "bisque.smtp.timeout": "smtp_timeout",
            "bisque.mail.from_email": "default_from_email",
            "bisque.mail.from_name": "default_from_name",
            "bisque.admin_email": "admin_email",
        }

        found_config = False
        for config_key, attr_name in config_map.items():
            value = config.get(config_key)
            if value:
                found_config = True
                if attr_name in ["smtp_port", "smtp_timeout"]:
                    value = int(value)
                elif attr_name in ["smtp_use_tls", "smtp_use_ssl"]:
                    value = str(value).lower() in ("true", "1", "yes", "on")
                setattr(self, attr_name, value)
                log.debug(f"Loaded from TG config: {config_key} = {value}")

        log.debug(
            f"TG config loading: found_config={found_config}, smtp_host={getattr(self, 'smtp_host', None)}"
        )

        # Set defaults for missing values and validate required fields
        if found_config and self.smtp_host:
            self.smtp_port = self.smtp_port or (587 if self.smtp_use_tls else 25)
            self.default_from_email = self.default_from_email or self.admin_email

            # For MailerSend and most SMTP providers, username and password are required
            # Only return True if we have the minimum required configuration
            if self.smtp_username and self.smtp_password:
                return True
            else:
                log.debug(
                    f"SMTP configuration incomplete - host: {bool(self.smtp_host)}, username: {bool(self.smtp_username)}, password: {bool(self.smtp_password)}"
                )

        return False

    def _load_from_config_file(self) -> bool:
        """Load configuration directly from site.cfg file (fallback when TG config not available)"""
        try:
            import configparser

            config_file = "config/site.cfg"

            # Try common locations for site.cfg
            possible_paths = [
                config_file,
                "../config/site.cfg",
                os.path.join(os.path.dirname(__file__), "../../config/site.cfg"),
            ]

            config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break

            if not config_path:
                log.debug("Could not find site.cfg file")
                return False

            log.debug(f"Loading config from: {config_path}")

            parser = configparser.ConfigParser()
            parser.read(config_path)

            # Look in [app:main] section
            section = "app:main"
            if not parser.has_section(section):
                log.debug(f"No [{section}] section in config file")
                return False

            config_map = {
                "bisque.smtp.host": "smtp_host",
                "bisque.smtp.port": "smtp_port",
                "bisque.smtp.username": "smtp_username",
                "bisque.smtp.password": "smtp_password",
                "bisque.smtp.tls": "smtp_use_tls",
                "bisque.smtp.ssl": "smtp_use_ssl",
                "bisque.smtp.timeout": "smtp_timeout",
                "bisque.mail.from_email": "default_from_email",
                "bisque.mail.from_name": "default_from_name",
                "bisque.admin_email": "admin_email",
            }

            found_config = False
            for config_key, attr_name in config_map.items():
                if parser.has_option(section, config_key):
                    value = parser.get(section, config_key)
                    # Only skip completely empty values, not those with just whitespace
                    if value is not None:
                        value = value.strip()
                        if value or attr_name in [
                            "smtp_username",
                            "smtp_password",
                        ]:  # Allow empty username/password
                            found_config = True
                            if attr_name in ["smtp_port", "smtp_timeout"]:
                                value = int(value) if value else 0
                            elif attr_name in ["smtp_use_tls", "smtp_use_ssl"]:
                                value = str(value).lower() in ("true", "1", "yes", "on")
                            setattr(self, attr_name, value)
                            log.debug(f"Set {attr_name} = {value}")

            # Set defaults for missing values
            if found_config and self.smtp_host:
                self.smtp_port = getattr(self, "smtp_port", None) or (
                    587 if getattr(self, "smtp_use_tls", False) else 25
                )
                self.default_from_email = getattr(
                    self, "default_from_email", None
                ) or getattr(self, "admin_email", None)
                log.info(f"Email configuration loaded from {config_path}")
                return True
            else:
                log.debug(f"No valid email configuration found in {config_path}")

        except Exception as e:
            log.debug(f"Failed to load config from file: {e}")
            import traceback

            traceback.print_exc()

        return False

    def _load_legacy_config(self) -> bool:
        """Load configuration from legacy settings for backward compatibility"""
        if not config:
            return False

        # Check legacy patterns
        legacy_configs = [
            # Legacy TurboGears SMTP
            ("smtp.host", "smtp_host"),
            ("smtp.username", "smtp_username"),
            ("smtp.password", "smtp_password"),
            ("smtp.port", "smtp_port"),
            ("mail.smtp.server", "smtp_host"),
            ("bisque.admin_email", "admin_email"),
            ("error_email_from", "default_from_email"),
        ]

        found_config = False
        for config_key, attr_name in legacy_configs:
            value = config.get(config_key)
            if value and not getattr(self, attr_name):
                found_config = True
                if attr_name == "smtp_port":
                    value = int(value) if str(value).isdigit() else 25
                setattr(self, attr_name, value)

        if found_config and self.smtp_host:
            self.smtp_port = self.smtp_port or 25
            self.default_from_email = self.default_from_email or self.admin_email
            return True
        return False

    def is_configured(self) -> bool:
        """Check if email is properly configured"""
        return bool(self.smtp_host and self.default_from_email)

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration (without sensitive data)"""
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "smtp_use_tls": self.smtp_use_tls,
            "smtp_use_ssl": self.smtp_use_ssl,
            "default_from_email": self.default_from_email,
            "default_from_name": self.default_from_name,
            "admin_email": self.admin_email,
            "configured": self.is_configured(),
        }


class EmailService:
    """Modern unified email service for Bisque"""

    def __init__(self, config: Optional[EmailConfiguration] = None):
        log.info(
            f"Initializing EmailService with config: {config} {config.get_config_summary() if config else 'None'}"
        )
        self.config = config or EmailConfiguration()

    def is_available(self) -> bool:
        """Check if email service is available and configured"""
        return self.config.is_configured()

    def test_connection(self) -> Dict[str, Any]:
        """Test SMTP connection and return result"""
        if not self.is_available():
            return {"success": False, "error": "Email service not configured"}

        try:
            server = self._get_smtp_server()
            server.quit()
            return {
                "success": True,
                "message": f"Successfully connected to {self.config.smtp_host}:{self.config.smtp_port}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to connect to SMTP server: {str(e)}",
            }

    def send_email(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email with modern SMTP support

        Args:
            to: Recipient email(s)
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            from_email: Sender email (defaults to configured from_email)
            from_name: Sender name (optional)
            reply_to: Reply-to email (optional)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            attachments: List of attachments (optional)

        Returns:
            Dict with success status and message/error
        """

        if not self.is_available():
            return {"success": False, "error": "Email service not configured"}

        try:
            # Prepare recipients
            to_list = [to] if isinstance(to, str) else to

            # Create message
            msg = (
                MIMEMultipart("alternative")
                if html_body
                else MIMEText(body, "plain", "utf-8")
            )

            if isinstance(msg, MIMEMultipart):
                # Add both plain text and HTML parts
                msg.attach(MIMEText(body, "plain", "utf-8"))
                msg.attach(MIMEText(html_body, "html", "utf-8"))

            # Set headers
            from_email = from_email or self.config.default_from_email
            if from_name:
                msg["From"] = formataddr((from_name, from_email))
            else:
                msg["From"] = from_email

            msg["To"] = ", ".join(to_list)
            msg["Subject"] = subject
            msg["Date"] = formatdate(localtime=True)

            if reply_to:
                msg["Reply-To"] = reply_to
            if cc:
                msg["Cc"] = ", ".join(cc)
                to_list.extend(cc)
            if bcc:
                to_list.extend(bcc)

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)

            # Send email
            server = self._get_smtp_server()
            text = msg.as_string()
            server.sendmail(from_email, to_list, text)
            server.quit()

            log.info(f"Email sent successfully to {', '.join(to_list)}")
            return {
                "success": True,
                "message": f"Email sent to {len(to_list)} recipient(s)",
            }

        except Exception as e:
            log.error(f"Failed to send email: {e}")
            return {"success": False, "error": str(e)}

    def send_template_email(
        self,
        template_name: str,
        to: str | List[str],
        context: Dict[str, Any],
        subject: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Send an email using a template

        Args:
            template_name: Name of the email template
            to: Recipient email(s)
            context: Template context variables
            subject: Email subject (can be in template)
            **kwargs: Additional arguments for send_email
        """

        # This is a placeholder for template functionality
        # In a full implementation, you would load templates from files
        # and render them with the provided context

        templates = {
            "user_registration": {
                "subject": "Welcome to Bisque - Registration Successful",
                "body": """Hello {username},

Welcome to Bisque! Your account has been successfully created.

Your login details:
- Username: {username}
- Email: {email}

You can now access the system and start using Bisque for your research.

Best regards,
The Bisque Team""",
                "html_body": """<html><body>
<h2>Welcome to Bisque!</h2>
<p>Hello <strong>{username}</strong>,</p>
<p>Your account has been successfully created.</p>
<h3>Your login details:</h3>
<ul>
<li><strong>Username:</strong> {username}</li>
<li><strong>Email:</strong> {email}</li>
</ul>
<p>You can now access the system and start using Bisque for your research.</p>
<p>Best regards,<br>The Bisque Team</p>
</body></html>""",
            },
            "email_verification": {
                "subject": "Bisque - Please verify your email address",
                "body": """Hello {username},

Please verify your email address by clicking the link below:

{verification_link}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
The Bisque Team""",
                "html_body": """<html><body>
<h2>Email Verification Required</h2>
<p>Hello <strong>{username}</strong>,</p>
<p>Please verify your email address by clicking the button below:</p>
<p><a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email Address</a></p>
<p>Or copy and paste this link in your browser:<br>
<a href="{verification_link}">{verification_link}</a></p>
<p><em>This link will expire in 24 hours.</em></p>
<p>If you didn't create this account, please ignore this email.</p>
<p>Best regards,<br>The Bisque Team</p>
</body></html>""",
            },
            "admin_notification": {
                "subject": "Bisque System Notification",
                "body": """System Notification

{message}

Details:
{details}

Bisque System""",
                "html_body": """<html><body>
<h2>System Notification</h2>
<p>{message}</p>
<h3>Details:</h3>
<pre>{details}</pre>
<p><em>Bisque System</em></p>
</body></html>""",
            },
        }

        if template_name not in templates:
            return {"success": False, "error": f'Template "{template_name}" not found'}

        template = templates[template_name]

        # Render template
        try:
            rendered_subject = subject or template["subject"].format(**context)
            rendered_body = template["body"].format(**context)
            rendered_html = template.get("html_body", "").format(**context)

            return self.send_email(
                to=to,
                subject=rendered_subject,
                body=rendered_body,
                html_body=rendered_html if rendered_html else None,
                **kwargs,
            )

        except KeyError as e:
            return {"success": False, "error": f"Missing template variable: {e}"}

    def _get_smtp_server(self):
        """Create and configure SMTP server connection"""
        if self.config.smtp_use_ssl:
            server = smtplib.SMTP_SSL(
                self.config.smtp_host,
                self.config.smtp_port,
                timeout=self.config.smtp_timeout,
            )
        else:
            server = smtplib.SMTP(
                self.config.smtp_host,
                self.config.smtp_port,
                timeout=self.config.smtp_timeout,
            )
            if self.config.smtp_use_tls:
                server.starttls()

        if self.config.smtp_username and self.config.smtp_password:
            server.login(self.config.smtp_username, self.config.smtp_password)

        return server

    def _add_attachment(self, msg, attachment: Dict[str, Any]):
        """Add an attachment to the email message"""
        filename = attachment.get("filename", "attachment")
        content = attachment.get("content", b"")
        content_type = attachment.get("content_type", "application/octet-stream")

        part = MIMEBase(*content_type.split("/", 1))
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
        msg.attach(part)


# Global email service instance
_email_service = None


def get_email_service() -> EmailService:
    """Get the global email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


def send_email(*args, **kwargs):
    """Convenience function to send email using the global service"""
    return get_email_service().send_email(*args, **kwargs)


def send_template_email(*args, **kwargs):
    """Convenience function to send template email using the global service"""
    return get_email_service().send_template_email(*args, **kwargs)


def is_email_available() -> bool:
    """Check if email service is available"""
    return get_email_service().is_available()
