from datetime import datetime
from datetime import datetime, timedelta
from openerp import tools
from odoo import api, fields, models, _
import openerp.addons.decimal_precision as dp
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    
    # Column copied from sale.order.line and renamed to remove '%'   
    discount = fields.Float(string='Discount (percent)', digits=dp.get_precision('Discount'), default=0.0)
    #New field for discount in amount
    discount_amount = fields.Float(string='Discount (amount)', digits=(16, 2), default=0.0)
    
    #Deprecated, tried to delete but stuck with a "discount_type doest not exist" error
    #Seems to work when uninstalling then installing the module but then the data is lost...
    discount_type = fields.Selection([('amount', 'Amount'),
                                  ('percent', 'Percent')],
                                   'Discount type', readonly=True,
                                    states={'draft': [('readonly', False)]},
                                    default='percent')

    def check_discount_percent(self, discount_value):
        error = ""
        if (discount_value < 0.0):
            error = _("A discount in percent cannot be negative !")
        elif (discount_value > 100.0):
            error = _("A discount in percent cannot be bigger than 100 !")
        return error
 
    def check_discount_amount(self, discount_amount_value, price_unit_value):
        error = ""
        if (discount_amount_value < 0.0):
            error = _("A discount in amount cannot be negative !")
        elif (discount_amount_value > price_unit_value):
            error = _("A discount in amount cannot be bigger than the price !")
        return error
     
     
    #Override "create" and "write" functions to check discount constraints each save/creation in DB.
    #Tried using @api.constrains for almost one day, seems never to be called...
    @api.model
    def create(self, values):
        # Do your custom logic here
        final_error = ""
        if 'discount' in values:
            error = self.check_discount_percent(values['discount'])
            if error:
                final_error+=(error+"\n")
        if 'discount_amount' in values:
            error = self.check_discount_amount(values['discount_amount'], values['price_unit'])
            if error:
                final_error+=error
        if final_error:
            raise ValidationError(final_error)    
        return super(sale_order_line, self).create(values)
 
    @api.model
    def write(self, values):
        # Do your custom logic here
        final_error = ""
        if 'discount' in values:
            error = self.check_discount_percent(values['discount'])
            if error:
                final_error+=(error+"\n")
        if 'discount_amount' in values:
            error = self.check_discount_amount(values['discount_amount'], self.price_unit)
            if error:
                final_error+=error
        if final_error:
            raise ValidationError(final_error)
        return super(sale_order_line, self).write(values)

    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            # Prisme Modification begin
            if line.refused:
                continue
            # Prisme Modification end
            
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].create(vals)
            new_proc.message_post_with_view('mail.message_origin_link',
                values={'self': new_proc, 'origin': line.order_id},
                subtype_id=self.env.ref('mail.mt_note').id)
            new_procs += new_proc
        new_procs.run()
        return new_procs
    
    
    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        # Prisme modification start
        if self.date_delivery:
            date_planned = datetime.strptime(self.date_delivery, "%Y-%m-%d")
        else:
            date_planned = datetime.strptime(self.order_id.date_order, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=self.customer_lead or 0.0)
        date_planned = (date_planned - timedelta(days=self.order_id.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # Prisme modification end
        return {
            'name': self.name,
            'origin': self.order_id.name,
            'date_planned': date_planned,
            'product_id': self.product_id.id,
            'product_qty': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            'company_id': self.order_id.company_id.id,
            'group_id': group_id,
            'sale_line_id': self.id
        }

    price_subtotal = fields.Monetary(compute='_compute_amount_prisme', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Monetary(compute='_compute_amount_prisme', string='Taxes', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount_prisme', string='Total', readonly=True, store=True)
    
    price_reduce = fields.Monetary(compute='_get_price_reduce_prisme', string='Price Reduce', readonly=True, store=True)
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_amount')
    def _compute_amount_prisme(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
             # Prisme modification start
            price = line.price_unit
            if (line.discount_amount):
                price = price - line.discount_amount
                
            if (line.discount):
                price = price * (1 - (line.discount / 100.0))
            
            # Modification: if the line has been refused, set the price to 0
            if line.refused or line.layout_type != 'article':
                price = 0.0
            # Prisme modification end
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            
            #Prisme Modification start: if the rounding on subtotal has been set, recalculating
            # the subtotals
            if line.refused != True and line.order_id.rounding_on_subtotal > 0:
                old_price_subtotal = line.price_subtotal
                new_price_subtotal = round(old_price_subtotal / \
                                   line.order_id.rounding_on_subtotal) * \
                                   line.order_id.rounding_on_subtotal
                line.update({
                    'price_subtotal': new_price_subtotal,
                })
            #Prisme modification end
  
  
    @api.depends('price_unit', 'discount', 'discount_amount')
    def _get_price_reduce_prisme(self):

        for line in self:
            #Prisme Modification start: compute the reduced price with amount and/or percent discount
            if line.refused or line.layout_type != 'article':
                continue           
            
            price = line.price_unit
            if (line.discount_amount):
                price = price - line.discount_amount
                
            if (line.discount):
                price = price * (1 - (line.discount / 100.0))

                
            line.price_reduce = price
             #Prisme modification end
            
    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit')
    def _product_margin(self):
        for line in self:
            if line.refused or line.layout_type != 'article':
                line.margin = 0.0
                continue
            
            currency = line.order_id.pricelist_id.currency_id
            margin = currency.round(line.price_subtotal - ((line.purchase_price or line.product_id.standard_price) * line.product_uom_qty))
            line.margin = margin
            #line.write({'margin': margin})
    
    
    date_delivery = fields.Date('Delivery Date')
                              
    refused = fields.Boolean('Refused', readonly=True,
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly',False)],
                    'done': [('readonly',False)]})
    
    refusal_reason = fields.Char('Refusal Reason', readonly=True,
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly', False)],
                    'done': [('readonly',False)]})
                
    cancellation_reason = fields.Char("Cancellation Reason",
            readonly=True,
            states={'draft': [('readonly', False)],
                      'manual': [('readonly', False)],
                      'progress': [('readonly', False)],
                      'shipping_except': [('readonly', False)],
                      'invoice_except': [('readonly', False)]})
              
             

    #discount = fields.Float('Discount', digits=(16, 2),
    #                             readonly=True,
    #                             states={'draft': [('readonly', False)]})

    
    # Method overriden to use the method in this class     
    shipped = fields.Boolean('Shipped')
        
    #Make field 'customer_lead' a optional
    customer_lead = fields.Float(
        'Delivery Lead Time', required=False, default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer", oldname="delay")
    
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=False)
    
    @api.constrains('refused')
    def _check_refusal_reason(self):
        ok = True
        for line in self:
            if line.refused:
                if not line.refusal_reason:
                     raise ValidationError('You must give a reason for each line you refuse')
        return ok
    
    @api.multi
    def invoice_line_create(self, invoice_id, qty):    
        
        """
        Create an invoice line. The quantity to invoice can be positive (invoice) or negative
        (refund).

        :param invoice_id: integer
        :param qty: float quantity to invoice
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            # Si la ligne a ete refusee ou n'est pas de type article
            if line.refused or line.layout_type != 'article':
                # ne pas facturer cette ligne
                continue       
              
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])]})
                self.env['account.invoice.line'].create(vals)
    
    def get_number_of_days_prisme(self, date_to):
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
            res["value"]["customer_lead"] = diff_day
        return res
    
    @api.multi
    @api.depends('rel_subtotal')
    def _sub_total(self):
        res = {}
        for sol in self:

            sub_total = 0.0
            if sol.layout_type == 'subtotal' and self._is_number(sol.order_id.id):
                sub_sols = self.env['sale.order.line'].search([('order_id','=',sol.order_id.id),('sequence','<=',sol.sequence),('id','!=',sol.id)], order='sequence desc,id desc')
                for sub_sol in sub_sols:
                    if sub_sol.layout_type == 'subtotal': break
                    if sub_sol.sequence == sol.sequence and sub_sol.id > sol.id: break
                    if sub_sol.layout_type == 'article' and sub_sol.refused != True:
                        sub_total += sub_sol.price_subtotal
            
            sol.rel_subtotal = sub_total
    
    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced')
    def _compute_invoice_status(self):
        super(sale_order_line, self)._compute_invoice_status()        
        for line in self:
            # Si la ligne a ete refusee ou n'est pas de type article
            if line.refused or line.layout_type != 'article':
                # mettre la ligne en etat facture
                line.invoice_status = 'invoiced'