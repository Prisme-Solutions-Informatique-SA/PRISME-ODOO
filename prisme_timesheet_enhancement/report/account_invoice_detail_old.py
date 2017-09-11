import re
import time
import datetime
from openerp import addons
from openerp.report import report_sxw
from openerp.osv.osv import except_osv
from openerp.tools import mod10r
from openerp.tools.translate import _
from operator import itemgetter, attrgetter

from odoo.addons.report_webkit.models.webkit_report import webkit_report_extender
from odoo import SUPERUSER_ID

account_invoice_detail_total = 0
account_invoice_detail_amount = 0

@webkit_report_extender("prisme_timesheet_enhancement.account_invoice_detail")
def extend_account_invoice_detail(pool, cr, uid, localcontext, context):
    localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
			'pool' : pool,
            'user': pool.get("res.users").browse(cr, uid, uid),
			'getprice': getprice,
			'getSortedList': getSortedList,
			'addToTotal': addToTotal,
			'getAndResetTotal': getAndResetTotal,
			'addToAmount': addToAmount,
			'getAndResetAmount': getAndResetAmount,
			'formatDate': formatDate,
    })
	
	
def getprice(pool, cr, uid, pricelist_id, product_id, partner_id, quantity):
	context =  {'date':False,}
	price = 0
	price = pool.get('product.pricelist').price_get(cr,uid,[pricelist_id], product_id, quantity, partner=partner_id, context=context)[pricelist_id]
        return price
		
def getSortedList(cr, oid):
	cr.execute("select acc.name, ptr.name, line.date, line.name, line.unit_amount, prd.default_code, tmpl.list_price,fact.factor,fact.name,prd.id,acc.pricelist_id,acc.partner_id from hr_analytic_timesheet t,account_analytic_line line, account_analytic_account acc, res_users usr, res_partner ptr, product_product prd, product_template tmpl,hr_timesheet_invoice_factor fact where t.line_id = line.id and fact.id=line.to_invoice and prd.product_tmpl_id=tmpl.id and line.product_id=prd.id and usr.partner_id=ptr.id and line.user_id=usr.id and acc.id=line.account_id and line.move_id is null and line.invoice_id="+str(oid)+" order by date, t.time_beginning")
	res = cr.fetchall()
	sortedList = []
	sortedList = sorted(res,key=itemgetter(0,1,5,8,2))
	return sortedList
	
def addToTotal(l_total):
	global account_invoice_detail_total
	account_invoice_detail_total = account_invoice_detail_total + l_total

def getAndResetTotal():
	global account_invoice_detail_total
	act_total = account_invoice_detail_total
	account_invoice_detail_total = 0
	return act_total
	
def addToAmount(l_amount):
	global account_invoice_detail_amount
	account_invoice_detail_amount = account_invoice_detail_amount + l_amount

def getAndResetAmount():
	global account_invoice_detail_amount
	act_amount = account_invoice_detail_amount
	account_invoice_detail_amount = 0
	return act_amount
	
def formatDate(date):
	curDate = ""
	if date:
		curDate = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d. %m. %Y")
	return curDate
	
	
	
