from odoo import fields, models

from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)
    state = fields.Selection([('open', 'Open'),
                              ('close', 'Close'),
                              ('waiting', 'Waiting list')],
                             string="State")
    solidary = fields.Selection([('yes', 'Yes'),
                                 ('no', 'No')],
                                string="Solidary product")
    banking = fields.Selection([('yes', 'Yes'),
                                ('no', 'No')],
                               string="Banking product")
    book_value = fields.Html(string="Book value",
                             translate=True)
    dividend_date = fields.Date(string="Dividend payment date")
    dividend_policy = fields.Html(string="Dividend policy",
                                  translate=True)
    voting_rights = fields.Html(string="Voting rights",
                                help="Voting rights of the associate",
                                translate=True)
    advantages = fields.Html(string="Other advantages",
                             translate=True)
    tax_policy = fields.Char(string="Tax policy",
                             translate=True)
    tax_benefit = fields.Char(string="Tax benefit",
                              translate=True)
    fees = fields.Html(string="Subscription_fees",
                       translate=True)
    minimum_amount = fields.Float(string="Minimum subscription amount",
                                  digits=dp.get_precision('Product Price'))
    maximum_amount = fields.Float(string="Maximum subscription amount",
                                  digits=dp.get_precision('Product Price'))
    access_terms = fields.Char(string="Terms of access",
                               translate=True)
    max_target_issue = fields.Float(string="Issue total amount")
    min_target_issue = fields.Float(string="Issue minimal amount")
    subscription_start_date = fields.Date(string="Issue Start date")
    subscription_end_date = fields.Date(string="Issue End date")
    subscription_length = fields.Char(string="Subscription length",
                                      translate=True)
    oversubscription_policy = fields.Char(string="Over subscription policy",
                                          translate=True)
    purpose_of_issue = fields.Html(string="Purpose of the issue",
                                   translate=True)
    price_fluctuation_risk = fields.Char(string="Price fluctuation price")
    capital_risk = fields.Html(string="Risk on equity",
                               translate=True)
    other_product_risk = fields.Html(string="Other risk on product",
                                     translate=True)
    transfer_allowed = fields.Html(string="Product transfer possibility",
                                   translate=True)
    refund_policy = fields.Html(string="Refund policy",
                                translate=True)
    info_note_url = fields.Char(string="Information note url")
