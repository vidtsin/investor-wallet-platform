from odoo import fields, models

EMAIL_TEMPLATE_IDS = [
    "easy_my_coop.email_template_release_capital",
    "easy_my_coop.email_template_confirmation",
    "easy_my_coop.email_template_confirmation_company",
    "easy_my_coop.email_template_certificat",
    "easy_my_coop.email_template_certificat_increase",
    "easy_my_coop.email_template_share_transfer",
    "easy_my_coop.email_template_share_update",
    "easy_my_coop_loan.loan_subscription_confirmation",
    "easy_my_coop_loan.loan_issue_payment_request"
    ]


class MailTemplate(models.Model):
    _inherit = "mail.template"

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)])
