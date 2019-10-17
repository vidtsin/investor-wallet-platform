from odoo import fields, models


class StructureProject(models.Model):
    _name = 'structure.project'
    _description = 'Structure Project'

    name = fields.Char(string="Name",
                       translate=True)
    description = fields.Html(string="Description",
                              translate=True)
    url = fields.Char(string="Url")

    # todo
    structure_id = fields.Many2one(
                        'res.partner',
                        string="Structure",
                        domain=[('is_plateform_structure', '=', True)])
