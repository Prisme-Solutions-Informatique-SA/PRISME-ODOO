from osv import osv, fields
import netsvc
import decimal_precision as dp
import time
from lxml import etree
import openerp.exceptions
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _



class account_invoice_line_prisme(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"

    
    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
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

    def _price_unit_default(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('check_total', False):
            t = context['check_total']
            for l in context.get('invoice_line', {}):
                if isinstance(l, (list, tuple)) and len(l) >= 3 and l[2]:
                    tax_obj = self.pool.get('account.tax')
                    p = 0
                    if l[2].get('discount_type')=='amount':
                      p = l[2].get('price_unit', 0) - l[2].get('discount', 0)
                    else:
                      p = l[2].get('price_unit', 0) * (1-l[2].get('discount', 0)/100.0)
                    t = t - (p * l[2].get('quantity'))
                    taxes = l[2].get('invoice_line_tax_id')
                    if len(taxes[0]) >= 3 and taxes[0][2]:
                        taxes = tax_obj.browse(cr, uid, list(taxes[0][2]))
                        for tax in tax_obj.compute_all(cr, uid, taxes, p,l[2].get('quantity'), l[2].get('product_id', False), context.get('partner_id', False))['taxes']:
                            t = t - tax['amount']
            return t
        return 0
        
   
    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        for line in inv.invoice_line:
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)
            tax_code_found= False
            price = 0
            # Modification to use the discount_type
            if line.discount_type == 'amount':
                price = line.price_unit - (line.discount or 0.0)
            elif line.discount_type == 'percent':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit

            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id,
                    price,
                    line.quantity, line.product_id,
                    inv.partner_id)['taxes']:

                if inv.type in ('out_invoice', 'in_invoice'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = line.price_subtotal * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = line.price_subtotal * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, tax_amount, context={'date': inv.date_invoice})
        return res

 
    _columns = {
        "price_subtotal": fields.function(_amount_line, method=True, \
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
                            price_unit=False, currency_id=False, context=None, company_id=None):
        # Execution de la commande originale (faite par OpenERP)
        res = super(account_invoice_line_prisme, self).product_id_change(cr, \
                    uid, ids, product, uom_id, qty, name, type, partner_id, fposition_id, \
                     price_unit, currency_id, context=context, company_id=company_id)
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


class account_invoice_tax(osv.osv):
    _name = "account.invoice.tax"
    _inherit = "account.invoice.tax"

    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        for line in inv.invoice_line:
            price = 0
            # Modification to use the discount_type
            if line.discount_type == 'amount':
                price = line.price_unit - (line.discount or 0.0)
            elif line.discount_type == 'percent':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit

            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, line.product_id, inv.partner_id)['taxes']:
                val={}
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line['quantity'])
                if inv.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped

account_invoice_tax()

