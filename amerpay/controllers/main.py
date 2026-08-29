import pprint
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class AamarpayController(http.Controller):
    _return_url = '/payment/amarpay/return'

    @http.route(_return_url, type='http', auth='public', methods=['POST'], csrf=False, save_session=False)
    def aamarpay_return_from_checkout(self, **post):
        """Aamarpay থেকে রিটার্ন হওয়া POST ডেটা হ্যান্ডেল করা"""
        _logger.info("Aamarpay Return Data: \n%s", pprint.pformat(post))
        
        # পেমেন্ট ট্রানজ্যাকশন প্রসেস করা
        request.env['payment.transaction'].sudo()._process('amarpay', post)
        
        # ডিফল্ট পেমেন্ট স্ট্যাটাস পেজে রিডাইরেক্ট
        return request.redirect('/payment/status', 303)