from osv import osv, fields

class sale_order_prisme(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    _columns = {
                'print_totals': fields.boolean('Print Totals',
                                              help='Show the totals on the ' + 
                                              'botom of the quotation/SO. ' + 
                                              'Used, for example, to offer 2 ' + 
                                              'choices to a customer and ' + 
                                              ' don\'t show a useless total.'),
                'print_vat': fields.boolean('Print VAT',
                                            help='Show the VAT on the bottom ' + 
                                            ' on the Quotation/SO. Warning: ' + 
                                            'you cannot print VAT if you ' + 
                                             'don\'t print the totals.'),
                
    }
    
    _defaults = {
                 'print_totals': True,
                 'print_vat': True,
                 }
    def _check_printings(self, cr, uid, ids):
        ok = True
        for sale_order in self.browse(cr, uid, ids):
            if not sale_order.print_totals:
                if sale_order.print_vat:
                    ok = False
        return ok
    
    _constraints = [
                     (_check_printings, 'You can\'t print VAT if you ' + 
                      'don\'t print totals', ['print_totals', 'print_vat']),
                    ]
      
sale_order_prisme()
