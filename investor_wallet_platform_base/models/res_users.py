from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])
