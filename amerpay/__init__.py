from . import controllers
from . import models
from . import wizard

from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(env):
    setup_provider(env, 'amarpay')
    providers = env['payment.provider'].search([('code', '=', 'amarpay')])
    for provider in providers:
        provider._amarpay_ensure_journal()


def uninstall_hook(env):
    reset_payment_provider(env, 'amarpay')
