# Copyright 2018 Odoo SA <http://odoo.com>
# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.iwp_website.controllers.investor_form import InvestorForm
from odoo.addons.iwp_website.controllers.investor_form import InvestorCompanyForm
from odoo.http import request
from odoo.tools.translate import _


class InvestorPortal(CustomerPortal):

    @http.route(['/my/wallet'], type='http', auth="user", website=True)
    def my_wallet(self, page=1, date_begin=None, date_end=None,
                  sortby=None, **kw):
        """Wallet of financial product for the connected user."""
        values = self._prepare_portal_layout_values()
        shareline_mgr = request.env['share.line']
        # loanlines_mgr = request.env['loan.issue.line']

        domain = self.shareline_domain

        # search the count to display, according to the pager data
        sharelines = shareline_mgr.sudo().search(
            domain,
            order='effective_date',
            limit=self._items_per_page
        )

        # Grand Amount Total
        grand_total = sum([sl.total_amount_line for sl in sharelines])

        values.update({
            'date': date_begin,
            'finproducts': sharelines.sudo(),
            'grand_total': grand_total,
            'page_name': 'wallet',
            'default_url': '/my/wallet',
        })
        return request.render(
            'iwp_website.portal_my_wallet',
            values
        )

    @http.route('/struct', type='http', auth="public", website=True)
    def structures(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        struct_mgr = request.env['res.partner']

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name'},
            'type': {'label': _('Type'), 'order': 'structure_type'},
        }

        # default sortby order
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        # count for pager
        struct_count = struct_mgr.sudo().search_count(self.structure_domain)
        # make pager
        pager = portal_pager(
            url='/struct',
            url_args={
                'sortby': sortby
            },
            total=struct_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        structures = struct_mgr.sudo().search(
            self.structure_domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'structures': structures.sudo(),
            'page_name': 'structures',
            'pager': pager,
            'default_url': '/struct',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render(
            'iwp_website.structures',
            values
        )

    @http.route()
    def account(self, redirect=None, **post):
        """Form processing to edit user details"""
        user = request.env.user
        if user.is_company:
            form = InvestorCompanyForm()
        else:
            form = InvestorForm()
        # Prepare the form
        form.normalize_form_data(request.params)
        form.validate_form(request.params)
        form.init_form_data(request.params)
        form.set_form_defaults(request.params, user=user)
        if 'firstname' in request.params or 'lastname' in request.params:
            request.params['name'] = form.generate_name_field(
                request.params.get('firstname', ''),
                request.params.get('lastname', ''),
            )
        # Process the form
        if ('error' not in request.params
                and request.httprequest.method == 'POST'):
            if user.is_company:
                # company
                values = {
                    key: request.params[key]
                    for key in request.params
                    if key in form.company_fields
                }
                user.write(values)
                # representative
                values = {
                    key[4:]: request.params[key]
                    for key in request.params
                    if key in form.representative_fields
                }
                representative = user.child_ids[0]
                representative.write(values)
            else:
                values = {
                    key: request.params[key]
                    for key in request.params
                    if key in form.user_fields
                }
                user.write(values)
            return request.redirect('/my/home')

        qcontext = request.params
        qcontext.update({
            'page_name': 'my_details',
        })
        if user.partner_id.is_company:
            return request.render(
                'iwp_website.investor_company_details',
                qcontext
            )
        return request.render(
            'iwp_website.investor_details',
            qcontext
        )

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        shareline_mgr = request.env['share.line']
        shareline_count = (shareline_mgr.sudo()
                           .search_count(self.shareline_domain))
        values.update({
            'finproduct_count': shareline_count,
        })
        return values

    @property
    def shareline_domain(self):
        partner = request.env.user.partner_id
        domain = [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ]
        return domain

    @property
    def structure_domain(self):
        domain = [
            ('is_plateform_structure', '=', True)
        ]
        return domain
