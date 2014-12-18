from osv import osv, fields
import stock

class stock_production_lot(osv.osv):
    _name = "stock.production.lot"
    _inherit = "stock.production.lot"
    
    _columns = {
                "description": fields.text("Description"),
                "model_no": fields.char("Model No", 255),
                "customer": fields.many2one("res.partner", string="Customer",
                                            domain="[('customer','=', 1)]"),
                "user": fields.char("End User", 255),
                "user_department": fields.char("End User Dept", 255),
                "installation_date": fields.date("Installation Date"),
                #TODO The context would complete the partner search field to
                # match the customer name
                "customer_invoice": fields.many2one("account.invoice",
                                        string="Customer Invoice",
                                        domain="[('type','=','out_invoice')]",),
                "attachments": fields.text("Attachments"),
                "manufacturer": fields.char("Manufacturer", 255),
                "manufact_item_no": fields.char("Part. Number", 255),
                "supplier": fields.many2one("res.partner", string="Supplier",
                                            domain="[('supplier','=', 1)]"),
                "supplier_item_no": fields.char("Supplier Item No", 255),
                #TODO The context would complete the partner search field to
                # match the supplier name
                "supplier_invoice": fields.many2one("account.invoice",
                                        string="Supplier Invoice",
                                        domain="[('type','=','in_invoice')]"),
                "delivery_date": fields.date("Delivery Date"),
                "remarks": fields.text("Remarks"),
                
                # TODO Faire en sorte que le champ lot de production de la 
                # garantie soit mis a jour immediatement lorsqu'on le cree
                # depuis le lot de production.
                'warranties_ids': fields.one2many('prisme.warranty.warranty',
                                    'lot_id', 'Warranties'),
    }
    
    def onchange_product(self, cr, uid, ids, product_id):
        value_to_return = {}
        if(product_id):
            products = \
                self.pool.get('product.product').browse(cr, uid, [product_id])
            i = 0
            for product in products:
                i += 1
                value_to_return['description'] = \
                    product.product_tmpl_id.description
                value_to_return['warranty_description'] = \
                    product.product_tmpl_id.description
        return {'value': value_to_return}
    
    #Line for live debugging:
    #import pdb; pdb.set_trace()

stock_production_lot()
