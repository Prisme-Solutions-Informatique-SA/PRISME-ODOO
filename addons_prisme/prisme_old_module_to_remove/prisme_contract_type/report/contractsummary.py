import re
import time
from openerp import addons
from openerp.report import report_sxw
from openerp.osv.osv import except_osv
from openerp.tools import mod10r
from openerp.tools.translate import _

class ContractSummary(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ContractSummary, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'user': self.pool.get("res.users").browse(cr, uid, uid),
	    'getTimesheets': self.getTimesheets,
	    'getInvoices': self.getInvoices,
 	    'getPurchases': self.getPurchases,
        })

    def getJournalTimesheet(self):
	return self.pool.get("account.analytic.journal").search(self.cr,self.uid,[('code','ilike','TS'),])

    def getJournalInvoice(self):
        return self.pool.get("account.analytic.journal").search(self.cr,self.uid,[('code','ilike','VTE'),])

    def getJournalPurchase(self):
        return self.pool.get("account.analytic.journal").search(self.cr,self.uid,[('code','ilike','ACH'),])

    def getTimesheets(self, account_id):
        res=[]
 	aal=self.pool.get("account.analytic.line")
        ids = aal.search(self.cr,self.uid,['&',('journal_id','=',self.getJournalTimesheet()),('account_id','=',account_id),])
        for l in aal.browse(self.cr,self.uid,ids):	
		line={}
		line['name']=l.user_id.partner_id.name
		line['date']=l.date
		line['amount']=l.amount
		line['unit_amount']=l.unit_amount
		res.append(line)
        return res

    def getInvoices(self,account_id):
        res=[]
	aal=self.pool.get("account.analytic.line")
        ids = aal.search(self.cr,self.uid,['&',('journal_id','=',self.getJournalInvoice()),('account_id','=',account_id),])
        oldinvoices=[]
        for l in aal.browse(self.cr,self.uid,ids):
   		line={}
                if l.invoice_id:
                        if not(l.invoice_id.id in oldinvoices):
                        	oldinvoices.append(l.invoice_id.id)
				line['date']=l.invoice_id.date_invoice
				line['number']=l.invoice_id.number
				line['amount_total']=l.invoice_id.amount_total
				res.append(line)
        return res

    def getPurchases(self,account_id):
        res=[]
	aal=self.pool.get("account.analytic.line")
        ids = aal.search(self.cr,self.uid,['&',('journal_id','=',self.getJournalPurchase()),('account_id','=',account_id),])
	oldinvoices=[]
        for l in aal.browse(self.cr,self.uid,ids):
		line={}
         	if l.move_id:
                   if l.move_id.invoice:
                        if not(l.move_id.invoice.id in oldinvoices):
                                oldinvoices.append(l.move_id.invoice.id)
                                line['date']=l.move_id.invoice.date_invoice
				line['supplier']=l.move_id.invoice.partner_id.name
                                line['number']=l.move_id.invoice.number
				line['supplier_number']=l.move_id.invoice.supplier_invoice_number
                                line['amount_total']=l.move_id.invoice.amount_total
                                res.append(line)			
        return res


report_sxw.report_sxw('report.contracts_summary',
                      'account.analytic.account',
                      'prisme_contract_type/report/contractsummary.mako',
                      parser=ContractSummary)

