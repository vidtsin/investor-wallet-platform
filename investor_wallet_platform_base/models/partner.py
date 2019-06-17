from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_plateform_structure = fields.Boolean(string="Is a Platform Structure")
    coop_membership = fields.One2many('coop.membership',
                                      'partner_id',
                                      string="Cooperative membership")
    initialized = fields.Boolean(string="Sequence initialized")
    structure_type = fields.Selection([('cooperative', 'Cooperative'),
                                       ('association', 'Association')],
                                      string="Structure type")
    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])
    account_journal = fields.Many2one('account.journal',
                                      string="Account Journal",
                                      readonly=True)
    register_sequence = fields.Many2one('ir.sequence',
                                        string="Register sequence",
                                        readonly=True)
    operation_sequence = fields.Many2one('ir.sequence',
                                         string="Operation Register",
                                         readonly=True)

    @api.multi
    def generate_sequence(self):
        self.ensure_one()
        journal_obj = self.env['account.journal']
        ir_sequence_obj = self.env['ir.sequence']

        sequence_vals = {
            'name': 'Subscription Register ' + self.name,
            'code': 'subscription.register.' + self.name.replace(" ", "_"),
            'number_next': 1,
            'number_increment': 1,
            }
        register_sequence = ir_sequence_obj.create(sequence_vals)

        sequence_vals = {
            'name': 'Register Operation ' + self.name,
            'code': 'register.operation.' + self.name.replace(" ", "_"),
            }
        operation_sequence = ir_sequence_obj.create(sequence_vals)
        sequence_vals = {
            'name': 'Account Default Subscription Journal ' + self.name,
            'padding': 3,
            'use_date_range': True,
            'prefix': 'SUBJ/%(year)s/',
            }
        journal_sequence = ir_sequence_obj.create(sequence_vals)
        # TODO create journal
        journal_vals = {
            'name': 'Subscription Journal ' + self.name,
            'code': 'SUBJ_' + self.name.replace(" ", "_"),
            'type': 'sale',
            'sequence_id': journal_sequence.id,
            }
        account_journal = journal_obj.create(journal_vals)
        self.register_sequence = register_sequence
        self.operation_sequence = operation_sequence
        self.account_journal = account_journal

        return True

    def get_membership(self, structure):
        return self.coop_membership.filtered(
                        lambda record: record.structure == structure.id)
