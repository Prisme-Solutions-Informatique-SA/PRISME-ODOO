from osv import osv, fields

class account_invoice_line_prisme(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
    
    _columns = {
        "page_break": fields.boolean("Page Break", 
                                     help="Add a page break before this line"),
    }
      
account_invoice_line_prisme()
