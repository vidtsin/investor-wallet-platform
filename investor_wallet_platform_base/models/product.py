from odoo import api, fields, models

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
                             string="State",
                             default='close')
    solidary = fields.Selection([('yes', 'Yes'),
                                 ('no', 'No')],
                                string="Solidary product")
    banking = fields.Selection([('yes', 'Yes'),
                                ('no', 'No')],
                               string="Banking product")
    book_value = fields.Float(string="Book value",
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
    minimum_amount = fields.Monetary(string="Minimum subscription amount",
                                     currency_field='currency_id')
    maximum_amount = fields.Monetary(string="Maximum subscription amount",
                                     currency_field='currency_id')
    access_terms = fields.Char(string="Terms of access",
                               translate=True)
    max_target_issue = fields.Monetary(string="Issue total amount",
                                       currency_field='currency_id')
    min_target_issue = fields.Monetary(string="Issue minimal amount",
                                       currency_field='currency_id')
    subscription_start_date = fields.Date(string="Issue Start date")
    subscription_end_date = fields.Date(string="Issue End date")
    subscription_length = fields.Char(string="Subscription length",
                                      translate=True)
    oversubscription_policy = fields.Char(string="Over subscription policy",
                                          translate=True)
    purpose_of_issue = fields.Html(string="Purpose of the issue",
                                   translate=True)
    price_fluctuation_risk = fields.Char(string="Price fluctuation risk",
                                         translate=True)
    capital_risk = fields.Html(string="Risk on equity",
                               translate=True)
    other_product_risk = fields.Html(string="Other risk on product",
                                     translate=True)
    transfer_allowed = fields.Html(string="Product transfer possibility",
                                   translate=True)
    refund_policy = fields.Html(string="Refund policy",
                                translate=True)
    info_note_url = fields.Char(string="Information note url")

    @api.model
    def count_published_shares(self):
        """Count number of share type that investor can invest in"""
        return self.search_count([
            ("is_share", "=", True),
            ("sale_ok", "=", True),
            ("state", "=", "open"),
            ("display_on_website", "=", True),
        ])

    @api.multi
    def can_buy_max_amount(self, partner_id):
        """
        Return the amount that a partner can subscribe on for this type
        of share product.
        Return a negative number if there is not limit.
        """
        self.ensure_one()
        company = self.env["res.company"]._company_default_get()
        amount_owned_structure = sum(
            sl.total_amount_line
            for sl in partner_id.share_ids
            if sl.structure == self.structure
        )
        amount_owned_share = self.owned_amount(partner_id)
        max_subscription = (
            self.structure.subscription_maximum_amount
            or company.subscription_maximum_amount
        )
        # First amount left regarding to the general max subscription
        if max_subscription > 0:
            left_amount = max_subscription - amount_owned_structure
            # Then amount left for this type of share
            if left_amount > 0:
                return max(0, self.maximum_amount - amount_owned_share)
            return 0
        return -1  # No limit

    @api.multi
    def can_buy_min_amount(self, partner_id):
        """
        Return the minimum amount that a partner have to subscribe.
        """
        self.ensure_one()
        return max(0, self.minimum_amount - self.owned_amount(partner_id))

    @api.multi
    def owned_amount(self, partner_id):
        """
        Return the amount of this type of share owned by the given
        partner.
        """
        return sum(
            sl.total_amount_line
            for sl in partner_id.share_ids
            if sl.share_product_id == self.product_variant_id
        )
