from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SubscriptionRequest(models.Model):
    _inherit = 'subscription.request'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])


class ShareLine(models.Model):
    _inherit = 'share.line'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])


class SubscriptionRegister(models.Model):
    _inherit = 'subscription.register'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])


class OperationRequest(models.Model):
    _inherit = 'operation.request'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])
