# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
import logging


_logger = logging.getLogger(__name__)


class WebsiteLoanIssue(http.Controller):

    @http.route(
        [
            '/loan/subscription',
        ],
        type='http',
        auth='user',
        website=True,
    )
    def subscribe_to_loan_issue(
        self,
        **post
    ):
        self.init_form_data(qcontext=post)
        self.set_form_defaults(qcontext=post)
        self.normalize_form_data(qcontext=post)
        if post and request.httprequest.method == 'POST':
            self.validate_form(qcontext=post)
            if 'error' not in post:
                values = self.prepare_loan_issue_line_value(qcontext=post)
                request.env['loan.issue.line'].sudo().create(values)
                post['success'] = True
        # Populate template value
        qcontext = post.copy()
        return request.render(
            'iwp_website.subscribe_to_loan_issue',
            qcontext
        )

    def prepare_loan_issue_line_value(self, qcontext=None):
        if qcontext is None:
            qcontext = request.params
        partner = request.env.user.partner_id
        loan_issue = request.env['loan.issue'].browse(qcontext['loan_issue'])
        values = {
            'loan_issue_id': loan_issue.id,
            'partner_id': partner.id,
            'quantity': qcontext['quantity'],
        }
        return values

    def validate_form(self, qcontext=None):
        """
        Populate request.parms with errors if the params from the form
        are not correct. If a qcontext is given, this function works on
        this qcontext.
        """
        if qcontext is None:
            qcontext = request.params
        selected_issue = qcontext.get('loan_issue', None)
        if not selected_issue:
            qcontext['error'] = _("You must select a financial product.")
            return qcontext
        if qcontext.get('quantity', 0) < 1:
            qcontext['error'] = _("You must order at least 1 financial"
                                  " product.")
            return qcontext
        return qcontext

    def init_form_data(self, qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        defalut data needed to render the form.
        """
        if qcontext is None:
            qcontext = request.params
        # Loan issues
        is_company = request.env.user.type == 'company'
        loan_issues = (
            request.env['loan.issue'].sudo().get_web_issues(is_company)
        )
        qcontext.update({
            'loan_issues': loan_issues,
        })
        return qcontext

    def set_form_defaults(self, qcontext=None, force=False):
        """
        Populate the given qcontext or request.parms if empty with the
        default value for the form.
        """
        if qcontext is None:
            qcontext = request.params
        # Set number according to the default share
        if 'quantity' not in qcontext or force:
            qcontext['number'] = 0
        if 'total_amount' not in qcontext or force:
            qcontext['total_amount'] = 0
        return qcontext

    def normalize_form_data(self, qcontext=None):
        """
        Normalize data encoded by the user.
        """
        if qcontext is None:
            qcontext = request.params
        # Convert to int when needed
        if 'quantity' in qcontext:
            qcontext['quantity'] = int(qcontext['quantity'])
        if 'loan_issue' in qcontext:
            qcontext['loan_issue'] = int(qcontext['loan_issue'])
        return qcontext
