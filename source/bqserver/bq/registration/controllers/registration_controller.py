import logging
from tg import expose, validate, request, redirect, flash
from tg.exceptions import HTTPFound
from bq.core.lib.base import BaseController
from bq.core.model import DBSession
from bq.core.model.auth import User

# Import domain models for authorization checking
try:
    from bq.data_service.model.domain_model import AuthorizedEmailDomain
    DOMAIN_MODELS_AVAILABLE = True
except ImportError:
    DOMAIN_MODELS_AVAILABLE = False
    AuthorizedEmailDomain = None

# Import email verification conditionally to avoid import errors during service loading
try:
    from bq.registration.email_verification import (
        EmailVerificationService,
        EmailVerificationError,
    )

    EMAIL_VERIFICATION_AVAILABLE = True
except ImportError as e:
    EMAIL_VERIFICATION_AVAILABLE = False
    EmailVerificationService = None
    EmailVerificationError = Exception
    import logging

    logging.getLogger("bq.registration").warning(
        f"Email verification not available due to import error: {e}"
    )

log = logging.getLogger("bq.registration")


class RegistrationController(BaseController):
    """
    Enhanced registration controller for Bisque user registration
    Supports: email, username, fullname, research area, institution, funding agency
    With optional email verification
    """

    service_type = "registration"

    def __init__(self):
        super().__init__()
        # Initialize email verification service safely
        self.email_service = None

        if not EMAIL_VERIFICATION_AVAILABLE:
            log.info(
                "Email verification disabled - service not available due to import issues"
            )
            return

        try:
            self.email_service = EmailVerificationService()

            # Log email verification status at startup
            config_status = self._safe_email_call(
                "validate_configuration",
            )
            if config_status["available"]:
                log.info("Email verification service initialized and ready")
            else:
                if not config_status["smtp_configured"]:
                    log.info("Email verification disabled: SMTP not configured")
                elif not config_status["verification_enabled"]:
                    log.info(
                        "Email verification disabled: feature not enabled in configuration"
                    )
                else:
                    log.warning(
                        f"Email verification disabled due to configuration errors: {config_status['errors']}"
                    )
                log.info("Users will remain unverified and require admin approval")
        except Exception as e:
            log.warning(f"Failed to initialize email verification service: {e}")
            log.info(
                "Email verification disabled - users will remain unverified and require admin approval"
            )
            self.email_service = None

    def _safe_email_call(self, method_name, *args, **kwargs):
        """Safely call an email service method, returning default values if service unavailable"""
        log.info(
            f"self.email_service is {self.email_service} Calling email service method: {method_name} with args: {args}, kwargs: {kwargs}"
        )
        if self.email_service is None:
            # Return default values based on method name
            if method_name == "is_available":
                return False
            elif method_name == "validate_configuration":
                return {
                    "available": False,
                    "smtp_configured": False,
                    "verification_enabled": False,
                    "errors": ["Email verification service not initialized"],
                }
            elif method_name == "is_user_verified":
                return False  # Default to unverified if no email service - requires admin approval
            elif method_name == "test_smtp_connection":
                return {"success": False, "error": "Email service not available"}
            elif method_name in [
                "generate_verification_token",
                "send_verification_email",
                "mark_user_as_verified",
            ]:
                return None  # These need explicit error handling
            else:
                return None

        try:
            method = getattr(self.email_service, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            log.warning(f"Email service method {method_name} failed: {e}")
            # Return safe defaults
            if method_name == "is_available":
                return False
            elif method_name == "is_user_verified":
                return False  # Default to unverified if check fails - requires admin approval
            elif method_name in [
                "generate_verification_token",
                "send_verification_email",
                "mark_user_as_verified",
            ]:
                return None  # These need explicit error handling
            else:
                return None

    def _is_domain_authorized(self, email):
        """Check if email domain is in authorized domains list"""
        if not email or '@' not in email:
            log.warning(f"Invalid email format: {email}")
            return False
        
        domain = email.split('@')[1].lower()
        
        try:
            # Use the domain model to check authorization - pass the full email
            from bq.data_service.model.domain_model import is_domain_authorized
            result = is_domain_authorized(email)  # Pass full email, not just domain
            log.info(f"Domain authorization check for {domain}: {result}")
            return result
        except Exception as e:
            log.error(f"Error checking domain authorization for {domain}: {e}")
            # For security, default to DENYING registration if check fails
            # This ensures domain management is properly enforced
            log.warning(f"Domain authorization check failed, denying registration for security: {e}")
            return False

    def _create_pending_registration(self, email, username, fullname, password, 
                                   research_area, institution_affiliation, funding_agency=None):
        """Create a pending registration request"""
        try:
            # Ensure tables exist first
            from bq.admin_service.controllers.service import ensure_domain_tables
            ensure_domain_tables()
            
            from bq.data_service.model.domain_model import add_pending_registration
            
            # Use the helper function to add pending registration
            success = add_pending_registration(email, fullname, password)
            
            if success:
                log.info(f"Created pending registration for {email}")
                return True
            else:
                log.error(f"Failed to create pending registration for {email}")
                return False
                
        except Exception as e:
            log.error(f"Failed to create pending registration for {email}: {e}")
            raise

    @expose("bq.registration.templates.index")
    def index(self, **kw):
        """Registration form page"""
        # Get email verification configuration status
        email_verification_status = self._safe_email_call("validate_configuration")
        email_verification_enabled = email_verification_status["available"]

        # Log configuration status for debugging
        if email_verification_enabled:
            log.info("Email verification is enabled and properly configured")
        else:
            log.info(
                f"Email verification disabled - SMTP configured: {email_verification_status['smtp_configured']}, "
                f"Verification enabled: {email_verification_status['verification_enabled']}"
            )
            if email_verification_status["errors"]:
                log.warning(
                    f"Email verification configuration errors: {email_verification_status['errors']}"
                )

        return {
            "msg": "Welcome to user registration",
            "email_verification_enabled": email_verification_enabled,
            "email_verification_status": email_verification_status,
        }

    @expose("json")
    def register(self, **kw):
        """
        Enhanced user registration endpoint
        Accepts: email, username, fullname, password, research_area, institution_affiliation, funding_agency
        """
        try:
            # Extract required fields
            email = kw.get("email", "").strip()
            username = kw.get("username", "").strip()
            fullname = kw.get("fullname", "").strip()
            password = kw.get("password", "").strip()
            research_area = kw.get("research_area", "").strip()
            institution_affiliation = kw.get("institution_affiliation", "").strip()
            funding_agency = kw.get("funding_agency", "").strip()

            # Validation
            if not email or not username or not fullname or not password:
                return {
                    "status": "error",
                    "message": "Missing required fields: email, username, fullname, and password are required",
                }

            if not research_area or not institution_affiliation:
                return {
                    "status": "error",
                    "message": "Research area and institution affiliation are required",
                }

            if len(password) < 6:
                return {
                    "status": "error",
                    "message": "Password must be at least 6 characters long",
                }

            # Check for existing users
            existing_user_email = User.by_email_address(email)
            if existing_user_email:
                return {
                    "status": "error",
                    "message": "A user with this email address already exists",
                }

            existing_user_name = User.by_user_name(username)
            if existing_user_name:
                return {"status": "error", "message": "This username is already taken"}

            # Check if domain is authorized for registration
            if not self._is_domain_authorized(email):
                domain = email.split('@')[1] if '@' in email else 'unknown'
                log.info(f"Registration attempt from unauthorized domain: {domain}")
                return {
                    "status": "error",
                    "message": f"Registration not allowed for domain '{domain}'. Please contact an administrator to authorize your domain for registration."
                }

            # Validate research area options
            valid_research_areas = [
                "Bioinformatics",
                "Cell Biology",
                "Developmental Biology",
                "Ecology",
                "Genetics",
                "Immunology",
                "Materials Science",
                "Microbiology",
                "Molecular Biology",
                "Neuroscience",
                "Pharmacology",
                "Plant Biology",
                "Structural Biology",
                "Other",
            ]
            if research_area and research_area not in valid_research_areas:
                return {
                    "status": "error",
                    "message": f'Invalid research area. Must be one of: {", ".join(valid_research_areas)}',
                }

            # Validate funding agency options (optional field)
            valid_funding_agencies = [
                "NIH",
                "NSF",
                "DOE",
                "DoD",
                "NASA",
                "USDA",
                "Private_Foundation",
                "Industry",
                "International",
                "Other",
                "None",
                "",
            ]
            if funding_agency and funding_agency not in valid_funding_agencies:
                return {
                    "status": "error",
                    "message": f'Invalid funding agency. Must be one of: {", ".join(valid_funding_agencies)}',
                }

            log.info(f"Creating new user: {username} ({email})")

            # Create the core TurboGears User first
            tg_user = User(
                user_name=username,
                email_address=email,
                display_name=fullname,
                password=password,
            )
            DBSession.add(tg_user)
            DBSession.flush()  # Get the TG user ID, this also triggers bquser_callback

            # The bquser_callback automatically creates a BQUser, so let's find it
            from bq.data_service.model import BQUser

            bq_user = DBSession.query(BQUser).filter_by(resource_name=username).first()
            if not bq_user:
                # Fallback: create BQUser manually if callback didn't work
                bq_user = BQUser(tg_user=tg_user, create_tg=False, create_store=True)
                DBSession.add(bq_user)
                DBSession.flush()
                bq_user.owner_id = bq_user.id

            # Now add custom tags for the extended profile information
            from bq.data_service.model.tag_model import Tag

            # Create all tags now that bq_user has an ID
            fullname_tag = Tag(parent=bq_user)
            fullname_tag.name = "fullname"
            fullname_tag.value = fullname
            fullname_tag.owner = bq_user
            DBSession.add(fullname_tag)

            username_tag = Tag(parent=bq_user)
            username_tag.name = "username"
            username_tag.value = username
            username_tag.owner = bq_user
            DBSession.add(username_tag)

            research_area_tag = Tag(parent=bq_user)
            research_area_tag.name = "research_area"
            research_area_tag.value = research_area
            research_area_tag.owner = bq_user
            DBSession.add(research_area_tag)

            institution_tag = Tag(parent=bq_user)
            institution_tag.name = "institution_affiliation"
            institution_tag.value = institution_affiliation
            institution_tag.owner = bq_user
            DBSession.add(institution_tag)

            # Add funding agency tag (if provided)
            if funding_agency:
                funding_tag = Tag(parent=bq_user)
                funding_tag.name = "funding_agency"
                funding_tag.value = funding_agency
                funding_tag.owner = bq_user
                DBSession.add(funding_tag)

            log.info(
                f"Successfully created user: {username} with ID: {bq_user.resource_uniq}"
            )

            # Handle email verification if enabled
            verification_message = ""

            # Use the same validation approach as index method
            email_verification_status = self._safe_email_call("validate_configuration")
            email_verification_available = (
                email_verification_status.get("available", False)
                if email_verification_status
                else False
            )

            log.info(f"Email verification validation: {email_verification_status}")
            log.info(f"Email verification available: {email_verification_available}")

            if email_verification_available:
                log.info("Email verification is enabled - sending verification email")
                try:
                    # Test SMTP connection first
                    smtp_test = self._safe_email_call(
                        "test_smtp_connection",
                    )
                    if not smtp_test["success"]:
                        log.error(f"SMTP connection test failed: {smtp_test['error']}")
                        raise EmailVerificationError(
                            f"SMTP connection failed: {smtp_test['error']}"
                        )

                    # Generate verification token
                    verification_token = self._safe_email_call(
                        "generate_verification_token", email, username
                    )
                    if not verification_token:
                        log.error(f"Failed to generate verification token for {email}")
                        flash(
                            f"Registration completed but email verification failed. You can request a new verification email.",
                            "warning",
                        )
                        self._safe_email_call("mark_user_as_verified", bq_user)
                        redirect("/client_service/")

                    # Get base URL for verification link
                    base_url = request.host_url.rstrip("/")

                    # Send verification email
                    send_result = self._safe_email_call(
                        "send_verification_email",
                        email,
                        username,
                        fullname,
                        verification_token,
                        base_url,
                    )
                    if not send_result or not send_result.get("success"):
                        log.error(f"Failed to send verification email for {email}")
                        flash(
                            "Registration completed but failed to send verification email. Please use the resend verification feature.",
                            "warning",
                        )
                        # Still proceed with registration but show warning

                    verification_message = " A verification email has been sent to your email address. Please check your email and click the verification link to activate your account."

                    # Store verification token as a tag for later verification
                    token_tag = Tag(parent=bq_user)
                    token_tag.name = "email_verification_token"
                    token_tag.value = verification_token
                    token_tag.owner = bq_user
                    DBSession.add(token_tag)

                    log.info(f"Verification email sent to {email} for user {username}")

                except EmailVerificationError as e:
                    log.warning(f"Failed to send verification email to {email}: {e}")
                    verification_message = " Note: Verification email could not be sent due to email server issues. Your account was created but requires administrator approval. Please contact an administrator for manual verification."
                    # Do NOT mark user as verified since email failed - leave for admin approval

            else:
                # Email verification not available - do NOT auto-verify for domain management
                # Leave user unverified so admin can manually approve through domain management interface
                
                # Provide detailed logging about why verification was skipped
                if email_verification_status:
                    if not email_verification_status.get("smtp_configured", False):
                        log.info(
                            f"Email verification skipped for {username}: SMTP not configured. User left unverified for admin approval."
                        )
                        verification_message = " Your account has been created but requires administrator approval since email verification is not configured. Please wait for an administrator to verify your account."
                    elif not email_verification_status.get(
                        "verification_enabled", False
                    ):
                        log.info(
                            f"Email verification skipped for {username}: verification disabled in config. User left unverified for admin approval."
                        )
                        verification_message = " Your account has been created but requires administrator approval since email verification is disabled. Please wait for an administrator to verify your account."
                    elif email_verification_status.get("errors"):
                        log.info(
                            f"Email verification skipped for {username}: configuration errors: {email_verification_status['errors']}. User left unverified for admin approval."
                        )
                        verification_message = " Your account has been created but requires administrator approval due to email configuration issues. Please wait for an administrator to verify your account."
                    else:
                        log.info(
                            f"Email verification skipped for {username}: unknown reason. User left unverified for admin approval."
                        )
                        verification_message = " Your account has been created but requires administrator approval. Please wait for an administrator to verify your account."
                else:
                    log.warning(
                        f"Email verification skipped for {username}: failed to get verification status. User left unverified for admin approval."
                    )
                    verification_message = " Your account has been created but requires administrator approval. Please wait for an administrator to verify your account."

            return {
                "status": "success",
                "message": f"Account created successfully{verification_message}",
                "user_id": bq_user.resource_uniq,
                "username": username,
                "email_verification_required": email_verification_available,
            }

        except Exception as e:
            # Let TurboGears transaction manager handle rollback
            log.error(f"Registration failed for {kw.get('email', 'unknown')}: {str(e)}")
            import traceback

            log.error(f"Full traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "message": "Registration failed due to server error. Please try again.",
            }

    @expose("json")
    def check_config(self, **kw):
        """Check email verification configuration status (admin endpoint)"""
        try:
            config_status = self._safe_email_call(
                "validate_configuration",
            )
            smtp_test = None

            if config_status["smtp_configured"]:
                smtp_test = self._safe_email_call(
                    "test_smtp_connection",
                )

            return {
                "status": "success",
                "email_verification": config_status,
                "smtp_test": smtp_test,
            }

        except Exception as e:
            log.error(f"Error checking email verification config: {e}")
            return {"status": "error", "message": f"Failed to check configuration: {e}"}

    @expose("json")
    def confirm(self, **kw):
        """Email confirmation endpoint - placeholder for future implementation"""
        code = kw.get("code")
        return {
            "status": "success",
            "message": "Email confirmation not yet implemented.",
        }

    @expose("json")
    def check_availability(self, **kw):
        """Check if username or email is available"""
        username = kw.get("username", "").strip()
        email = kw.get("email", "").strip()

        result = {"username_available": True, "email_available": True}

        if username:
            existing_user = User.by_user_name(username)
            result["username_available"] = existing_user is None

        if email:
            existing_user = User.by_email_address(email)
            result["email_available"] = existing_user is None

        return result

    @expose()
    def register_redirect(self, **kw):
        """    
        Registration endpoint that redirects to login with flash message
        This provides a fallback for non-AJAX registration
        """
        try:
            # Extract required fields
            email = kw.get("email", "").strip()
            username = kw.get("username", "").strip()
            fullname = kw.get("fullname", "").strip()
            password = kw.get("password", "").strip()
            research_area = kw.get("research_area", "").strip()
            institution_affiliation = kw.get("institution_affiliation", "").strip()
            funding_agency = kw.get("funding_agency", "").strip()

            # Validation
            if not email or not username or not fullname or not password:
                flash(
                    "Missing required fields: email, username, fullname, and password are required",
                    "error",
                )
                redirect("/registration/")

            if not research_area or not institution_affiliation:
                flash("Research area and institution affiliation are required", "error")
                redirect("/registration/")

            if len(password) < 6:
                flash("Password must be at least 6 characters long", "error")
                redirect("/registration/")

            # Check for existing users
            existing_user_email = User.by_email_address(email)
            if existing_user_email:
                flash("A user with this email address already exists", "error")
                redirect("/registration/")

            existing_user_name = User.by_user_name(username)
            if existing_user_name:
                flash("This username is already taken", "error")
                redirect("/registration/")

            # Check if domain is authorized for registration
            if not self._is_domain_authorized(email):
                domain = email.split('@')[1] if '@' in email else 'unknown'
                log.info(f"Registration attempt from unauthorized domain: {domain}")
                flash(f"Registration not allowed for domain '{domain}'. Please contact an administrator to authorize your domain for registration.", "error")
                redirect("/registration/")

            # Validate research area options
            valid_research_areas = [
                "Bioinformatics",
                "Cell Biology",
                "Developmental Biology",
                "Ecology",
                "Genetics",
                "Immunology",
                "Materials Science",
                "Microbiology",
                "Molecular Biology",
                "Neuroscience",
                "Pharmacology",
                "Plant Biology",
                "Structural Biology",
                "Other",
            ]
            if research_area and research_area not in valid_research_areas:
                flash(
                    f'Invalid research area. Must be one of: {", ".join(valid_research_areas)}',
                    "error",
                )
                redirect("/registration/")

            # Create user using the same logic as the JSON endpoint
            log.info(f"Creating new user: {username} ({email})")

            # Create the core TurboGears User first
            tg_user = User(
                user_name=username,
                email_address=email,
                display_name=fullname,
                password=password,
            )
            DBSession.add(tg_user)
            DBSession.flush()  # Get the TG user ID, this also triggers bquser_callback

            # The bquser_callback automatically creates a BQUser, so let's find it
            from bq.data_service.model import BQUser

            bq_user = DBSession.query(BQUser).filter_by(resource_name=username).first()
            if not bq_user:
                # Fallback: create BQUser manually if callback didn't work
                bq_user = BQUser(tg_user=tg_user, create_tg=False, create_store=True)
                DBSession.add(bq_user)
                DBSession.flush()
                bq_user.owner_id = bq_user.id

            # Add custom tags for the extended profile information
            from bq.data_service.model.tag_model import Tag

            # Create all tags
            fullname_tag = Tag(parent=bq_user)
            fullname_tag.name = "fullname"
            fullname_tag.value = fullname
            DBSession.add(fullname_tag)

            username_tag = Tag(parent=bq_user)
            username_tag.name = "username"
            username_tag.value = username
            DBSession.add(username_tag)

            research_area_tag = Tag(parent=bq_user)
            research_area_tag.name = "research_area"
            research_area_tag.value = research_area
            DBSession.add(research_area_tag)

            institution_tag = Tag(parent=bq_user)
            institution_tag.name = "institution_affiliation"
            institution_tag.value = institution_affiliation
            DBSession.add(institution_tag)

            # Add funding agency tag (if provided)
            if funding_agency:
                funding_tag = Tag(parent=bq_user)
                funding_tag.name = "funding_agency"
                funding_tag.value = funding_agency
                DBSession.add(funding_tag)

            log.info(
                f"Successfully created user: {username} with ID: {bq_user.resource_uniq}"
            )

            # Handle email verification
            email_verification_status = self._safe_email_call("validate_configuration")
            email_verification_available = (
                email_verification_status.get("available", False)
                if email_verification_status
                else False
            )

            if email_verification_available:
                log.info(
                    f"Email verification is available - sending verification email to {email}"
                )

                # Generate verification token
                verification_token = self._safe_email_call(
                    "generate_verification_token", email, username
                )
                if not verification_token:
                    log.error(f"Failed to generate verification token for {email}")
                    flash(
                        f"Registration completed but email verification failed. You can request a new verification email.",
                        "warning",
                    )
                    self._safe_email_call("mark_user_as_verified", bq_user)
                    redirect("/client_service/")

                # Get base URL for verification link
                base_url = request.host_url.rstrip("/")

                # Send verification email
                send_result = self._safe_email_call(
                    "send_verification_email",
                    email,
                    username,
                    fullname,
                    verification_token,
                    base_url,
                )
                if send_result and send_result.get("success"):
                    log.info(f"Verification email sent successfully to {email}")

                    # Store verification token as a tag for later verification
                    token_tag = Tag(parent=bq_user)
                    token_tag.name = "email_verification_token"
                    token_tag.value = verification_token
                    token_tag.owner = bq_user
                    DBSession.add(token_tag)

                    flash(
                        f"Account created successfully for {fullname}! Please check your email ({email}) for a verification link before signing in.",
                        "success",
                    )
                else:
                    log.error(
                        f"Failed to send verification email to {email}: {send_result}"
                    )
                    # Mark user as verified if email sending fails
                    self._safe_email_call("mark_user_as_verified", bq_user)
                    flash(
                        f"Account created successfully for {fullname}! Email verification failed, but you can sign in immediately.",
                        "warning",
                    )
            else:
                log.info(
                    f"Email verification not available - user left unverified for admin approval"
                )
                # Do NOT mark user as verified when email verification is not available
                # User must be manually verified by admin
                flash(
                    f"Account created successfully for {fullname}! Your account requires administrator approval before you can sign in. Please wait for verification.",
                    "info",
                )

            redirect("/client_service/")

        except Exception as e:
            # Check if this is a redirect exception (which is normal)
            import tg.exceptions

            if isinstance(e, (tg.exceptions.HTTPFound, tg.exceptions.HTTPRedirection)):
                # This is a redirect, let it propagate normally
                raise
            else:
                # This is a real error - let TurboGears transaction manager handle rollback
                log.error(
                    f"Registration failed for {kw.get('email', 'unknown')}: {str(e)}"
                )
                import traceback

                log.error(f"Full traceback: {traceback.format_exc()}")
                flash(
                    "Registration failed due to server error. Please try again.",
                    "error",
                )
                redirect("/registration/")

    @expose()
    def register_with_redirect(self, **kw):
        """
        Alternative registration endpoint that uses TurboGears flash messages and redirect
        This is used as a fallback when JavaScript is disabled
        """
        try:
            # Extract required fields for validation (same as JSON endpoint)
            email = kw.get("email", "").strip()
            username = kw.get("username", "").strip()
            fullname = kw.get("fullname", "").strip()
            password = kw.get("password", "").strip()
            research_area = kw.get("research_area", "").strip()
            institution_affiliation = kw.get("institution_affiliation", "").strip()
            funding_agency = kw.get("funding_agency", "").strip()

            # Validation (same logic as JSON endpoint but with redirects)
            if not email or not username or not fullname or not password:
                flash(
                    "Missing required fields: email, username, fullname, and password are required",
                    "error",
                )
                redirect("/registration/")

            if not research_area or not institution_affiliation:
                flash("Research area and institution affiliation are required", "error")
                redirect("/registration/")

            if len(password) < 6:
                flash("Password must be at least 6 characters long", "error")
                redirect("/registration/")

            # Check for existing users
            existing_user_email = User.by_email_address(email)
            if existing_user_email:
                flash("A user with this email address already exists", "error")
                redirect("/registration/")

            existing_user_name = User.by_user_name(username)
            if existing_user_name:
                flash("This username is already taken", "error")
                redirect("/registration/")

            # Check if domain is authorized for registration
            if not self._is_domain_authorized(email):
                domain = email.split('@')[1] if '@' in email else 'unknown'
                log.info(f"Registration attempt from unauthorized domain: {domain}")
                flash(f"Registration not allowed for domain '{domain}'. Please contact an administrator to authorize your domain for registration.", "error")
                redirect("/registration/")

            # Validate research area options
            valid_research_areas = [
                "Bioinformatics",
                "Cell Biology",
                "Developmental Biology",
                "Ecology",
                "Genetics",
                "Immunology",
                "Materials Science",
                "Microbiology",
                "Molecular Biology",
                "Neuroscience",
                "Pharmacology",
                "Plant Biology",
                "Structural Biology",
                "Other",
            ]
            if research_area and research_area not in valid_research_areas:
                flash(
                    f'Invalid research area. Must be one of: {", ".join(valid_research_areas)}',
                    "error",
                )
                redirect("/registration/")

            # Create user using the same logic as the JSON endpoint
            log.info(f"Creating new user: {username} ({email})")

            # Create the core TurboGears User first
            tg_user = User(
                user_name=username,
                email_address=email,
                display_name=fullname,
                password=password,
            )
            DBSession.add(tg_user)
            DBSession.flush()  # Get the TG user ID, this also triggers bquser_callback

            # The bquser_callback automatically creates a BQUser, so let's find it
            from bq.data_service.model import BQUser

            bq_user = DBSession.query(BQUser).filter_by(resource_name=username).first()
            if not bq_user:
                # Fallback: create BQUser manually if callback didn't work
                bq_user = BQUser(tg_user=tg_user, create_tg=False, create_store=True)
                DBSession.add(bq_user)
                DBSession.flush()
                bq_user.owner_id = bq_user.id

            # Add custom tags for the extended profile information
            from bq.data_service.model.tag_model import Tag

            # Create all tags
            fullname_tag = Tag(parent=bq_user)
            fullname_tag.name = "fullname"
            fullname_tag.value = fullname
            DBSession.add(fullname_tag)

            username_tag = Tag(parent=bq_user)
            username_tag.name = "username"
            username_tag.value = username
            DBSession.add(username_tag)

            research_area_tag = Tag(parent=bq_user)
            research_area_tag.name = "research_area"
            research_area_tag.value = research_area
            DBSession.add(research_area_tag)

            institution_tag = Tag(parent=bq_user)
            institution_tag.name = "institution_affiliation"
            institution_tag.value = institution_affiliation
            DBSession.add(institution_tag)

            # Add funding agency tag (if provided)
            if funding_agency:
                funding_tag = Tag(parent=bq_user)
                funding_tag.name = "funding_agency"
                funding_tag.value = funding_agency
                DBSession.add(funding_tag)

            log.info(
                f"Successfully created user: {username} with ID: {bq_user.resource_uniq}"
            )

            # Handle email verification
            email_verification_status = self._safe_email_call("validate_configuration")
            email_verification_available = (
                email_verification_status.get("available", False)
                if email_verification_status
                else False
            )

            if email_verification_available:
                log.info(
                    f"Email verification is available - sending verification email to {email}"
                )

                # Generate verification token
                verification_token = self._safe_email_call(
                    "generate_verification_token", email, username
                )
                if not verification_token:
                    log.error(f"Failed to generate verification token for {email}")
                    flash(
                        f"Registration completed but email verification failed. You can request a new verification email.",
                        "warning",
                    )
                    self._safe_email_call("mark_user_as_verified", bq_user)
                    redirect("/client_service/")

                # Get base URL for verification link
                base_url = request.host_url.rstrip("/")

                # Send verification email
                send_result = self._safe_email_call(
                    "send_verification_email",
                    email,
                    username,
                    fullname,
                    verification_token,
                    base_url,
                )
                if send_result and send_result.get("success"):
                    log.info(f"Verification email sent successfully to {email}")

                    # Store verification token as a tag for later verification
                    token_tag = Tag(parent=bq_user)
                    token_tag.name = "email_verification_token"
                    token_tag.value = verification_token
                    token_tag.owner = bq_user
                    DBSession.add(token_tag)

                    flash(
                        f"Account created successfully! Please check your email ({email}) for a verification link before signing in.",
                        "success",
                    )
                else:
                    log.error(
                        f"Failed to send verification email to {email}: {send_result}"
                    )
                    # Do NOT mark user as verified if email sending fails - require admin approval
                    flash(
                        f"Account created successfully! Email verification failed - your account requires administrator approval before you can sign in.",
                        "info",
                    )
            else:
                log.info(
                    f"Email verification not available - user left unverified for admin approval"
                )
                # Do NOT mark user as verified when email verification is not available
                flash(
                    f"Account created successfully! Your account requires administrator approval before you can sign in.",
                    "info",
                )

            redirect("/client_service/")

        except HTTPFound:
            # This is a normal TurboGears redirect - let it propagate
            raise
        except Exception as e:
            log.error(f"Registration with redirect failed: {str(e)}")
            import traceback

            log.error(f"Full traceback: {traceback.format_exc()}")
            flash("Registration failed due to server error. Please try again.", "error")
            redirect("/registration/")

    @expose("bq.registration.templates.redirect_with_flash")
    def verify_email(self, **kw):
        """Email verification endpoint"""
        token = kw.get("token", "").strip()
        email = kw.get("email", "").strip()

        if not token or not email:
            flash(
                "Invalid verification link. Please check your email for the correct link.",
                "error",
            )
            return dict(redirect_url="/registration/")

        try:
            # Find user by email
            from bq.data_service.model import BQUser

            bq_user = None

            log.info(f"Looking up user by email: {email}")

            # Search for user by email (stored in the value field)
            users = DBSession.query(BQUser).filter(BQUser.resource_value == email).all()
            if not users:
                log.error(f"No user found with email: {email}")
                flash("User not found. Please register again.", "error")
                redirect("/registration/")

            if len(users) > 1:
                log.warning(
                    f"Multiple users found with email {email}: {[u.resource_name for u in users]}"
                )

            bq_user = users[0]
            username = bq_user.resource_name

            log.info(
                f"Found user: {username} (ID: {bq_user.resource_uniq}) for email: {email}"
            )

            # Check if user is already verified
            if self._safe_email_call("is_user_verified", bq_user):
                flash(
                    "Your email is already verified! You can sign in normally.",
                    "success",
                )
                return dict(redirect_url="/client_service/")

            # Get stored verification token
            from bq.data_service.model.tag_model import Tag

            log.info(
                f"Looking for stored verification token for user {username} (ID: {bq_user.id}, resource_uniq: {bq_user.resource_uniq}) ({email})"
            )

            # First try simple lookup without filtering
            all_tokens = (
                DBSession.query(Tag)
                .filter(
                    Tag.parent == bq_user,
                    Tag.resource_name == "email_verification_token",
                )
                .all()
            )

            log.info(
                f"All tokens found for user (using resource_name): {[(t.id, t.name, t.value, t.resource_name, t.resource_value) for t in all_tokens]}"
            )

            # Look for the most recent valid token
            token_tag = None
            if all_tokens:
                # Find the most recent valid token
                valid_tokens = [
                    t for t in all_tokens if t.value and t.value.strip() != ""
                ]
                if valid_tokens:
                    token_tag = valid_tokens[-1]  # Get the most recent valid one
                    log.info(
                        f"Using valid token: ID={token_tag.id}, value='{token_tag.value}'"
                    )
                else:
                    log.error(
                        f"No valid tokens found among {len(all_tokens)} total tokens"
                    )
            else:
                log.error(f"No email_verification_token tags found for user")

            # Debug: Also try finding by resource_parent_id directly
            token_tag_by_id = (
                DBSession.query(Tag)
                .filter(
                    Tag.resource_parent_id == bq_user.id,
                    Tag.resource_name == "email_verification_token",
                )
                .order_by(Tag.id.desc())
                .first()
            )

            log.info(f"Token found by parent object: {token_tag is not None}")
            log.info(
                f"Token found by parent_id (using bq_user.id={bq_user.id}): {token_tag_by_id is not None}"
            )

            if token_tag:
                log.info(
                    f"Token by parent - value: {token_tag.value}, parent_id: {token_tag.resource_parent_id}"
                )
            if token_tag_by_id:
                log.info(
                    f"Token by parent_id - value: {token_tag_by_id.value}, parent_id: {token_tag_by_id.resource_parent_id}"
                )

            if not token_tag and not token_tag_by_id:
                log.error(
                    f"No verification token found for user {username} (ID: {bq_user.id}, resource_uniq: {bq_user.resource_uniq}) ({email})"
                )
                # Debug: Check all tags for this user
                all_user_tags = DBSession.query(Tag).filter(Tag.parent == bq_user).all()
                all_user_tags_by_id = (
                    DBSession.query(Tag)
                    .filter(Tag.resource_parent_id == bq_user.id)
                    .all()
                )
                log.info(
                    f"All tags for user {username} (by parent): {[(t.name, t.value) for t in all_user_tags]}"
                )
                log.info(
                    f"All tags for user {username} (by resource_parent_id={bq_user.id}): {[(t.name, t.value) for t in all_user_tags_by_id]}"
                )
                flash(
                    "Verification token not found. Please request a new verification email.",
                    "error",
                )
                # redirect("/registration/resend_verification")
                return dict(redirect_url="/registration/resend_verification")

            # Use whichever method found the token
            actual_token_tag = token_tag or token_tag_by_id

            log.info(
                f"Found stored token for user {username}: {actual_token_tag.value}"
            )
            log.info(f"URL token: {token}")
            log.info(f"Tokens match: {actual_token_tag.value == token}")

            # Verify the token
            if not self._safe_email_call("verify_token", token, email, username):
                flash(
                    "Invalid or expired verification link. Please request a new verification email.",
                    "error",
                )
                # redirect("/registration/resend_verification")
                return dict(redirect_url="/registration/resend_verification")

            # Mark user as verified
            if self._safe_email_call("mark_user_as_verified", bq_user):
                # Remove the verification token
                DBSession.delete(actual_token_tag)
                DBSession.flush()

                # Get user display name from tags or use username as fallback
                display_name_tag = bq_user.findtag("display_name")
                display_name = display_name_tag.value if display_name_tag else username

                flash(
                    f"Email verified successfully! Welcome to Bisque, {display_name}. You can now sign in.",
                    "success",
                )
                # redirect("/client_service/")
                return dict(redirect_url="/client_service/")
            else:
                flash(
                    "Verification failed due to a server error. Please try again.",
                    "error",
                )
                # redirect("/registration/")
                return dict(redirect_url="/registration/")

        except Exception as e:
            # Check if this is a redirect exception (which is normal)
            import tg.exceptions

            if isinstance(e, (tg.exceptions.HTTPFound, tg.exceptions.HTTPRedirection)):
                # This is a redirect, let it propagate normally
                raise
            else:
                # This is a real error
                log.error(f"Email verification failed: {e}")
                flash(
                    "Verification failed due to a server error. Please try again.",
                    "error",
                )
                # redirect("/registration/")
                return dict(redirect_url="/registration/")

    @expose("bq.registration.templates.resend_verification")
    def resend_verification(self, **kw):
        """Resend verification email page"""
        if not self._safe_email_call(
            "is_available",
        ):
            flash("Email verification is not available.", "error")
            redirect("/registration/")

        return {"msg": "Resend verification email"}

    @expose("json")
    @expose("bq.registration.templates.resend_verification")
    def send_verification(self, **kw):
        """Send verification email endpoint"""
        if not self._safe_email_call(
            "is_available",
        ):
            error_msg = "Email verification is not available"
            return self._handle_verification_response("error", error_msg, **kw)

        email = kw.get("email", "").strip()
        if not email:
            error_msg = "Email address is required"
            return self._handle_verification_response("error", error_msg, **kw)

        try:
            # Find user by email
            from bq.data_service.model import BQUser

            users = DBSession.query(BQUser).filter(BQUser.resource_value == email).all()
            if not users:
                error_msg = "User not found with this email address"
                return self._handle_verification_response("error", error_msg, **kw)

            bq_user = users[0]
            username = bq_user.resource_name

            # Check if already verified
            if self._safe_email_call("is_user_verified", bq_user):
                success_msg = (
                    "Your email is already verified! You can sign in normally."
                )
                return self._handle_verification_response("success", success_msg, **kw)

            # Get user's full name
            from bq.data_service.model.tag_model import Tag

            fullname_tag = (
                DBSession.query(Tag)
                .filter(Tag.parent == bq_user, Tag.name == "fullname")
                .first()
            )
            fullname = fullname_tag.value if fullname_tag else username

            # Generate new verification token
            verification_token = self._safe_email_call(
                "generate_verification_token", email, username
            )
            if not verification_token:
                log.error(f"Failed to generate verification token for {email}")
                error_msg = "Failed to generate verification token. Please try again."
                return self._handle_verification_response("error", error_msg, **kw)

            log.info(f"Generated verification token for {email}: {verification_token}")

            # Update verification token
            token_tag = (
                DBSession.query(Tag)
                .filter(Tag.parent == bq_user, Tag.name == "email_verification_token")
                .first()
            )

            if token_tag:
                log.info(f"Updating existing token for {email}")
                token_tag.value = verification_token
            else:
                log.info(f"Creating new token tag for {email}")
                token_tag = Tag(parent=bq_user)
                token_tag.name = "email_verification_token"
                token_tag.value = verification_token
                token_tag.owner = bq_user
                DBSession.add(token_tag)

            # Send verification email
            base_url = request.host_url.rstrip("/")
            send_result = self._safe_email_call(
                "send_verification_email",
                email,
                username,
                fullname,
                verification_token,
                base_url,
            )

            if not send_result or not send_result.get("success"):
                error_msg = (
                    send_result.get("error", "Unknown error")
                    if send_result
                    else "Email service unavailable"
                )
                log.error(f"Failed to send verification email to {email}: {error_msg}")
                error_msg = f"Failed to send verification email: {error_msg}"
                return self._handle_verification_response("error", error_msg, **kw)

            DBSession.flush()
            log.info(
                f"Token stored and flushed to database for {email}: {verification_token}"
            )
            success_msg = (
                "Verification email sent successfully! Please check your email."
            )
            return self._handle_verification_response("success", success_msg, **kw)

        except EmailVerificationError as e:
            log.error(f"Failed to resend verification email: {e}")
            error_msg = f"Failed to send verification email: {e}"
            return self._handle_verification_response("error", error_msg, **kw)
        except Exception as e:
            # Check if this is a redirect exception (which is normal)
            import tg.exceptions

            if isinstance(e, (tg.exceptions.HTTPFound, tg.exceptions.HTTPRedirection)):
                # This is a redirect, let it propagate normally
                raise
            else:
                # This is a real error
                log.error(f"Resend verification failed: {e}")
                error_msg = "Failed to send verification email due to server error"
                return self._handle_verification_response("error", error_msg, **kw)

    def _handle_verification_response(self, status, message, **kw):
        """Handle response for verification requests - JSON for AJAX, redirect for browser"""
        from tg import request

        # Check if this is an AJAX request
        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest" or "application/json" in request.headers.get(
            "Accept", ""
        ):
            # Return JSON for AJAX requests
            return {"status": status, "message": message}
        else:
            # Handle browser requests with flash messages and redirects
            if status == "success":
                flash(message, "success")
                redirect("/registration/resend_verification?sent=1")
            else:
                flash(message, "error")
                return {
                    "msg": "Resend verification email",
                    "email": kw.get("email", ""),
                }

    @expose("bq.registration.templates.verify_email")
    def verify(self, token=None, **kw):
        """Email verification endpoint with token in URL path: /registration/verify/{token}"""
        try:
            if not token:
                flash("Invalid verification link. Missing verification token.", "error")
                redirect("/registration/")

            token = token.strip()

            # Find the user by searching for the verification token
            from bq.data_service.model import BQUser
            from bq.data_service.model.tag_model import Tag

            log.info(f"Looking up verification token: {token}")

            # Find user by verification token
            token_tag = (
                DBSession.query(Tag)
                .filter(Tag.name == "email_verification_token", Tag.value == token)
                .first()
            )

            if not token_tag:
                log.error(f"Verification token not found in database: {token}")
                # Debug: Check if there are any verification tokens at all
                all_verification_tokens = (
                    DBSession.query(Tag)
                    .filter(Tag.name == "email_verification_token")
                    .all()
                )
                log.info(
                    f"All verification tokens in database: {[t.value for t in all_verification_tokens]}"
                )
                flash(
                    "Invalid or expired verification link. Please request a new verification email.",
                    "error",
                )
                redirect("/registration/resend_verification")

            log.info(
                f"Found verification token for user: {token_tag.parent.resource_name if token_tag.parent else 'NO_PARENT'}"
            )

            bq_user = token_tag.parent
            if not bq_user:
                log.error(f"Token found but no parent user: {token}")
                flash("User not found. Please register again.", "error")
                redirect("/registration/")

            username = bq_user.resource_name
            email = bq_user.resource_value

            # Check if user is already verified
            if self._safe_email_call("is_user_verified", bq_user):
                flash(
                    "Your email is already verified! You can sign in normally.",
                    "success",
                )
                redirect("/client_service/")

            # Verify the token
            if not self._safe_email_call("verify_token", token, email, username):
                flash(
                    "Invalid or expired verification link. Please request a new verification email.",
                    "error",
                )
                redirect("/registration/resend_verification")

            # Mark user as verified
            verify_result = self._safe_email_call("mark_user_as_verified", bq_user)
            if verify_result and verify_result.get("success"):
                # Remove the verification token
                DBSession.delete(token_tag)
                DBSession.flush()

                display_name = bq_user.get("display_name", username)
                flash(
                    f"Email verified successfully! Welcome to Bisque, {display_name}. You can now sign in.",
                    "success",
                )
                redirect("/client_service/")
            else:
                error_msg = (
                    verify_result.get("error", "Unknown error")
                    if verify_result
                    else "Unknown error"
                )
                flash(f"Verification failed: {error_msg}. Please try again.", "error")
                redirect("/registration/")

        except Exception as e:
            # Check if this is a redirect exception (which is normal)
            import tg.exceptions

            if isinstance(e, (tg.exceptions.HTTPFound, tg.exceptions.HTTPRedirection)):
                # This is a redirect, let it propagate normally
                raise
            else:
                # This is a real error
                log.error(f"Email verification failed: {e}")
                import traceback

                log.error(f"Full traceback: {traceback.format_exc()}")
                flash(
                    "Verification failed due to a server error. Please try again.",
                    "error",
                )
                redirect("/registration/")

    # Password Reset Methods
    @expose("bq.registration.templates.lost_password")
    def lost_password(self, **kw):
        """Lost/forgot password form page"""
        # Get email verification configuration status for display
        email_verification_status = self._safe_email_call("validate_configuration")
        email_verification_enabled = (
            email_verification_status.get("available", False)
            if email_verification_status
            else False
        )

        return {
            "msg": "Reset your password",
            "email_verification_enabled": email_verification_enabled,
            "email_verification_status": email_verification_status,
        }

    @expose("json")
    @expose("bq.registration.templates.lost_password")
    def request_password_reset(self, **kw):
        """Process password reset request"""
        email = kw.get("email", "").strip()
        if not email:
            error_msg = "Email address is required"
            return self._handle_reset_response("error", error_msg, **kw)

        try:
            # Find user by email
            from bq.data_service.model import BQUser

            users = DBSession.query(BQUser).filter(BQUser.resource_value == email).all()
            if not users:
                # Don't reveal if email exists for security - always show success
                success_msg = "If an account with this email exists, a password reset email has been sent."
                return self._handle_reset_response("success", success_msg, **kw)

            bq_user = users[0]
            username = bq_user.resource_name

            # Get user's full name
            from bq.data_service.model.tag_model import Tag

            fullname_tag = (
                DBSession.query(Tag)
                .filter(Tag.parent == bq_user, Tag.name == "fullname")
                .first()
            )
            fullname = fullname_tag.value if fullname_tag else username

            # Generate password reset token
            reset_token = self._safe_email_call(
                "generate_password_reset_token", email, username
            )
            if not reset_token:
                log.error(f"Failed to generate password reset token for {email}")
                # Show success message even if token generation fails (for security)
                success_msg = "If an account with this email exists, a password reset email has been sent."
                return self._handle_reset_response("success", success_msg, **kw)

            log.info(f"Generated password reset token for {email}: {reset_token}")

            # Store reset token as a tag for later verification
            token_tag = (
                DBSession.query(Tag)
                .filter(Tag.parent == bq_user, Tag.name == "password_reset_token")
                .first()
            )

            if token_tag:
                log.info(f"Updating existing password reset token for {email}")
                token_tag.value = reset_token
            else:
                log.info(f"Creating new password reset token tag for {email}")
                token_tag = Tag(parent=bq_user)
                token_tag.name = "password_reset_token"
                token_tag.value = reset_token
                token_tag.owner = bq_user
                DBSession.add(token_tag)

            # Send password reset email
            base_url = request.host_url.rstrip("/")
            send_result = self._safe_email_call(
                "send_password_reset_email",
                email,
                username,
                fullname,
                reset_token,
                base_url,
            )

            if not send_result or not send_result.get("success"):
                log.error(f"Failed to send password reset email to {email}")
                # Still show success for security, but log the error
                success_msg = "If an account with this email exists, a password reset email has been sent."
                return self._handle_reset_response("success", success_msg, **kw)

            DBSession.flush()
            log.info(f"Password reset email sent successfully to {email}")
            success_msg = "If an account with this email exists, a password reset email has been sent."
            return self._handle_reset_response("success", success_msg, **kw)

        except Exception as e:
            # Check if this is a redirect exception (which is normal)
            if isinstance(e, HTTPFound):
                # This is a redirect, let it propagate normally
                raise
            else:
                # This is a real error
                log.error(f"Password reset request failed for {email}: {e}")
                # Show success message even for errors (for security)
                success_msg = "If an account with this email exists, a password reset email has been sent."
                return self._handle_reset_response("success", success_msg, **kw)

    @expose("bq.registration.templates.reset_password")
    def reset_password(self, **kw):
        """Password reset form page"""
        token = kw.get("token", "").strip()
        email = kw.get("email", "").strip()

        # Get email verification configuration status for display
        email_verification_status = self._safe_email_call("validate_configuration")
        email_verification_enabled = (
            email_verification_status.get("available", False)
            if email_verification_status
            else False
        )

        if not token or not email:
            flash(
                "Invalid password reset link. Please request a new password reset.",
                "error",
            )
            redirect("/registration/lost_password")

        return {
            "msg": "Set your new password",
            "token": token,
            "email": email,
            "email_verification_enabled": email_verification_enabled,
            "email_verification_status": email_verification_status,
        }

    @expose("json")
    @expose("bq.registration.templates.reset_password")
    def process_password_reset(self, **kw):
        """Process password reset form submission"""
        token = kw.get("token", "").strip()
        email = kw.get("email", "").strip()
        new_password = kw.get("new_password", "").strip()
        confirm_password = kw.get("confirm_password", "").strip()

        if not token or not email or not new_password:
            error_msg = "Missing required fields"
            return self._handle_reset_form_response(
                "error", error_msg, token, email, **kw
            )

        if new_password != confirm_password:
            error_msg = "Passwords do not match"
            return self._handle_reset_form_response(
                "error", error_msg, token, email, **kw
            )

        if len(new_password) < 6:
            error_msg = "Password must be at least 6 characters long"
            return self._handle_reset_form_response(
                "error", error_msg, token, email, **kw
            )

        try:
            # Find user by email
            from bq.data_service.model import BQUser

            users = DBSession.query(BQUser).filter(BQUser.resource_value == email).all()
            if not users:
                error_msg = "Invalid reset link"
                return self._handle_reset_form_response(
                    "error", error_msg, token, email, **kw
                )

            bq_user = users[0]
            username = bq_user.resource_name

            # Verify reset token
            if not self._safe_email_call(
                "verify_password_reset_token", token, email, username
            ):
                error_msg = "Invalid or expired reset link"
                return self._handle_reset_form_response(
                    "error", error_msg, token, email, **kw
                )

            # Reset password
            reset_result = self._safe_email_call(
                "reset_user_password", bq_user, new_password
            )
            if not reset_result or not reset_result.get("success"):
                error_msg = "Failed to reset password. Please try again."
                return self._handle_reset_form_response(
                    "error", error_msg, token, email, **kw
                )

            # Remove reset token
            from bq.data_service.model.tag_model import Tag

            token_tag = (
                DBSession.query(Tag)
                .filter(Tag.parent == bq_user, Tag.name == "password_reset_token")
                .first()
            )
            if token_tag:
                DBSession.delete(token_tag)

            DBSession.flush()

            log.info(f"Password reset successfully for user {username} ({email})")

            # Handle redirect based on request type
            try:
                flash(
                    "Password reset successfully! You can now sign in with your new password.",
                    "success",
                )
                redirect("/client_service/")
            except (HTTPFound, Exception) as redirect_ex:
                # This is normal - redirect throws an exception
                if hasattr(redirect_ex, "location"):
                    raise redirect_ex
                else:
                    # Fallback if redirect fails
                    return {
                        "status": "success",
                        "message": "Password reset successfully!",
                        "redirect": "/client_service/",
                    }

        except (HTTPFound, Exception) as e:
            # Handle redirect exceptions normally
            if hasattr(e, "location"):
                raise e
            else:
                log.error(f"Password reset processing failed: {e}")
                error_msg = "Password reset failed due to server error"
                # Remove email from kw to avoid duplicate argument
                kw_without_email = {k: v for k, v in kw.items() if k != "email"}
                return self._handle_reset_form_response(
                    "error", error_msg, token, email, **kw_without_email
                )

    def _handle_reset_response(self, status, message, **kw):
        """Handle response for password reset requests - JSON for AJAX, redirect for browser"""
        from tg import request

        # Check if this is an AJAX request
        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest" or "application/json" in request.headers.get(
            "Accept", ""
        ):
            # Return JSON for AJAX requests
            return {"status": status, "message": message}
        else:
            # Handle browser requests with flash messages and redirects
            if status == "success":
                flash(message, "success")
                redirect("/registration/lost_password?sent=1")
            else:
                flash(message, "error")
                return {"msg": "Reset your password", "email": kw.get("email", "")}

    def _handle_reset_form_response(self, status, message, token, email, **kw):
        """Handle response for password reset form - JSON for AJAX, template for browser"""
        from tg import request

        # Check if this is an AJAX request
        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest" or "application/json" in request.headers.get(
            "Accept", ""
        ):
            # Return JSON for AJAX requests
            return {"status": status, "message": message}
        else:
            # Handle browser requests with template display
            if status == "success":
                flash(message, "success")
                redirect("/client_service/")
            else:
                # Get email verification status for template
                email_verification_status = self._safe_email_call(
                    "validate_configuration"
                )
                email_verification_enabled = (
                    email_verification_status.get("available", False)
                    if email_verification_status
                    else False
                )

                return {
                    "msg": "Set your new password",
                    "token": token,
                    "email": email,
                    "error_message": message,
                    "email_verification_enabled": email_verification_enabled,
                    "email_verification_status": email_verification_status,
                }

    # =========================================
    # USER PROFILE EDITING FUNCTIONALITY
    # =========================================

    @expose("bq.registration.templates.edit_user")
    def edit_user(self, **kw):
        """User profile editing form"""
        from tg import request
        from bq.core.model.auth import User
        from bq.data_service.model import BQUser
        from bq.data_service.model.tag_model import Tag

        # Check if user is logged in
        if not request.identity or not request.identity.get("repoze.who.userid"):
            flash("You must be logged in to edit your profile.", "error")
            redirect("/auth_service/login")

        current_user = request.identity.get("user")
        if not current_user:
            flash("User session not found. Please log in again.", "error")
            redirect("/auth_service/login")

        username = current_user.user_name

        try:
            # Get user details from BQUser
            bq_user = (
                DBSession.query(BQUser).filter(BQUser.resource_name == username).first()
            )
            if not bq_user:
                flash("User profile not found.", "error")
                redirect("/client_service/")

            email = bq_user.resource_value

            # Get user tags (additional profile information)
            user_tags = {}
            tags = DBSession.query(Tag).filter(Tag.parent == bq_user).all()
            for tag in tags:
                user_tags[tag.name] = tag.value

            # Get current user information
            user_info = {
                "username": username,
                "email": email,
                "fullname": user_tags.get("fullname", ""),
                "research_area": user_tags.get("research_area", ""),
                "institution_affiliation": user_tags.get("institution_affiliation", ""),
                "funding_agency": user_tags.get("funding_agency", ""),
                "account_created": bq_user.ts if hasattr(bq_user, "ts") else "Unknown",
                "verified": (
                    self._safe_email_call("is_user_verified", bq_user)
                    if self.email_service
                    else False
                ),
            }

            # Get email verification status for display
            email_verification_status = self._safe_email_call("validate_configuration")
            email_verification_enabled = (
                email_verification_status.get("available", False)
                if email_verification_status
                else False
            )

            return {
                "msg": "Edit User Profile",
                "user": user_info,
                "email_verification_enabled": email_verification_enabled,
                "email_verification_status": email_verification_status,
            }

        except Exception as e:
            log.error(f"Error loading user profile for {username}: {e}")
            flash("Error loading user profile. Please try again.", "error")
            redirect("/client_service/")

    @expose("json")
    @expose("bq.registration.templates.edit_user")
    def update_user(self, **kw):
        """Process user profile update"""
        from tg import request
        from bq.core.model.auth import User
        from bq.data_service.model import BQUser
        from bq.data_service.model.tag_model import Tag

        # Check if user is logged in
        if not request.identity or not request.identity.get("repoze.who.userid"):
            error_msg = "You must be logged in to update your profile."
            return self._handle_edit_user_response("error", error_msg, **kw)

        current_user = request.identity.get("user")
        if not current_user:
            error_msg = "User session not found. Please log in again."
            return self._handle_edit_user_response("error", error_msg, **kw)

        username = current_user.user_name

        # Get form data
        fullname = kw.get("fullname", "").strip()
        research_area = kw.get("research_area", "").strip()
        institution_affiliation = kw.get("institution_affiliation", "").strip()
        funding_agency = kw.get("funding_agency", "").strip()
        new_password = kw.get("new_password", "").strip()
        confirm_password = kw.get("confirm_password", "").strip()

        # Validation
        if not fullname:
            error_msg = "Full name is required."
            return self._handle_edit_user_response("error", error_msg, **kw)

        if not research_area:
            error_msg = "Research area is required."
            return self._handle_edit_user_response("error", error_msg, **kw)

        if not institution_affiliation:
            error_msg = "Institution affiliation is required."
            return self._handle_edit_user_response("error", error_msg, **kw)

        # Password validation if changing password
        if new_password:
            if len(new_password) < 6:
                error_msg = "Password must be at least 6 characters long."
                return self._handle_edit_user_response("error", error_msg, **kw)

            if new_password != confirm_password:
                error_msg = "Passwords do not match."
                return self._handle_edit_user_response("error", error_msg, **kw)

        try:
            # Get user records
            bq_user = (
                DBSession.query(BQUser).filter(BQUser.resource_name == username).first()
            )
            if not bq_user:
                error_msg = "User profile not found."
                return self._handle_edit_user_response("error", error_msg, **kw)

            if not bq_user:
                error_msg = "User profile not found."
                return self._handle_edit_user_response("error", error_msg, **kw)

            # Update password if provided (using TurboGears User password property which handles hashing)
            if new_password:
                current_user.password = (
                    new_password  # This uses the TurboGears User _set_password method
                )
                log.info(f"Password updated for user {username}")

            # Update TurboGears User display_name to match the new fullname
            current_user.display_name = fullname
            log.info(
                f"Updated TurboGears User display_name to {fullname} for user {username}"
            )

            # Update user tags - find existing tags or create new ones
            tag_updates = {
                "display_name": fullname,  # This is the standard tag name for full name
                "fullname": fullname,
                "research_area": research_area,
                "institution_affiliation": institution_affiliation,
                "funding_agency": funding_agency,
            }

            for tag_name, tag_value in tag_updates.items():
                # Try to find existing tag using findtag method
                existing_tag = bq_user.findtag(tag_name)

                if existing_tag:
                    # Update existing tag
                    existing_tag.value = tag_value
                    log.info(f"Updated existing tag {tag_name} for user {username}")
                else:
                    # Create new tag
                    new_tag = Tag(parent=bq_user)
                    new_tag.name = tag_name
                    new_tag.value = tag_value
                    new_tag.owner = bq_user
                    DBSession.add(new_tag)
                    log.info(f"Created new tag {tag_name} for user {username}")

            # Transaction will be committed automatically by TurboGears transaction manager

            # Clear server-side cache for this user to ensure fresh data on next request
            try:
                from bq.data_service.controllers.data_service import (
                    invalidate_cache_user,
                )

                if hasattr(invalidate_cache_user, "__call__"):
                    invalidate_cache_user(bq_user.id)
                    log.info(f"Invalidated server cache for user {username}")
            except (ImportError, AttributeError):
                # If cache invalidation is not available, log it but don't fail
                log.info(f"Cache invalidation not available - user data may be cached")

            success_msg = "Profile updated successfully!"

            log.info(f"Profile updated for user {username}")
            return self._handle_edit_user_response("success", success_msg, **kw)

        except HTTPFound:
            # Re-raise redirect exceptions (these are not errors)
            raise
        except Exception as e:
            log.error(f"Error updating profile for {username}: {e}")
            # Don't manually rollback - let TurboGears transaction manager handle it
            error_msg = "Error updating profile. Please try again."
            return self._handle_edit_user_response("error", error_msg, **kw)

    def _handle_edit_user_response(self, status, message, **kw):
        """Handle response for user profile editing"""
        from tg import request

        # Check if this is an AJAX request
        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest" or "application/json" in request.headers.get(
            "Accept", ""
        ):
            return {"status": status, "message": message}
        else:
            flash(message, status)
            if status == "success":
                redirect("/registration/edit_user")
            else:
                # For errors, return the edit form with the error message instead of redirecting
                # This avoids HTTPFound exceptions in error handling contexts
                return self.edit_user(**kw)

    # =========================================
    # DEBUG ENDPOINT (temporary for troubleshooting)
    # =========================================

    # @expose("json")
    # def debug_user_tags(self, username=None):
    #     """Debug endpoint to check user tags - temporary for troubleshooting"""
    #     from tg import request
    #     from bq.data_service.model import BQUser
    #     from bq.data_service.model.tag_model import Tag

    #     if not username:
    #         if not request.identity or not request.identity.get("repoze.who.userid"):
    #             return {"error": "Not logged in and no username provided"}
    #         current_user = request.identity.get("user")
    #         username = current_user.user_name if current_user else None

    #     if not username:
    #         return {"error": "No username available"}

    #     try:
    #         # Find the user
    #         bq_user = (
    #             DBSession.query(BQUser).filter(BQUser.resource_name == username).first()
    #         )
    #         if not bq_user:
    #             return {"error": f"User {username} not found"}

    #         # Get all tags for this user
    #         tags = DBSession.query(Tag).filter(Tag.parent == bq_user).all()

    #         result = {
    #             "user_id": bq_user.id,
    #             "username": bq_user.resource_name,
    #             "email": bq_user.resource_value,
    #             "total_tags": len(tags),
    #             "tags": [],
    #         }

    #         for tag in tags:
    #             result["tags"].append(
    #                 {
    #                     "id": tag.id,
    #                     "name": tag.name,
    #                     "value": tag.value,
    #                     "owner_id": tag.owner_id,
    #                 }
    #             )

    #         # Test findtag method
    #         result["findtag_test"] = {}
    #         test_tags = [
    #             "display_name",
    #             "fullname",
    #             "research_area",
    #             "institution_affiliation",
    #             "funding_agency",
    #         ]
    #         for tag_name in test_tags:
    #             found_tag = bq_user.findtag(tag_name)
    #             if found_tag:
    #                 result["findtag_test"][tag_name] = {
    #                     "found": True,
    #                     "id": found_tag.id,
    #                     "value": found_tag.value,
    #                 }
    #             else:
    #                 result["findtag_test"][tag_name] = {"found": False}

    #         return result

    #     except Exception as e:
    #         log.error(f"Error in debug_user_tags: {e}")
    #         return {"error": str(e)}

    # =========================================
    # END DEBUG SECTION
    # =========================================
