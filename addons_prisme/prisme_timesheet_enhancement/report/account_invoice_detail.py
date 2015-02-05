import re
import time
from openerp import addons
from openerp.report import report_sxw
from openerp.osv.osv import except_osv
from openerp.tools import mod10r
from openerp.tools.translate import _


class AccountInvoiceDetails(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(AccountInvoiceDetails, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'user': self.pool.get("res.users").browse(cr, uid, uid),
            'getprice': self.getprice,
        })

    def getprice(self, pricelist_id, product_id, partner_id, quantity):
	context =  {'date':False,}
	price = 0
	price = self.pool.get('product.pricelist').price_get(self.cr,self.uid,[pricelist_id], product_id, quantity, partner=partner_id, context=context)[pricelist_id]
        return price


report_sxw.report_sxw('report.account_invoice_detail',
                      'account.invoice',
                      'prisme_timesheet_enhancement/report/templates/account_invoice_detail.mako',
                      parser=AccountInvoiceDetails)

