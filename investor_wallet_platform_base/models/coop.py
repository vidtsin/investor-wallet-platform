from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SubscriptionEquest(models.Model):
    _inherit = 'subscription.request'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])
