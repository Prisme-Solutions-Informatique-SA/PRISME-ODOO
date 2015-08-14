from openerp import netsvc
from openerp.osv import fields, osv, expression
import openerp.addons.decimal_precision as dp

class account_invoice_line_prisme(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
    

    # def copied to add control of amount discount
    def _compute_price(self):
        if self.discount_type == 'amount':
            price = self.price_unit - (self.discount or 0.0)
        elif self.discount_type == 'percent':
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        else:
            price = self.price_unit
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)

       
    
    _columns = {
        
        # Field copied to remove the '%' in the label        
        'discount': fields.float(string='Discount'   ,digits=dp.get_precision('Discount'),default=0.0),

        # Field add to allow amount discount
        'discount_type': fields.selection([('none', ''),
                                           ('amount', 'Amount'),
                                           ('percent', 'Percent')],
                                          'Discount type'),
    }
    
    _defaults = {
        'discount_type': 'percent',
    }
    
    # Methode appelee lorsqu'on change le produit dans une ligne d'une facture
    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', \
                           type='out_invoice', partner_id=False, fposition_id=False, \
                            price_unit=False, currency_id=False, company_id=None, context=None, ):
        # Execution de la commande originale (faite par OpenERP)
        res = super(account_invoice_line_prisme, self).product_id_change(cr,uid, ids, product, uom_id, qty, name, type, partner_id, fposition_id,price_unit, currency_id,context=context, company_id=company_id)
        # Si la facture est de type out (facture client)
        if (type == "out_invoice"):
            # Si un produit est definit
            if product:
                # Recuperation du produit
                product = self.pool.get("product.product").browse(cr, uid,
                                            product, context=context)
                # Recuperation du compte analytique de vente de produit
                prod_analytic_acc = product.sale_analytic_account_id
                # Si le compte analytique existe
                if prod_analytic_acc:
                    # Modifie la valeur du compte analytique de la ligne de
                    # la facture dans le resultat
                    res["value"].update({"account_analytic_id": 
                                         prod_analytic_acc.id})
            else:
                # Si le produit n'est pas (ou plus) definit, le compte 
                # analytique de la ligne de la facture est mis a vide
                res["value"].update({"account_analytic_id": False})
        return res
    #Line for live debug:
    #import pdb; pdb.set_trace()

account_invoice_line_prisme()
