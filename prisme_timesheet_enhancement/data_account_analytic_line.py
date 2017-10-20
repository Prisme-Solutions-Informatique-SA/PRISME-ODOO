from osv import osv, fields 

class account_analytic_line_prisme(osv.osv):
    _name = "account.analytic.line" 
    _inherit = "account.analytic.line"
    
    _columns = {
                "account_partner": fields.related("account_id",
                                                  "partner_id", 
                                                  type="many2one", 
                                                  string="Partner Id", 
                                                  relation="res.partner", 
                                                  store=True),
    }

account_analytic_line_prisme()