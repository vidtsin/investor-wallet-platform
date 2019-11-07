from odoo import api, fields, models

from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def default_structure(self):
        return self.env.user.structure

    is_platform_structure = fields.Boolean(string="Is a Platform Structure")
    coop_membership = fields.One2many('coop.membership',
                                      'partner_id',
                                      string="Cooperative membership")
    initialized = fields.Boolean(string="Sequence initialized")
    structure_type = fields.Selection([('cooperative', 'Cooperative'),
                                       ('association', 'Association'),
                                       ('limited_company', 'Limited Company')],
                                      string="Structure type")
    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_platform_structure', '=', True)],
                                default=default_structure)
    account_journal = fields.Many2one('account.journal',
                                      string="Account Journal",
                                      readonly=True)
    register_sequence = fields.Many2one('ir.sequence',
                                        string="Register sequence",
                                        readonly=True)
    operation_sequence = fields.Many2one('ir.sequence',
                                         string="Operation Register",
                                         readonly=True)
    share_type_ids = fields.One2many("product.template",
                                     "structure",
                                     string="Share type")
    loan_issue_ids = fields.One2many("loan.issue",
                                     "structure",
                                     string="Loan issues")
    projects = fields.Html(string="Projects",
                           translate=True)
    display_on_website = fields.Boolean(string="display on website")
    # Move to another module ?
    is_renewable_energy = fields.Boolean(string="is renewable energy")
    renewable_energy = fields.Html(string="Renewable energy",
                                   translate=True)
    description = fields.Html(string="Description",
                              translate=True)
    about_us = fields.Html(string="About us",
                           translate=True)
    governance = fields.Html(string="Governance",
                             translate=True)
    cover_image = fields.Binary(string="Cover image",
                                translate=True)
    labour_on_capital = fields.Html(string="Labour on capital",
                                    translate=True)
    autonomy_of_management = fields.Html(string="Autonomy of management",
                                         translate=True)
    purpose_service = fields.Html(string="Purpose of service to members",
                                  translate=True)
    sustainable_development = fields.Html(string="Sustainable development",
                                          translate=True)
    key_numbers = fields.Html(string="Key Numbers",
                              translate=True)
    operational_risk = fields.Html(string="Operational & commercial risk",
                                   translate=True)
    governance_risk = fields.Html(string="Governance risk",
                                  translate=True)
    total_bs = fields.Char(string="Total balance sheet",
                           translate=True)
    equity = fields.Html(string="Equity",
                         translate=True)
    solvency_ratio = fields.Html(string="Solvency ratio",
                                 translate=True)
    last_result = fields.Html(string="Last result",
                              translate=True)
    last_dividend = fields.Html(string="Last 3 years dividend",
                                translate=True)
    break_even_date = fields.Date(string="Break-even date")
    liquidity_ratio = fields.Html(string="Liquidity ratio",
                                  translate=True)
    susbidies_risk = fields.Html(string="Risks related to subsidies",
                                 translate=True)
    subscription_maximum_amount = fields.Float(
        string="Maximum authorised subscription amount")
    approval = fields.Char(string="Approval",
                           translate=True)
    activity_areas = fields.Many2many('activity.area',
                                      string="Activity areas")
    employee_number = fields.Char(string="Employee number",
                                  translate=True)
    statute_link = fields.Char(string="Statute link")
    annual_report_link = fields.Char(string="Last annual report link")
    area_char_list = fields.Char(compute='_return_area_char_list',
                                 string="activity areas")

    @api.multi
    def _return_area_char_list(self):
        for partner in self:
            partner.area_char_list = partner.activity_areas.mapped('name')

    @api.multi
    def generate_sequence(self):
        self.ensure_one()
        journal_obj = self.env['account.journal']
        ir_sequence_obj = self.env['ir.sequence']

        if not self.initialized:
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
            self.initialized = True
        else:
            raise UserError(_('You cannot initialize an already initialized '
                              'structure'))
        return True

    def get_membership(self, structure):
        return self.coop_membership.filtered(
                        lambda record: record.structure == structure)
