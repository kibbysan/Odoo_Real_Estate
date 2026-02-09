from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property Model"
    _sql_constraints = [
        ("expected_price_positive", "CHECK(expected_price > 0)", "The expected price must be positive."),
        ("selling_price_positive", "CHECK(selling_price >= 0)", "The selling price must be non-negative.")
    ]
    _order = "id desc"
    active = fields.Boolean(default=True)
    name = fields.Char(string ="Title ", required=True)
    state = fields.Selection(
        [
            ('new', 'New'),
            ('received', 'Offer Received'),
            ('accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        required=True,
        copy=False,
        default='new'
    )
    description = fields.Text(string ="Description")
    other_info = fields.Text(string ="Other Info")
    postcode = fields.Char(string ="Postcode")

    def default_date(self):
        return fields.Date.today()

    date_availability = fields.Date(
        string="Date Availability", 
        default=lambda self: fields.Date.today() + relativedelta(months=3),
        copy=False 
    )
    expected_price = fields.Float(string ="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string='Living Area', default=50)
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ],
        string="Garden Orientation"
    )
    property_type_id = fields.Many2one(
        comodel_name= 'estate.property.type'
    )

    offer_ids = fields.One2many(
        comodel_name = "estate.property.offer",
        inverse_name = "property_id"
    )

    tag_ids = fields.Many2many(
        comodel_name = "estate.property.tag"
    )
    total_area = fields.Integer(compute="_compute_total_area")
    best_offer = fields.Float(compute="_compute_best_offer")

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for property in self:
            property.best_offer = max(property.offer_ids.mapped('price')) if property.offer_ids else 0.0

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.onchange('garden')
    def _onchange_garden(self):
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden_orientation = 'north'
            else:
                record.garden_area = 0
                record.garden_orientation = False

    @api.onchange('date_availability')
    def onchange_date_availability(self):
        for record in self:
            if record.date_availability and record.date_availability < fields.Date.today():
                return{
                    'warning': {
                        'title': _('Warning'),
                        'message': _('The availability date has been set in the past.')
                    }
                }
            
    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError(_('A canceled property cannot be marked as sold.'))
            record.state = 'sold'
        return True
    
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError(_('A sold property cannot be cancelled.'))
            record.state = 'canceled'
        return True
    
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            # ONLY check if the selling price has actually been set (not zero)
            if not float_is_zero(record.selling_price, precision_digits=2):
                if float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) == -1:
                    raise ValidationError(_("The selling price cannot be lower than 90% of the expected price!"))
                
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError(_('Only properties in "New" or "Canceled" state can be deleted.'))