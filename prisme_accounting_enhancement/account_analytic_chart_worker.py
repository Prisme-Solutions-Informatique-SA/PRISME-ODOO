from osv import osv, fields

class prisme_account_analytic_chart(osv.osv_memory):
    _name = "account.analytic.chart"
    _inherit = "account.analytic.chart"
    
    _columns = {
                "product_category_filter": fields.many2one("product.category",
                    string="Product Category Filter",
                    help="Use this filter to obtain" + \
                          " quantities and amounts calculated" + \
                          " on analytic lines concerning only some" + \
                          " kind of products."),
                "financial_account_filter": fields.many2many("account.account",
                    "rel_account_analytic_chart", "chart_id", "account_id",
                    string="Financial Account",
                    help="Use this filter to obtain quantities and amounts" +\
                    " calculated only on analytic lines concerning " + \
                    " certain accounts. Used to avoid the double hours count" +\
                    " on projects (one for the hour worked, and one for the " +\
                    " hour invoiced."),
    }
    
    def analytic_account_chart_open_window(self, cr, uid, ids, context=None):
        result = super(prisme_account_analytic_chart,\
                       self).analytic_account_chart_open_window(cr, uid, ids,\
                                                                context)
        this = self.browse(cr, uid, ids, context)[0]
        product_category_filter = this.product_category_filter
        financial_account_filter = this.financial_account_filter
        result_context = result["context"]
        
        # Result_context is a dictionnary that has been converted to a string
        # This method convert the string to a dictionnary back. 
        import ast; 
        result_context = ast.literal_eval(result_context)

        if product_category_filter:
            result_context.update({"product_category_filter_id": \
                                   product_category_filter.id})
        if financial_account_filter:
            account_ids = []
            for account in financial_account_filter:
                account_ids.append(account.id)
            result_context.update({"financial_account_filter_ids": \
                                   str(account_ids)})
        result.update({"context": str(result_context)})
        return result
    
    #Line for live debugging:
    #import pdb; pdb.set_trace()
    
prisme_account_analytic_chart()