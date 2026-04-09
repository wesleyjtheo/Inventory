"""
Authentication and Security Module
Handles PIN authentication, rate limiting, and session management
"""
import hashlib
import time
import secrets
import os
import smtplib
from email.message import EmailMessage
from functools import wraps
from flask import session, request, jsonify, redirect

# Security: Rate limiting for login attempts
login_attempts = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 300  # 5 minutes in seconds

# Generate a random access token on startup
ACCESS_TOKEN = secrets.token_urlsafe(32)

# One-time code state per IP address
otp_challenges = {}
OTP_EXPIRY_SECONDS = 300  # 5 minutes
DEFAULT_OTP_RECIPIENT = 'wesleyj.theo@gmail.com'


def get_otp_recipient():
    """Return the destination email for login OTP delivery."""
    return os.getenv('OTP_RECIPIENT_EMAIL', DEFAULT_OTP_RECIPIENT).strip()


def send_otp_email(code):
    """Send a 6-digit login code through SMTP."""
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com').strip()
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '').strip()
    smtp_password = os.getenv('SMTP_PASSWORD', '').strip()
    recipient = get_otp_recipient()

    if not smtp_user or not smtp_password:
        raise RuntimeError('SMTP_USER and SMTP_PASSWORD must be configured to send OTP email')

    msg = EmailMessage()
    msg['Subject'] = 'Sora Inventory Login Code'
    msg['From'] = smtp_user
    msg['To'] = recipient
    msg.set_content(
        f"Your Sora Inventory login code is: {code}\n\n"
        f"This code expires in {OTP_EXPIRY_SECONDS // 60} minutes."
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


def issue_login_code(ip):
    """Generate and send a one-time login code for this IP."""
    code = f"{secrets.randbelow(1000000):06d}"
    expires_at = time.time() + OTP_EXPIRY_SECONDS
    otp_challenges[ip] = {
        'code_hash': hashlib.sha256(code.encode()).hexdigest(),
        'expires_at': expires_at,
    }
    send_otp_email(code)


def verify_login_code(ip, code):
    """Verify a submitted one-time code for the IP address."""
    challenge = otp_challenges.get(ip)
    if not challenge:
        return False, 'No active code. Request a new code first.'

    if time.time() > challenge['expires_at']:
        otp_challenges.pop(ip, None)
        return False, 'Code expired. Request a new code.'

    submitted_hash = hashlib.sha256(code.encode()).hexdigest()
    if submitted_hash != challenge['code_hash']:
        return False, 'Invalid code.'

    otp_challenges.pop(ip, None)
    return True, ''

# Security PIN - stored as hash
SECURITY_PIN_HASH = None  # Will be set from environment or generated

def get_security_pin():
    """Get security PIN from environment or generate one"""
    global SECURITY_PIN_HASH
    pin = os.getenv('SECURITY_PIN')
    if pin:
        pin = pin.strip()

    running_on_render = os.getenv('RENDER', '').lower() == 'true'

    if not pin:
        if running_on_render:
            raise RuntimeError(
                "SECURITY_PIN is not set. Configure it in Render Environment variables."
            )
        # Generate a random 6-digit PIN
        pin = str(secrets.randbelow(900000) + 100000)
        print(f"\n⚠️  SECURITY PIN: {pin}")
        print(f"   Set SECURITY_PIN={pin} in your .env file to keep it permanent\n")
    else:
        if not (pin.isdigit() and len(pin) == 6):
            raise ValueError("SECURITY_PIN must be exactly 6 digits")
        print(f"\n🔒 Security PIN loaded from .env file\n")
    
    # Store as hash
    SECURITY_PIN_HASH = hashlib.sha256(pin.encode()).hexdigest()
    return pin

def check_rate_limit(ip):
    """Check if IP is rate limited"""
    if ip in login_attempts:
        attempts, last_attempt = login_attempts[ip]
        if attempts >= MAX_LOGIN_ATTEMPTS:
            if time.time() - last_attempt < LOCKOUT_TIME:
                return False
            else:
                # Reset after lockout period
                login_attempts[ip] = (0, time.time())
    return True

def record_login_attempt(ip, success=False):
    """Record a login attempt"""
    if success:
        login_attempts[ip] = (0, time.time())
    else:
        attempts, _ = login_attempts.get(ip, (0, 0))
        login_attempts[ip] = (attempts + 1, time.time())

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            # Check if this is an API request (JSON) or browser request (HTML)
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'Authentication required', 'redirect': '/login'}), 401
            else:
                # Browser request - redirect to login page
                return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def verify_pin(pin):
    """Verify PIN against stored hash"""
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    return pin_hash == SECURITY_PIN_HASH
