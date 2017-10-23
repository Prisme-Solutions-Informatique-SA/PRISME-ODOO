from osv import osv, fields 
import netsvc

class sale_order_line_prisme(osv.osv):
    _name = 'sale.order.line' 
    _inherit = 'sale.order.line'

    #Modification de la creation d une facture depuis un bl
    def invoice_line_create(self, cr, uid, ids, context=None):
        #Appel de la methode original
        res = super(sale_order_line_prisme, self).invoice_line_create(cr,\
                    uid, ids, context)
        # Setting the analytic account from the product or from the line
        obj_line = self.pool.get('account.invoice.line')
        for line_id in res:
            line = obj_line.browse(cr, uid, line_id)
            product_id = line.product_id.id
            if product_id:
                product = self.pool.get('product.product').browse(cr, uid,\
                              product_id, context=context)
                prod_analytic_acc = product.sale_analytic_account_id
                if prod_analytic_acc:
                    #If product account present, merging with sale_account
                    order = self.browse(cr, uid, ids[0]).order_id
                    aid=prod_analytic_acc.merge_account(prod_analytic_acc.id,order.project_id)
                    if aid:
                        obj_line.write(cr, uid, line_id,\
                        {'account_analytic_id': aid})
                    else:
                        obj_line.write(cr, uid, line_id,\
                        {'account_analytic_id': None})


            
        # Discount type recovery
        obj_inv_line = self.pool.get('account.invoice.line')
        for so_line in self.browse(cr, uid, ids, context=context):
            for inv_line in so_line.invoice_lines:
                obj_inv_line.write(cr, uid, inv_line.id,\
                                   {'discount_type': so_line.discount_type})
        
        return res

sale_order_line_prisme()
