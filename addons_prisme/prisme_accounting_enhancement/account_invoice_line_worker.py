from openerp import netsvc
from openerp.osv import fields, osv, expression
import openerp.addons.decimal_precision as dp

class account_invoice_line_prisme(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
    
    def _amount_line_prisme(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            
            # Modification to use the discount_type
            if line.discount_type == 'amount':
                price = line.price_unit - (line.discount or 0.0)
            elif line.discount_type == 'percent':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit
            
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id,
                                        price, line.quantity,
                                        product=line.product_id,
                                        partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        
        # Modification to compute the subtotal using rounding_on_subtotal
        for line in self.browse(cr, uid, ids):
            if line.invoice_id.rounding_on_subtotal > 0:
                old_amount = res[line.id]
                new_amount = round(old_amount / \
                                   line.invoice_id.rounding_on_subtotal) * \
                                   line.invoice_id.rounding_on_subtotal
                res.update({line.id: new_amount})
    
        return res
        
    
    _columns = {
        "price_subtotal": fields.function(_amount_line_prisme, method=True, \
            string="Subtotal", type="float",
            digits_compute=dp.get_precision("Invoice"), store=True),
        
        # Field copied to remove the '%' in the label        
        'discount': fields.float('Discount',
                                 digits_compute=dp.get_precision('Account')),
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
