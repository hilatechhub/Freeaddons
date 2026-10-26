import base64
import logging
import os

_logger = logging.getLogger(__name__)

DASHBOARD_EXTERNAL_ID = 'hilatech_purchase_dashboard.purchase_dashboard_main'
JSON_FILE = os.path.join(os.path.dirname(__file__), 'data', 'files', 'purchase_dashboard.json')


def _load_dashboard_data(env):
    """Force la mise à jour du spreadsheet_binary_data (contourne le noupdate)."""
    record = env.ref(DASHBOARD_EXTERNAL_ID, raise_if_not_found=False)
    if not record:
        _logger.warning('hilatech_purchase_dashboard: dashboard record not found, skipping')
        return

    if not os.path.exists(JSON_FILE):
        _logger.warning('hilatech_purchase_dashboard: JSON not found at %s', JSON_FILE)
        return

    with open(JSON_FILE, 'rb') as f:
        json_b64 = base64.b64encode(f.read())

    record.sudo().write({
        'spreadsheet_binary_data': json_b64,
        'sample_dashboard_file_path': 'hilatech_purchase_dashboard/data/files/purchase_dashboard.json',
    })
    _logger.info('hilatech_purchase_dashboard: dashboard updated (id=%s)', record.id)


def post_init_hook(env):
    _load_dashboard_data(env)


def post_upgrade_hook(env):
    _load_dashboard_data(env)
