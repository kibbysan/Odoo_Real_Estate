from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offers made for real estates"

    _sql_constraints = [
        ('offer_price_positive', 'CHECK(price>0)', 'The offer price must be positive.')
    ]

    price =  fields.Float()
    status = fields.Selection(
        [
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        copy = False
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(related = 'property_id.property_type_id', store = True)

    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for offer in self:
            base_date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = base_date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            base_date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - base_date).days

    def action_accept(self):
        self.ensure_one()
        if "accepted" in self.property_id.offer_ids.mapped('status'):
            raise UserError(_("Another offer has already been accepted for this property."))
        self.status = 'accepted'
        self.property_id.selling_price = self.price
        self.property_id.state = 'accepted'
        return True
    
    def action_refuse(self):
        self.ensure_one()
        self.status = "refused"

        if self.property_id.selling_price == self.price:
            self.property_id.selling_price = 0
        return True
