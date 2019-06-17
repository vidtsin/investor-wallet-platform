from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    structure = fields.Many2one('res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)])
