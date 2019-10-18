# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class LoanIssue(models.Model):
    _inherit = "loan.issue"

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        domain=[("is_plateform_structure", "=", True)],
        default=default_structure,
    )


class LoanIssueLine(models.Model):
    _inherit = "loan.issue.line"

    structure = fields.Many2one(
        comodel_name="res.partner",
        string="Platform Structure",
        related="loan_issue_id.structure",
    )
