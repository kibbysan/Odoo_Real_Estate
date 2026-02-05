from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag Model"
    _sql_constraints = [
        ("tag_name_unique", "UNIQUE(name)", "The tag name must be unique.")
    ]

    name = fields.Char(string='Name', required=True)

