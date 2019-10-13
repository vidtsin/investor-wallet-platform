# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class WebsiteOperationRequest(http.Controller):

    @http.route(
        [
            '/struct/<int:struct_id>/sell',
            '/struct/<int:struct_id>/finprod/<int:finprod_id>/sell'
        ],
        type='http',
        auth='user',
        website=True,
    )
    def sell_finproduct(self, struct_id=None, finprod_id=None, **post):
        # self.reqargs contains request arguments but only if they pass
        # checks.
        self.reqargs = {}
        # Get structure and perform access check
        struct = request.env['res.partner'].sudo().browse(struct_id)
        if not struct:
            raise NotFound
        if not struct.is_plateform_structure:
            raise NotFound
        self.reqargs['struct'] = struct
        # Get findproduct if given
        finprod = (
            request.env['product.template']
            .sudo()
            .browse(finprod_id)
        )
        if finprod:
            if finprod.structure != struct:
                raise NotFound
            self.reqargs['finprod'] = finprod
        else:
            finprod = None
        self.init_form_data(qcontext=post)
        self.set_form_defaults(qcontext=post)
        self.normalize_form_data(qcontext=post)
        if post and request.httprequest.method == 'POST':
            self.validate_form(qcontext=post)
            if 'error' not in post:
                values = self.prepare_operation_request_value(
                    struct,
                    qcontext=post
                )
                request.env['operation.request'].sudo().create(values)
                post['success'] = True
        # Populate template value
        qcontext = {
            'struct': struct,
        }
        qcontext.update(post)
        return request.render(
            'iwp_website.sell_finproduct',
            qcontext
        )

    def prepare_operation_request_value(self, struct, qcontext=None):
        if qcontext is None:
            qcontext = request.params
        partner = request.env.user.partner_id
        values = {}
        values.update({
            'partner_id': partner.id,
            'state': 'draft',
            'operation_type': 'sell_back',
            'share_product_id': qcontext['shareproduct'],
            'quantity': qcontext['number'],
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
        product_obj = request.env['product.template']
        selected_share = qcontext.get('shareproduct', 0)
        shareproduct = product_obj.sudo().browse(selected_share)
        if not shareproduct:
            qcontext['error'] = _("You must select a financial product.")
            return qcontext
        if qcontext.get('number', 0) < 1:
            qcontext['error'] = _("You must order at least 1 financial"
                                  " product.")
            return qcontext
        # Check that share can be sold
        share_line = request.env.user.share_ids.filtered(
            lambda r: r.share_product_id.id == shareproduct.id
        )
        if not share_line:
            qcontext['error'] = _("You cannot sell this share.")
            return qcontext
        # Check maximum quantity of sold share
        max_quantity = sum(share_line.mapped('share_number'))
        if qcontext['number'] >= max_quantity:
            qcontext['error'] = _("You cannot sell more than %s shares."
                                  % max_quantity)
            return qcontext
        return qcontext

    def init_form_data(self, qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        defalut data needed to render the form.
        """
        if qcontext is None:
            qcontext = request.params
        # Share products
        share_lines = request.env.user.share_ids.filtered(
            lambda r: (
                r.share_product_id.structure.id == self.reqargs['struct'].id
            )
        )
        share_products = share_lines.mapped('share_product_id')
        qcontext.update({
            'share_products': share_products,
        })
        cmp = request.env['res.company']._company_default_get()
        # TODO: take shares held by the user into account to adjust the
        # maximum amount
        qcontext['total_amount_max'] = cmp.subscription_maximum_amount
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
        if (
            'shareproduct' not in qcontext or force
        ) and 'finprod' in self.reqargs:
            qcontext['shareproduct'] = self.reqargs['finprod'].id
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
