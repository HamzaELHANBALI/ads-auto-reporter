"""Email reporting and digest generation."""

from .digest import DigestGenerator
from .email_sender import EmailSender

__all__ = [
    "DigestGenerator",
    "EmailSender"
]




