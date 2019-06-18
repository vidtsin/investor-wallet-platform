# Copyright 2018 Odoo SA <http://odoo.com>
# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.http import request
from odoo.tools.translate import _


class InvestorWallet(CustomerPortal):

    @http.route(['/my/wallet'], type='http', auth="user", website=True)
    def portal_my_wallet(self, page=1, date_begin=None, date_end=None,
                         sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        shareline_mgr = request.env['share.line']

        domain = self.shareline_domain

        searchbar_sortings = {
            # FIXME: Should be ordered by the name of the structure not
            # his id.
            # 'structure': {'label': _('Structure'), 'order': 'structure'},
            'date': {'label': _('Date'), 'order': 'effective_date asc'},
            # FIXME: total_amount_line is a computed field that cannot
            # be ordered
            # 'amount': {'label': _('Amount'), 'order': 'total_amount_line'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        # FIXME: _get_archive_groups do no use sudo
        # archive_groups = self._get_archive_groups('share.line', domain)
        # if date_begin and date_end:
        #     domain += [('effective_date', '>', date_begin),
        #                ('effective_date', '<=', date_end)]

        # count for pager
        shareline_count = shareline_mgr.sudo().search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/wallet",
            url_args={
                'date_begin': date_begin,
                'date_end': date_end,
                'sortby': sortby
            },
            total=shareline_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        sharelines = shareline_mgr.sudo().search(
            domain,
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_sharelines_history'] = sharelines.ids[:100]

        # Grand Amount Total
        grand_total = sum([sl.total_amount_line for sl in sharelines])

        values.update({
            'date': date_begin,
            'finproducts': sharelines.sudo(),
            'grand_total': grand_total,
            'page_name': 'wallet',
            'pager': pager,
            # 'archive_groups': archive_groups,
            'default_url': '/my/wallet',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render(
            'investor_wallet_platform_website.portal_my_wallet',
            values
        )

    @http.route('/struct', type='http', auth="public", website=True)
    def structure(self, page=1, sortby=None, **kw):
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
            'investor_wallet_platform_website.structures',
            values
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
