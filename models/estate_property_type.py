from odoo import fields, models

class EstatePropertyType(models.Model):
    _name= 'estate.property.type'
    _description= 'Estate Property Type Model'
    _sql_constraints = [
        ("type_name_unique", "UNIQUE(name)", "The type name must be unique.")
    ]
    name = fields.Char(string='Name', required= True)