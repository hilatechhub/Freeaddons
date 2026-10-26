"""Logo of the database selector page.

That page is served before any database is chosen, so the picture cannot live in a
database: it is stored as a file in Odoo's data directory and is shared by the whole server.
"""
import base64
import os

from odoo.tools import config
from odoo.tools.mimetypes import guess_mimetype

ALLOWED_MIMETYPES = ('image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml')
DEFAULT_LOGO = '/web/static/img/logo2.png'
LOGO_URL = '/hilatech/db_selector/logo'


def _logo_path():
    return os.path.join(config['data_dir'], 'hilatech_db_selector_logo', 'logo')


def read_logo():
    """Return the stored logo as bytes, or None."""
    try:
        with open(_logo_path(), 'rb') as f:
            return f.read() or None
    except OSError:
        return None


def logo_version():
    try:
        return int(os.path.getmtime(_logo_path()))
    except OSError:
        return None


def is_valid_image(raw):
    return guess_mimetype(raw) in ALLOWED_MIMETYPES


def write_logo(b64_data):
    """Store the logo, or remove it when empty. The caller checks the image type first."""
    path = _logo_path()
    if not b64_data:
        if os.path.exists(path):
            os.remove(path)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64_data))
