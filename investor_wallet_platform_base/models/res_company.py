# Copyright 2019 Coop IT Easy SCRL fs
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    published_financial_product = fields.Integer(
        string="Published Financial Product",
        compute="_compute_published_financial_product",
        help="Number of financial product that investor can invest in",
    )

    nb_investor = fields.Integer(
        string="Number of Investor", compute="_compute_nb_investor"
    )

    total_outstanding_amount = fields.Monetary(
        string="Total Outstanding Amount",
        currency_field="currency_id",
    )

    def _compute_published_financial_product(self):
        """Count financial product that investor can invest in"""
        nb_loans = self.env["loan.issue"].count_published_loans()
        nb_shares = self.env["product.template"].count_published_shares()
        self.published_financial_product = nb_loans + nb_shares

    def _compute_nb_investor(self):
        """Count number of investors"""
        loaners = self.env["res.partner"].search_count(
            [("is_loaner", "=", True)]
        )
        cooperators = self.env["res.partner"].search_count(
            [("member", "=", True)]
        )
        self.nb_investor = loaners + cooperators
