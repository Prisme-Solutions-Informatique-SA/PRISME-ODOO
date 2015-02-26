from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.osv import fields, osv, expression
import openerp.addons.decimal_precision as dp

class sale_order_line(osv.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    
    # Method copied from sale.order.line (_amount_line)
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            # Modification: compute the discount in function of the type
            if line.discount_type == 'amount':
                price = line.price_unit - (line.discount or 0.0)
            elif line.discount_type == 'percent':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit 
            
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price,
                                        line.product_uom_qty,
                                        line.order_id.partner_invoice_id.id,
                                        line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
            
            # Modification: if the line has been refused, set the price to 0
            if line.refused:
                res.update({line.id: 0.0})
            
            # Modification: if the rounding on subtotal has been set, recalculating
            # the subtotals
            elif line.order_id.rounding_on_subtotal > 0:
                old_amount = res[line.id]
                new_amount = round(old_amount / \
                                   line.order_id.rounding_on_subtotal) * \
                                   line.order_id.rounding_on_subtotal
                res.update({line.id: new_amount})
                
        return res
    
    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = super (sale_order_line, self)._product_margin(cr, uid, ids,
                                                            field_name, arg,
                                                            context=context)
        for line in self.browse(cr, uid, ids, context=context):
            
            # Don't compute margin for the line if it has been refused
            if line.refused:
                res[line.id] = 0.0
                continue
            
            if line.product_id:
                
                if line.discount_type == 'amount':
                    unit_price = line.price_unit - (line.discount or 0.0)
                elif line.discount_type == 'percent':
                    unit_price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                else:
                    unit_price = line.price_unit 
                
                if line.purchase_price:
                    res[line.id] = round((unit_price * line.product_uos_qty) - (line.purchase_price * line.product_uos_qty), 2)
                else:
                    res[line.id] = round((unit_price * line.product_uos_qty) - (line.product_id.standard_price * line.product_uos_qty), 2)
        return res
    
    def _get_lines_recompute(self, cr, uid, ids, context = {}):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = True
        return res.keys()
    
    _columns = {
        'date_delivery': fields.date('Delivery Date'),
        'price_subtotal': fields.function(_amount_line, method=True, \
                              string='Subtotal', store={
                                'sale.order.line': (_get_lines_recompute,
                                                    ['price_unit', 'discount',
                                                     'discount_type','product_uom_qty'], 2)
                                                        }, \
                              digits_compute=dp.get_precision('Sale Price')),
                              
        'refused': fields.boolean('Refused', readonly=True,
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly',False)],
                    'done': [('readonly',False)]}),
        'refusal_reason': fields.char('Refusal Reason', 255, readonly=True,
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly', False)],
                    'done': [('readonly',False)]}),
                
        'cancellation_reason': fields.char("Cancellation Reason", 255,
            readonly=True,
            states={'draft': [('readonly', False)],
                      'manual': [('readonly', False)],
                      'progress': [('readonly', False)],
                      'shipping_except': [('readonly', False)],
                      'invoice_except': [('readonly', False)]}),
              
             
        # Column copied from sale.order.line and renamed to remove '%'   
        'discount': fields.float('Discount', digits=(16, 2),
                                 readonly=True,
                                 states={'draft': [('readonly', False)]}),
        'discount_type': fields.selection([('amount', 'Amount'),
                                           ('percent', 'Percent')],
                                          'Discount type', readonly=True,
                                          states={'draft': [('readonly', False)]}),
        
        # Method overriden to use the method in this class
        'margin': fields.function(_product_margin, method=True, string='Margin', store=True),
		'shipped': fields.boolean('Shipped'),
        
        #Make field 'dely' a optional
        'delay' : fields.float('delay', readonly=True, states={'draft': [('readonly', False)]})
    }
    
    _defaults = {
        'discount_type': 'percent',
    }
    
    def _check_refusal_reason(self, cr, uid, ids):
        ok = True
        for line in self.browse(cr, uid, ids):
            # TODO Demander a David s'il a une idee d'ou ca vient:
            # Si on enleve ces 2 lignes, quand on confirme SO avec des lignes 
            # non valides (refusee sans raison), le programme annule les
            # modifications faites depuis la derniers sauvegarde, puis confirme
            # quand meme la SO
            if line.state == 'draft':
                continue
            if line.refused:
                if not line.refusal_reason:
                    ok = False
        return ok

    _constraints = [
                    (_check_refusal_reason,
                     'You must give a reason for each line you refuse',
                     ['refused', 'refusal_reason']),
                   ]
    
    # Methode appelee lors de la creation d'une ligne de facture depuis
    # une SO
    def invoice_line_create(self, cr, uid, ids, context=None):
        # Pour chaque ligne de la SO
        for line in self.browse(cr, uid, ids, context=context):
            # Si la ligne a ete refusee
            if line.refused:
                # Suppression de l'id de cette ligne de la liste des ids des
                # lignes de SO sur lesquels creer des lignes de facture
                ids.remove(line.id)
                # Appel de la methode standard qui cree des lignes de facture
                # depuis les lignes de SO (ids)
        res = super(sale_order_line, self).invoice_line_create(cr, uid,
                    ids, context=context)
        return res
    
    def get_number_of_days_prisme(self, cr, uid, ids, date_to):
        import datetime
        
        res = {'value':{}}
        
        """Returns a float equals to the timedelta between two dates given as string."""
 
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        
        date_from = datetime.date.today().strftime(DATETIME_FORMAT)
        
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)

        dt_end = False
        if date_to:
            to_dt = datetime.datetime.strptime(date_to, "%Y-%m-%d")
            timedelta = to_dt - from_dt
            diff_day = timedelta.days + float(timedelta.seconds) / 86400
            res["value"]["delay"] = diff_day
        return res
      
sale_order_line()
