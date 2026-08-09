from . import models
from . import controllers


def post_init_hook(env):
    env['payment.provider']._setup_provider('bkash')


def uninstall_hook(env):
    env['payment.provider']._remove_provider('bkash')