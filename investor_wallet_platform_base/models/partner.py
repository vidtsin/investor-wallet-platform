from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_plateform_structure = fields.Boolean(string="Platform Structure")
    stucture_type = fields.Selection([('cooperative', 'Cooperative'),
                                      ('association', 'Association')],
                                     string="Structure type")
    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])
