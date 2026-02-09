from odoo import _, api, fields, models

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
    offer_ids = fields.One2many(
        comodel_name= 'estate.property.offer',
        inverse_name= 'property_type_id')
    
    offer_count = fields.Integer(compute='_compute_offer_count')
    property_count = fields.Integer(compute='_compute_property_count')
    
    @api.model_create_multi
    def create(self, vals_list):
        types = super().create(vals_list)
        for prop_type in types:

            existing_tag = self.env['estate.property.tag'].search([('name', '=', prop_type.name)], limit=1)

            if not existing_tag:
                self.env['estate.property.tag'].create({
                    'name': prop_type.name,
                    'color': (prop_type.sequence % 11) + 1,
                })
        return types
    
    def unlink(self):
        self.property_ids.state = "canceled"
        return super().unlink()

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    @api.depends('property_ids')
    def _compute_property_count(self):
        for record in self:
            record.property_count = len(record.property_ids)

    def action_open_property_ids(self):
        return {
            "name": _("Related Properties"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "estate.property",
            "target": "current",
            "domain": [("property_type_id", "=", self.id)],
            "context": {"default_property_type_id": self.id},
        }
    
  