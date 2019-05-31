from odoo import fields, models, _
from odoo.exceptions import ValidationError


class SubscriptionRequest(models.Model):
    _inherit = 'subscription.request'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])

    def get_journal(self):
        if self.structure:
            if self.structure.account_journal:
                return self.structure.account_journal
            else:
                raise ValidationError(_('There is no journal defined for this '
                                        'structure.'))
        else:
            raise ValidationError(_('There is no structure defined on this '
                                    'subscription request.'))

    def get_invoice_vals(self, partner):
        vals = super(SubscriptionRequest, self).get_invoice_vals(partner)
        vals['structure'] = self.structure.id
        
        return vals

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
