import re
import time
import datetime
from openerp import addons
from openerp.report import report_sxw
from openerp.osv.osv import except_osv
from openerp.tools import mod10r
from openerp.tools.translate import _
from operator import itemgetter, attrgetter

from openerp.addons.report_webkit.webkit_report import webkit_report_extender
from openerp import SUPERUSER_ID

old = ["", ""]
client = None
project = None

@webkit_report_extender("prisme_timesheet_enhancement.hr_analytic_timesheet_check")
def extend_analytic_timesheet_check(pool, cr, uid, localcontext, context):
    localcontext.update({
        'time': time,
        'cr': cr,
        'uid': uid,
		'pool' : pool,
        'user': pool.get("res.users").browse(cr, uid, uid),
		'context': context,
		'getSortedList': getSortedList,
		'updateClAPr': updateClAPr,
		'getClient': getClient,
		'getProject': getProject,
		'getFormattedDate': getFormattedDate,
        })

def getSortedList(objects):
	global old
	old = ["", ""]
	
	toSort=[]
	for o in objects:
		toSort.append(( o.partner_id.name, o.account_id.name, o.line_id.name, o.date, o.time_beginning, o.time_end,o.time_quantity,o.line_id.to_invoice.name, o.line_id.to_invoice.factor, o.line_id.user_id.partner_id.name  ))
	  
	sortedList=sorted(toSort,key=itemgetter(0,1,3,4))
   
	return sortedList
	
def updateClAPr(actT):
	global client, old, project
	if actT[0] == old[0]:
		client = ""
	else :
		client = actT[0]
		old[0] = actT[0]
	if actT[1] == old[1]:
		project = ""
	else:
		project = actT[1]
		old[1] = actT[1]
		
def getClient():
	return client

def getProject():
	return project

def getFormattedDate(date):
	return datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")