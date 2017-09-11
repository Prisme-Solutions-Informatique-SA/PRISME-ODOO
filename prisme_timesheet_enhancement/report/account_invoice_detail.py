from odoo import models, fields, api, _
from operator import itemgetter, attrgetter
from datetime import datetime

class account_invoice_detail(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"
    
    account_invoice_detail_total = 0
    account_invoice_detail_amount = 0
    
    def getSortedList(self, oid):
        cr = self.env.cr
        cr.execute("select acc.name, ptr.name, line.date, line.name, line.unit_amount, prd.default_code, tmpl.list_price,fact.factor,fact.name,prd.id,acc.pricelist_id,acc.partner_id from account_analytic_line line, account_analytic_account acc, res_users usr, res_partner ptr, product_product prd, product_template tmpl,hr_timesheet_invoice_factor fact where fact.id=line.to_invoice and prd.product_tmpl_id=tmpl.id and line.product_id=prd.id and usr.partner_id=ptr.id and line.user_id=usr.id and acc.id=line.account_id and line.move_id is null and line.invoice_id="+str(oid)+" order by date, line.time_beginning")
        res = cr.fetchall()
        sortedList = []
        sortedList = sorted(res,key=itemgetter(0,1,5,8,2))
        
        
        for row in sortedList:
            row_list = list(row)
            row_list[2] = datetime.strptime(row_list[2], '%Y-%m-%d').strftime('%d.%m.%Y')
            row = tuple(row_list)
            
        for idx, row in enumerate(sortedList):
            row_list = list(row)
            row_list[2] = datetime.strptime(row_list[2], '%Y-%m-%d').strftime('%d.%m.%Y')
            sortedList[idx] = row_list
        return sortedList
    
    def getAndResetTotal(self):
        act_total = account_invoice_detail.account_invoice_detail_total
        account_invoice_detail.account_invoice_detail_total = 0
        return act_total
    
    def getAndResetAmount(self):
        act_amount = account_invoice_detail.account_invoice_detail_amount
        account_invoice_detail.account_invoice_detail_amount = 0
        return act_amount
    
    def getprice(self,pricelist_id, product_id, partner_id, quantity):
        #context =  {'date':False,}
        price = 0
        pl = self.env['product.pricelist'].browse(pricelist_id)
        price = pl.price_get(product_id, quantity, partner=partner_id)[pl.id]
        return price
    
    def addToTotal(self, l_total):
        account_invoice_detail.account_invoice_detail_total = account_invoice_detail.account_invoice_detail_total + l_total
        
    def addToAmount(self, l_amount):
        account_invoice_detail.account_invoice_detail_amount = account_invoice_detail.account_invoice_detail_amount + l_amount
        
    def display_address(self, address_record, without_company=False):
        # FIXME handle `without_company`
        return address_record.contact_address