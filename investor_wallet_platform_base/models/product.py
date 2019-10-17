from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def default_structure(self):
        return self.env.user.structure

    structure = fields.Many2one(comodel_name='res.partner',
                                string="Platform Structure",
                                domain=[('is_plateform_structure', '=', True)],
                                default=default_structure)
