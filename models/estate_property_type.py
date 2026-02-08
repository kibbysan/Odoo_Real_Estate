from odoo import fields, models

class EstatePropertyType(models.Model):
    _name= 'estate.property.type'
    _description= 'Estate Property Type Model'
    _sql_constraints = [
        ("type_name_unique", "UNIQUE(name)", "The type name must be unique.")
    ]
    _order = "sequence desc, name"

    sequence = fields.Integer(default=1)
    name = fields.Char(string='Name', required= True)
    property_ids = fields.One2many(
        comodel_name= 'estate.property',
        inverse_name= 'property_type_id')