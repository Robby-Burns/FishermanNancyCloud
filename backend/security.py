from cryptography.fernet import Fernet
from backend.config import settings
import base64
import hashlib

# Generate a key derived from the secret key
# In production, this should be a separate secure key
def _get_key():
    # Use SHA256 to ensure 32 bytes, then base64 encode for Fernet
    key = hashlib.sha256(settings.secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key)

_fernet = Fernet(_get_key())

def encrypt_value(value: str) -> str:
    """Encrypt a string value"""
    if not value:
        return value
    return _fernet.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    """Decrypt a string value"""
    if not value:
        return value
    try:
        return _fernet.decrypt(value.encode()).decode()
    except Exception:
        # If decryption fails (e.g. data wasn't encrypted), return as is
        return value
