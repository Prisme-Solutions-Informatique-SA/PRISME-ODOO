from osv import osv, fields 
import netsvc
import hr_timesheet_invoice
from datetime import datetime
import openerp.addons.decimal_precision as dp
from math import fmod


class account_analytic_contract_type(osv.osv):
    _name = "account.analytic.contract.type"
    _columns = {
	'name': fields.char('Name', size=64, required=True, translate=False),
   }
    
account_analytic_contract_type()


class account_analytic_journal_type(osv.osv):
    _name = "account.analytic.journal"
    _inherit = "account.analytic.journal"
    _columns = {
        'journal_type': fields.selection([('sale','Sale'),('purchase','Purchase'),('timesheet','Timesheet'),('advance','Advance'),('other','Other'),],'Type', required=True,),
   }

account_analytic_journal_type()


class account_analytic_account_contract_type(osv.osv):
    _name = "account.analytic.account"
    _inherit =  "account.analytic.account"
    _columns = {
        'contract_type': fields.many2one('account.analytic.contract.type', 'Contract type'),
	'stored_hours_qtt_est': fields.float('Timesheets estimated',digits=(2,1)),
        'stored_hours_quantity': fields.float('Unit/Hours consumed',digits=(2,1)),
        'stored_remaining_hours': fields.float('Unit/Hours remaining',digits=(2,1)),
        'stored_timesheet_ca_invoiced': fields.float('Timesheets invoiced',digits=(2,1)),
        'stored_ca_to_invoice': fields.float('Timesheets to invoice',digits=(2,1)),
        'stored_est_total': fields.float('Estimated total',digits=(2,1)),
        'stored_toinvoice_total': fields.float('To invoice total',digits=(2,1)),
        'stored_invoiced_total': fields.float('Invoiced total',digits=(2,1)),
	'stored_quantity_max': fields.float('Unit/Hours estimated',digits=(2,1)),
        'stored_sum_sale': fields.float('Sum sale lines',digits=(2,1)),
        'stored_sum_purchase': fields.float('Sum purchase lines',digits=(2,1)),
        'stored_sum_advance': fields.float('Sum advance lines',digits=(2,1)),
        'stored_sum_timesheet': fields.float('Sum timesheet lines',digits=(2,1)),
   }

account_analytic_account_contract_type()



