# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import NotFound

from odoo import http
from odoo import tools
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import request
from odoo.tools.translate import _


class WebsiteSubscriptionRequest(http.Controller):

    @http.route(['/struct/<int:struct_id>/subscription'], type='http',
                auth='user', website=True)
    def subscribe_to_structure(self, struct_id=None, **post):
        # Get structure and perform access check
        struct = request.env['res.partner'].sudo().browse(struct_id)
        if not struct:
            raise NotFound
        if not struct.is_plateform_structure:
            raise NotFound
        self.init_form_data(struct_id, qcontext=post)
        self.set_form_defaults(qcontext=post)
        self.normalize_form_data(qcontext=post)
        if post and request.httprequest.method == 'POST':
            self.validate_form(qcontext=post)
            if 'error' not in post:
                values = self.prepare_subscription_request_value(struct,
                                                                 qcontext=post)
                request.env['subscription.request'].sudo().create(values)
                post['success'] = True
        # Populate template value
        qcontext = {
            'struct': struct,
        }
        qcontext.update(post)
        return request.render(
            'investor_wallet_platform_website.subscribe_to_structure',
            qcontext
        )

    def prepare_subscription_request_value(self, struct, qcontext=None):
        if qcontext is None:
            qcontext = request.params
        partner = request.env.user.partner_id
        values = {}
        partner_fields = set(key for key in request.env['res.partner']._fields)
        sub_req_fields = set(
            key for key in request.env['subscription.request'] ._fields
        )
        # TODO: can be improved, because there is to many fields that
        # needs to be excepted.
        excepted_fields = set([
            'type',
            'company_type',
            'company_id',
            'company_name',
            'company_register_number',
            'date',
            'create_date',
            'create_uid',
            'write_date',
            '__last_update',
            'user_id',
        ])
        # Value from user also in subscription request.
        values.update({
            key: partner[key]
            for key in partner_fields & sub_req_fields - excepted_fields
        })
        # Special fields
        values.update({
            'country_id': partner.country_id.id,
            'address': partner.street,
            'zip_code': partner.zip,
            'no_registre': partner.national_register_number,
            'iban': partner.bank_ids[0].acc_number,
            'source': 'website',
            'partner_id': partner.id,
            'share_product_id': qcontext['shareproduct'],
            'ordered_parts': qcontext['number'],
            'structure': struct.id,
        })
        return values

    def validate_form(self, qcontext=None):
        """
        Populate request.parms with errors if the params from the form
        are not correct. If a qcontext is given, this function works on
        this qcontext.
        """
        if qcontext is None:
            qcontext = request.params
        product_obj = request.env['product.template'].sudo().search(
            self.get_share_product_domain(),
        )

        selected_share = qcontext.get('shareproduct', 0)
        if not selected_share:
            qcontext['error'] = _("You must select a financial product.")
            return qcontext
        if qcontext.get('number', 0) < 1:
            qcontext['error'] = _("You must order at least 1 financial"
                                  " product.")
            return qcontext
        shareproduct = product_obj.sudo().browse(selected_share)
        # Check maximum amount
        max_amount = (request.env['res.company']
                      ._company_default_get().subscription_maximum_amount)
        total_amount = qcontext['number'] * shareproduct.list_price
        if max_amount <= total_amount:
            qcontext['error'] = _("You cannot order more than %s."
                                  % max_amount)
            return qcontext
        return qcontext

    def init_form_data(self, struct_id, qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        defalut data needed to render the form.
        """
        if qcontext is None:
            qcontext = request.params
        # Share products
        domain = self.get_share_product_domain()
        if struct_id:
            domain.append(('structure', '=', struct_id))
        share_products = request.env['product.template'].sudo().search(
           domain
        )
        qcontext.update({
            'share_products': share_products,
        })
        return qcontext

    def set_form_defaults(self, qcontext=None, force=False):
        """
        Populate the given qcontext or request.parms if empty with the
        default value for the form.
        """
        if qcontext is None:
            qcontext = request.params
        if 'number' not in qcontext or force:
            qcontext['number'] = 0
        if 'total_amount' not in qcontext or force:
            qcontext['total_amount'] = 0
        cmp = request.env['res.company']._company_default_get()
        # TODO: take shares held by the user into account to adjust the
        # maximum amount
        qcontext['total_amount_max'] = cmp.subscription_maximum_amount
        return qcontext

    def normalize_form_data(self, qcontext=None):
        """
        Normalize data encoded by the user.
        """
        if qcontext is None:
            qcontext = request.params
        # Convert to int when needed
        if 'number' in qcontext:
            qcontext['number'] = int(qcontext['number'])
        if 'shareproduct' in qcontext:
            qcontext['shareproduct'] = int(qcontext['shareproduct'])
        return qcontext

    @staticmethod
    def get_share_product_domain():
        share_product_domain = [
            ('is_share', '=', True),
            ('sale_ok', '=', True),
            ('display_on_website', '=', True)
        ]
        return share_product_domain
