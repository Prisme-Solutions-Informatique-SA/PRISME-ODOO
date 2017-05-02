from odoo import api, fields, models, _

class stock_production_lot(models.Model):
    _name = "stock.production.lot"
    _inherit = "stock.production.lot"
    

    description = fields.Text("Description")
    model_no = fields.Char("Model No")
    customer = fields.Many2one("res.partner", string="Customer", domain="[('customer','=', 1)]")
    user = fields.Char("End User")
    user_department = fields.Char("End User Dept")
    installation_date = fields.Date("Installation Date")
                #TODO The context would complete the partner search field to
                # match the customer name
    customer_invoice = fields.Many2one("account.invoice",
                                        string="Customer Invoice",
                                        domain="[('type','=','out_invoice')]",)
    attachments = fields.Text("Attachments")
    manufacturer = fields.Char("Manufacturer")
    manufact_item_no = fields.Char("Part. Number")
    supplier = fields.Many2one("res.partner", string="Supplier", domain="[('supplier','=', 1)]")
    supplier_item_no = fields.Char("Supplier Item No")

    supplier_invoice = fields.Many2one("account.invoice", string="Supplier Invoice", domain="[('type','=','in_invoice')]")
    delivery_date = fields.Date("Delivery Date")
    remarks = fields.Text("Remarks")
                
    warranties_ids = fields.One2many('prisme.warranty.warranty', 'lot_id', 'Warranties')
    end_life_date = fields.Date("Delivery Date")

    @api.one
    @api.onchange('product_id')
    def onchange_product(self):
        value_to_return = {}
        if(self.product_id):
            self.description = self.product_id.product_tmpl_id.description
            self.warranty_description = self.product_id.product_tmpl_id.description


    @api.multi
    def write(self, vals):
        print "Write fonction !"
        res = super(stock_production_lot,self).write(vals)
        for w in self.warranties_ids:
            w.partner = self.customer
        
        return res
