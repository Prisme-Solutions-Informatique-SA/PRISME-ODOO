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
        'stored_sum_sale_public': fields.float('Public Sum sale lines',digits=(2,1)),
        'stored_sum_purchase_public': fields.float('Public Sum purchase lines',digits=(2,1)),
        'stored_sum_advance_public': fields.float('Public Sum advance lines',digits=(2,1)),
        'stored_sum_timesheet_public': fields.float('Public Sum timesheet lines',digits=(2,1)),
	}


    def analysis_all_end(self, cr, uid, ids, fields, arg, context=None, dateend=False):
        dp = 2
        res = dict([(i, {}) for i in ids])
        parent_ids = tuple(ids) #We don't want consolidation for each of these fields because those complex computation is resource-greedy.
        accounts = self.browse(cr, uid, ids, context=context)

        for f in fields:
            if f == 'user_ids':
                cr.execute('SELECT MAX(id) FROM res_users')
                max_user = cr.fetchone()[0]
                if parent_ids:
                    cr.execute('SELECT DISTINCT("user") FROM account_analytic_analysis_summary_user ' \
                               'WHERE account_id IN %s AND unit_amount <> 0.0', (parent_ids,))
                    result = cr.fetchall()
                else:
                    result = []
                for id in ids:
                    res[id][f] = [int((id * max_user) + x[0]) for x in result]
            elif f == 'month_ids':
                if parent_ids:
                    cr.execute('SELECT DISTINCT(month_id) FROM account_analytic_analysis_summary_month ' \
                               'WHERE account_id IN %s AND unit_amount <> 0.0', (parent_ids,))
                    result = cr.fetchall()
                else:
                    result = []
                for id in ids:
                    res[id][f] = [int(id * 1000000 + int(x[0])) for x in result]
            elif f == 'last_worked_invoiced_date':
                for id in ids:
                    res[id][f] = False
                if parent_ids:
                    cr.execute("SELECT account_analytic_line.account_id, MAX(date) \
                            FROM account_analytic_line \
                            WHERE account_id IN %s \
                                AND invoice_id IS NOT NULL \
                                AND date <= %s \
                            GROUP BY account_analytic_line.account_id;", (parent_ids,dateend,))
                    for account_id, sum in cr.fetchall():
                        if account_id not in res:
                            res[account_id] = {}
                        res[account_id][f] = sum
            elif f == 'ca_to_invoice':
                for id in ids:
                    res[id][f] = 0.0
                res2 = {}
                for account in accounts:
                    cr.execute("""
                        SELECT product_id, sum(amount), user_id, to_invoice, sum(unit_amount), product_uom_id, line.name
                        FROM account_analytic_line line
                            LEFT JOIN account_analytic_journal journal ON (journal.id = line.journal_id)
                        WHERE account_id = %s
                            AND journal.type != 'purchase'
                            AND invoice_id IS NULL
                            AND to_invoice IS NOT NULL
                            AND line.date <= %s 
                        GROUP BY product_id, user_id, to_invoice, product_uom_id, line.name""", (account.id,dateend,))

                    res[account.id][f] = 0.0
                    for product_id, price, user_id, factor_id, qty, uom, line_name in cr.fetchall():
                        price = -price
                        if product_id:
                            price = self.pool.get('account.analytic.line')._get_invoice_price(cr, uid, account, product_id, user_id, qty, context)
                        factor = self.pool.get('hr_timesheet_invoice.factor').browse(cr, uid, factor_id, context=context)
                        res[account.id][f] += price * qty * (100-factor.factor or 0.0) / 100.0

                # sum both result on account_id
                for id in ids:
                    res[id][f] = round(res.get(id, {}).get(f, 0.0), dp) + round(res2.get(id, 0.0), 2)
            elif f == 'last_invoice_date':
                for id in ids:
                    res[id][f] = False
                if parent_ids:
                    cr.execute ("SELECT account_analytic_line.account_id, \
                                DATE(MAX(account_invoice.date_invoice)) \
                            FROM account_analytic_line \
                            JOIN account_invoice \
                                ON account_analytic_line.invoice_id = account_invoice.id \
                            WHERE account_analytic_line.account_id IN %s \
                                AND account_analytic_line.invoice_id IS NOT NULL \
                                AND  account_analytic_line.date <= %s \
                            GROUP BY account_analytic_line.account_id",(parent_ids,dateend,))
                    for account_id, lid in cr.fetchall():
                        res[account_id][f] = lid
            elif f == 'last_worked_date':
                for id in ids:
                    res[id][f] = False
                if parent_ids:
                    cr.execute("SELECT account_analytic_line.account_id, MAX(date) \
                            FROM account_analytic_line \
                            WHERE account_id IN %s \
                                AND invoice_id IS NULL \
                                AND date <= %s \
                            GROUP BY account_analytic_line.account_id",(parent_ids,dateend,))
                    for account_id, lwd in cr.fetchall():
                        if account_id not in res:
                            res[account_id] = {}
                        res[account_id][f] = lwd
            elif f == 'hours_qtt_non_invoiced':
                for id in ids:
                    res[id][f] = 0.0
                if parent_ids:
                    cr.execute("SELECT account_analytic_line.account_id, COALESCE(SUM(unit_amount), 0.0) \
                            FROM account_analytic_line \
                            JOIN account_analytic_journal \
                                ON account_analytic_line.journal_id = account_analytic_journal.id \
                            WHERE account_analytic_line.account_id IN %s \
                                AND account_analytic_journal.type='general' \
                                AND invoice_id IS NULL \
                                AND to_invoice IS NOT NULL \
                                AND  account_analytic_line.date <= %s \
                            GROUP BY account_analytic_line.account_id;",(parent_ids,dateend,))
                    for account_id, sua in cr.fetchall():
                        if account_id not in res:
                            res[account_id] = {}
                        res[account_id][f] = round(sua, dp)
                for id in ids:
                    res[id][f] = round(res[id][f], dp)
            elif f == 'hours_quantity':
                for id in ids:
                    res[id][f] = 0.0
                if parent_ids:
                    cr.execute("SELECT account_analytic_line.account_id, COALESCE(SUM(unit_amount), 0.0) \
                            FROM account_analytic_line \
                            JOIN account_analytic_journal \
                                ON account_analytic_line.journal_id = account_analytic_journal.id \
                            WHERE account_analytic_line.account_id IN %s \
                                AND account_analytic_journal.type='general' \
                                AND  account_analytic_line.date <= %s \
                            GROUP BY account_analytic_line.account_id",(parent_ids,dateend,))
                    ff =  cr.fetchall()
                    for account_id, hq in ff:
                        if account_id not in res:
                            res[account_id] = {}
                        res[account_id][f] = round(hq, dp)
                for id in ids:
                    res[id][f] = round(res[id][f], dp)
            elif f == 'ca_theorical':
                # TODO Take care of pricelist and purchase !
                for id in ids:
                    res[id][f] = 0.0
                # Warning
                # This computation doesn't take care of pricelist !
                # Just consider list_price
                if parent_ids:
                    cr.execute("""SELECT account_analytic_line.account_id AS account_id, \
                                COALESCE(SUM((account_analytic_line.unit_amount * pt.list_price) \
                                    - (account_analytic_line.unit_amount * pt.list_price \
                                        * hr.factor)), 0.0) AS somme
                            FROM account_analytic_line \
                            LEFT JOIN account_analytic_journal \
                                ON (account_analytic_line.journal_id = account_analytic_journal.id) \
                            JOIN product_product pp \
                                ON (account_analytic_line.product_id = pp.id) \
                            JOIN product_template pt \
                                ON (pp.product_tmpl_id = pt.id) \
                            JOIN account_analytic_account a \
                                ON (a.id=account_analytic_line.account_id) \
                            JOIN hr_timesheet_invoice_factor hr \
                                ON (hr.id=a.to_invoice) \
                        WHERE account_analytic_line.account_id IN %s \
                            AND a.to_invoice IS NOT NULL \
                            AND account_analytic_journal.type IN ('purchase', 'general')\
                            AND  account_analytic_line.date <= %s \
                        GROUP BY account_analytic_line.account_id""",(parent_ids,dateend,))
                    for account_id, sum in cr.fetchall():
                        res[account_id][f] = round(sum, dp)
        return res


    def remaining_hours_compute(self, cr, uid, quantity_max, hours_quantity):
        res = 0.0
        if quantity_max != 0:
          res = quantity_max - hours_quantity
          res = round(res,2)
        return res

    def timesheet_ca_invoiced_calc_end(self, cr, uid, ids, context=None, dateend=False):
        lines_obj = self.pool.get('account.analytic.line')
        res = {}
        inv_ids = []
        for account in self.browse(cr, uid, [ids], context=context):
            res[account.id] = 0.0
            line_ids = lines_obj.search(cr, uid, [('account_id','=', account.id), ('invoice_id','!=',False), ('to_invoice','!=', False), ('journal_id.type', '=', 'general'),('date','<=',dateend)], context=context)
            for line in lines_obj.browse(cr, uid, line_ids, context=context):
                if line.invoice_id not in inv_ids:
                    inv_ids.append(line.invoice_id)
                    res[account.id] += line.invoice_id.amount_untaxed
        return res

 
    def fix_price_to_invoice_calc_end(self, cr, uid, ids,  context=None, dateend=False):
        sale_obj = self.pool.get('sale.order')
        res = {}
        for account in self.browse(cr, uid, [ids], context=context):
            res[account.id.id] = 0.0
            sale_ids = sale_obj.search(cr, uid, [('date_confirm','<=',dateend),('project_id','=', account.id.id), ('state', '=', 'manual')], context=context)
            for sale in sale_obj.browse(cr, uid, sale_ids, context=context):
                res[account.id.id] += sale.amount_untaxed
                for invoice in sale.invoice_ids:
                    if invoice.state != 'cancel':
                        res[account.id.id] -= invoice.amount_untaxed
        return res


    def get_total_toinvoice_end(self,cr,uid,account,datend,ca_to_invoice):
        total_toinvoice = 0.0
	account_obj = self.pool.get('account.analytic.account')
	account = account_obj.browse(cr,uid,[account],context=None)[0]
        if account.fix_price_invoices:
            total_toinvoice += self.fix_price_to_invoice_calc_end(cr,uid,account,context=None, dateend=datend)[account.id]
	if account.invoice_on_timesheets:
             total_toinvoice += ca_to_invoice
        return total_toinvoice

 
    def ca_invoiced_end(self, cr, uid, ids, context=None,dateend=False):
        res = {}
        res_final = {}
        child_ids = tuple(ids) #We don't want consolidation for each of these fields because those complex computation is resource-greedy.
        for i in child_ids:
            res[i] =  0.0
        if not child_ids:
            return res

        if child_ids:
            #Search all invoice lines not in cancelled state that refer to this analytic account
            inv_line_obj = self.pool.get("account.invoice.line")
            inv_lines = inv_line_obj.search(cr, uid, ['&', ('account_analytic_id', 'in', child_ids), ('invoice_id.state', '!=', 'cancel')], context=context)
            for line in inv_line_obj.browse(cr, uid, inv_lines, context=context):
		if line.invoice_id.date_invoice<=dateend:    
                  res[line.account_analytic_id.id] += line.price_subtotal
        for acc in self.browse(cr, uid, res.keys(), context=context):
	    tci=self.timesheet_ca_invoiced_calc_end(cr,uid,acc.id,context=None, dateend=dateend)[acc.id]	
            res[acc.id] = res[acc.id] - (tci or 0.0)

        res_final = res
        return res_final

    def get_total_invoiced_end(self, cr, uid, account, datend, ca_invoiced):
        total_invoiced = 0.0
	account_obj = self.pool.get('account.analytic.account')
	account = account_obj.browse(cr,uid,[account],context=None)[0]
        if account.fix_price_invoices:
            total_invoiced += self.ca_invoiced_end(cr,uid,[account.id],context=None, dateend=datend)[account.id]
        if account.invoice_on_timesheets:
            total_invoiced += self.timesheet_ca_invoiced_calc_end(cr,uid,account.id,context=None, dateend=datend)[account.id]
        return total_invoiced

account_analytic_account_contract_type()

class account_analytic_line(osv.osv):
	_name = "account.analytic.line"
	_inherit = "account.analytic.line"
	_columns = {
			'amount_public': fields.float('Public Amount', digits=(2,1)),
			}

account_analytic_line()


