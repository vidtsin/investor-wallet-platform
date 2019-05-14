from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_plateform_structure = fields.Boolean(string="Plateform Structure")
    stucture_type = fields.Selection([('cooperative', 'Cooperative'),
                                      ('association', 'Association')],
                                     string="Structure type")
