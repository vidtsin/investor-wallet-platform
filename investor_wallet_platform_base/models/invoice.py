from odoo import fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])

    def validate_capital_release_request(self):
        if self.release_capital_request and not self.structure:
            raise ValidationError(_('There is no structure defined on this '
                                    'capital release request.'))
        return True

    def get_sequence_register(self):
        self.validate_capital_release_request()
        return self.structure.register_sequence

    def get_sequence_operation(self):
        self.validate_capital_release_request()
        return self.structure.operation_sequence

    def get_refund_domain(self, invoice):
        refund_domain = super(AccountInvoice, self).get_refund_domain(invoice)
        refund_domain.append(('structure', '=', invoice.structure.id))

        return refund_domain

    def get_subscription_register_vals(self, line, effective_date):
        vals = super(AccountInvoice,
                     self).get_subscription_register_vals(line, effective_date)
        vals['structure'] = self.structure.id

        return vals

    def get_share_line_vals(self, line, effective_date):
        vals = super(AccountInvoice, self).get_share_line_vals(line,
                                                               effective_date)
        vals['structure'] = self.structure.id
        return vals

    def get_membership_vals(self):
        membership = self.partner_id.get_membership(self.structure)

        if membership.member is False \
                and membership.old_member is False:
            sequence_id = self.get_sequence_register()
            sub_reg_num = sequence_id.next_by_id()
            vals = {'member': True, 'old_member': False,
                    'cooperator_number': int(sub_reg_num)
                    }
        elif membership.old_member:
            vals = {'member': True, 'old_member': False}

        return vals

    def set_membership(self):
        vals = self.get_membership_vals()
        membership = self.partner_id.get_membership(self.structure)

        membership.write(vals)

        return True
