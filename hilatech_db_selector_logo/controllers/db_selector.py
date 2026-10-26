from odoo import http
from odoo.http import request
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.web.controllers.database import Database

from .. import db_logo


class HilatechDatabaseSelector(Database):
    """Show the configured logo on the database selector / manager pages."""

    def _render_template(self, **d):
        page = super()._render_template(**d)
        version = db_logo.logo_version()
        if version is None:
            return page
        original = f'<img src="{db_logo.DEFAULT_LOGO}" class="img-fluid d-block mx-auto"'
        custom = (f'<img src="{db_logo.LOGO_URL}?v={version}" class="img-fluid d-block mx-auto" '
                  'style="max-height: 120px; width: auto; margin-bottom: 1.5rem;"')
        if isinstance(page, bytes):
            return page.replace(original.encode(), custom.encode())
        # plain str: Markup.replace() would HTML-escape the quotes of the arguments
        return str(page).replace(original, custom)


class HilatechDbSelectorLogo(http.Controller):

    @http.route('/hilatech/db_selector/logo', type='http', auth='none', csrf=False)
    def logo(self, **kw):
        raw = db_logo.read_logo()
        if not raw:
            return request.not_found()
        return request.make_response(raw, [
            ('Content-Type', guess_mimetype(raw, default='image/png')),
            ('Cache-Control', 'public, max-age=3600'),
            ('X-Content-Type-Options', 'nosniff'),
            # an SVG opened directly must not be able to run scripts
            ('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'"),
        ])
