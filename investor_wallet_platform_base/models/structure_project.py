from odoo import fields, models


class StructureProject(models.Model):
    _name = 'structure.project'
    _description = 'Structure Project'

    name = fields.Char(string="Name")
    description = fields.Html(string="Description")
    url = fields.Char(string="Url")
    structure_id = fields.Many2one('res.partner',
                                   string="Structure",
                                   domain=[('is_plateform_structure', '=', True)])
