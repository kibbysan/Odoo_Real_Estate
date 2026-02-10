from odoo import models, fields

class EstateMixin(models.Model):
    _name = "estate.mixin"

    name = fields.Char(string="Name", required=True)