# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from .subscription_request_form import SubscriptionRequestForm


class WebsiteSubscriptionRequest(http.Controller):

    @http.route(
        [
            '/struct/<int:struct_id>/subscription',
            '/struct/<int:struct_id>/share/subscription',
            '/struct/<int:struct_id>/share/<int:finprod_id>/subscription'
        ],
        type='http',
        auth='user',
        website=True,
    )
    def subscribe_to_structure(self, struct_id=None, finprod_id=None, **post):
        """Route for form to subscribe to a new share."""
        # Get structure and perform access check
        struct = request.env["res.partner"].sudo().browse(struct_id)
        if not struct or not struct.is_platform_structure:
            raise NotFound
        form_context = {"struct": struct, "user": request.env.user}
        if request.httprequest.method == "POST":
            form = self.subscription_request_form(
                data=request.params, context=form_context
            )
            if form.is_valid():
                self.process_subscription_request_form(
                    form, context=form_context
                )
                return request.redirect(request.params.get("redirect", ""))
        else:
            form = self.subscription_request_form(context=form_context)
        qcontext = {"form": form, "struct": struct}
        return request.render("iwp_website.subscribe_to_structure", qcontext)

    def subscription_request_form(self, data=None, context=None):
        """Return Form object."""
        form = SubscriptionRequestForm(
            initial=self.subscription_request_form_initial(context=context),
            data=data or None,
            context=context,
        )
        return form

    def subscription_request_form_initial(self, context=None):
        """Return initial for subscription request form."""
        context = {} if context is None else context
        initial = {}
        user = context.get("user")
        struct = context.get("struct")
        # TODO: take the first share_type or the default one.
        if struct:
            default_share_types = struct.share_type_ids.filtered(
                lambda r: r.display_on_website and r.default_share_product
            )
            default_share_type = (
                default_share_types[0] if default_share_types else None
            )
            if default_share_type:
                initial["share_type"] = str(default_share_type.id)
                initial["quantity"] = (
                    max(
                        1,
                        round(
                            default_share_type.can_buy_min_amount(
                                user.partner_id
                            ) / default_share_type.list_price
                        )
                    )
                )
                initial["total_amount"] = (
                    default_share_type.list_price * initial["quantity"]
                )
        return initial

    def process_subscription_request_form(self, form, context=None):
        """Process subscription share form."""
        user = context.get("user")
        vals = self.subscription_request_vals(form, context=context)
        if user.parent_id.is_company:
            sub_req = (
                request.env['subscription.request']
                .sudo()
                .create_comp_sub_req(vals)
            )
        else:
            sub_req = request.env['subscription.request'].sudo().create(vals)
        sub_req.onchange_partner()  # Set other field

    def subscription_request_vals(self, form, context=None):
        """Reutrn vals to create a new subscription request."""
        partner = context.get("user").commercial_partner_id
        struct = context.get("struct")
        share_type = request.env["product.template"].sudo().browse(
            int(form.cleaned_data["share_type"])
        )
        vals = {
            "source": "website",
            "partner_id": partner.id,
            "name": partner.name,
            "email": partner.email,
            "address": partner.street,
            "zip_code": partner.zip,
            "city": partner.city,
            "country_id": partner.country_id.id,
            # "iban": partner.bank_ids[0].acc_number,
            "share_product_id": share_type.product_variant_id.id,
            "ordered_parts": form.cleaned_data["quantity"],
            "structure": struct.id,
        }
        if partner.is_company:
            vals["company_name"] = partner.name
        return vals
