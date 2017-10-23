from openerp.osv import fields, osv, expression


class account_analytic_line_prisme(osv.osv):
    _name = "account.analytic.line"
    _inherit = "account.analytic.line"
    
    def search(self, cr, uid, search_args, offset=0, limit=None, order=None, \
               context=None, count=False):
        if context is None:
            context = {}
        if search_args is None:
            search_args = []
            
        if context.get("product_category_filter_id", False):
            search_args.append(("product_id.product_tmpl_id.categ_id", \
                                "child_of", \
                                context["product_category_filter_id"]))
        if context.get("financial_account_filter_ids", False):
            #Convert a list formated as string to a standard list
            import ast; 
            fa_ids = ast.literal_eval(context["financial_account_filter_ids"])
            search_args.append(("general_account_id", "child_of", fa_ids))
            
        return super(account_analytic_line_prisme, self).search(cr, uid, \
                   search_args, offset=offset, limit=limit, order=order, \
                   context=context, count=count)
    
    #Line for live debug:
    #import pdb; pdb.set_trace()
    
account_analytic_line_prisme()
