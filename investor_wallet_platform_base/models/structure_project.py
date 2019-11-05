from odoo import fields, models


class StructureProject(models.Model):
    _name = 'structure.project'
    _description = 'Structure Project'

    def default_structure(self):
        return self.env.user.structure

    name = fields.Char(string="Name",
                       translate=True)
    description = fields.Html(string="Description",
                              translate=True)
    url = fields.Char(string="Url")
    structure = fields.Many2one(
                        comodel_name='res.partner',
                        string="Structure",
                        domain=[("is_platform_structure", "=", True)],
                        default=default_structure)
