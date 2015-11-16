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

oldDate = ""
curDate = ""

@webkit_report_extender("prisme_timesheet_enhancement.hr_timesheet_sheet_check")
def extend_timesheet_sheet_check(pool, cr, uid, localcontext, context):
    localcontext.update({
        'time': time,
        'cr': cr,
        'uid': uid,
		'pool' : pool,
        'user': pool.get("res.users").browse(cr, uid, uid),
		'context': context,
		'getSortedList': getSortedList,
		'updateDate': updateDate,
		'getDate': getDate,
        })

def getSortedList(timesheet):
	oldDate = ""
	toSort=[]
	for line in timesheet:
		toSort.append(( line.partner_id.name, line.line_id.account_id.name, line.line_id.name, line.line_id.date,line.time_beginning,line.time_end, line.time_quantity, line.line_id.to_invoice.name, line.line_id.to_invoice.factor))
	  
	sortedList=sorted(toSort,key=itemgetter(3,4))
   
	return sortedList
	
def updateDate(date):
	global oldDate
	global curDate
	if oldDate!=date:
		curDate = date
		curDate = datetime.datetime.strptime(curDate, "%Y-%m-%d").strftime("%d.%m.%Y")
	else:
		curDate=""
	oldDate = date
	
	return curDate
	
def getDate():
	return curDate