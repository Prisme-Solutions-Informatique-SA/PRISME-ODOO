import datetime
import tools
from osv import osv, fields
import logging


class contracts_compute_wizard(osv.TransientModel):
    _name = 'contracts.compute.wizard'
    _columns = {
		 'end': fields.date('Date',required=True),
	} 

    def getChilds(self, cr, uid, contract_id):
	res = []
        contracts = self.pool.get('account.analytic.account')
        parent = contracts.browse(cr,uid,[contract_id])[0]
        ids = contracts.search(cr,uid,[('parent_id','in',[contract_id]),('state', 'in', ['open', 'draft']),],order='id')
	res.append(contract_id)
        for child in contracts.browse(cr,uid,ids):
          res.append(child.id)
          res.extend(self.getChilds(cr,uid,child.id))
        return res

    def getAnalyticSum(self, cr, uid, contract_id,dateend):
        res = {'sale':0,'purchase':0,'timesheet':0,'advance':0,}
	childs=self.getChilds(cr,uid,contract_id)
        if childs!=[]:
          childst=(tuple(childs),dateend,)
          cr.execute('select aj.journal_type, sum(al.amount) from account_analytic_line al,account_analytic_journal aj where al.journal_id=aj.id and al.account_id  in %s and date<=%s group by aj.journal_type;', childst)
          rows = cr.fetchall()
          for row in rows:
            res[str(row[0])]=row[1]
        return res        

    def recursiveCompute(self, cr, uid, contract_id):
        res = {'stored_hours_qtt_est': 0,
               'stored_hours_quantity': 0,
               'stored_ca_to_invoice': 0,
               'stored_remaining_hours': 0,
               'stored_timesheet_ca_invoiced': 0,
               'stored_est_total':0,
               'stored_toinvoice_total':0,
               'stored_invoiced_total':0,
	       'stored_quantity_max':0,}
        contracts = self.pool.get('account.analytic.account')
        parent = contracts.browse(cr,uid,[contract_id])[0]
        ids = contracts.search(cr,uid,[('parent_id','in',[contract_id]),('state', 'in', ['open', 'draft']),],order='id')
        if ids==[]:
          worker=contracts._analysis_all(cr, uid, [contract_id], ['hours_quantity','ca_to_invoice',], None, context=None)
          res['stored_hours_qtt_est']=parent.hours_qtt_est
          res['stored_quantity_max']=parent.quantity_max
          res['stored_hours_quantity']=worker[contract_id]['hours_quantity']
          res['stored_ca_to_invoice']=worker[contract_id]['ca_to_invoice']
          res['stored_remaining_hours']=contracts._remaining_hours_calc(cr, uid, [contract_id], None, None, context=None)[contract_id]
          res['stored_timesheet_ca_invoiced']=contracts._timesheet_ca_invoiced_calc(cr, uid, [contract_id], None, None, context=None)[contract_id]
          res['stored_est_total']=contracts._get_total_estimation(parent)
          res['stored_toinvoice_total']=contracts._get_total_toinvoice(parent)
          res['stored_invoiced_total']=contracts._get_total_invoiced(parent)
        else:        
          for child in contracts.browse(cr,uid,ids):
            childres=self.recursiveCompute(cr, uid, child.id)
            res['stored_hours_qtt_est']+=childres['stored_hours_qtt_est']
            res['stored_hours_quantity']+=childres['stored_hours_quantity']
            res['stored_ca_to_invoice']+=childres['stored_ca_to_invoice']
	    res['stored_remaining_hours']+=childres['stored_remaining_hours']
            res['stored_timesheet_ca_invoiced']+=childres['stored_timesheet_ca_invoiced']
            res['stored_est_total']+=childres['stored_est_total']
            res['stored_toinvoice_total']+=childres['stored_toinvoice_total']
	    res['stored_invoiced_total']+=childres['stored_invoiced_total']
            res['stored_quantity_max']+=childres['stored_quantity_max']
        contracts.write(cr,uid,[contract_id],
            {
            'stored_hours_qtt_est': float(res['stored_hours_qtt_est']),
            'stored_hours_quantity': float(res['stored_hours_quantity']),
            'stored_ca_to_invoice': float(res['stored_ca_to_invoice']),
            'stored_remaining_hours': float(res['stored_remaining_hours']),
            'stored_timesheet_ca_invoiced': float(res['stored_timesheet_ca_invoiced']),
            'stored_est_total': float(res['stored_est_total']),
            'stored_toinvoice_total': float(res['stored_toinvoice_total']),
            'stored_invoiced_total': float(res['stored_invoiced_total']),
            'stored_quantity_max': float(res['stored_quantity_max']),})
        return res    
    
    def computedisplay(self, cr, uid, ids, \
                       context=None):
	for wiz in self.browse(cr,uid,ids): 
        	print('----------------------COMPUTE START')
        	contracts = self.pool.get('account.analytic.account')
        	ids = contracts.search(cr,uid,[('state', 'in', ['open', 'draft']),],order='id')
		for fid in ids:
        	# self.recursiveCompute(cr, uid, fid)
        	  anal=self.getAnalyticSum(cr,uid,fid,wiz.end)
        	  contracts.write(cr,uid,[fid],
        	    {
        	    'stored_sum_sale': float(anal['sale']),
        	    'stored_sum_purchase': float(anal['purchase']),
        	    'stored_sum_timesheet': float(anal['timesheet']),
        	    'stored_sum_advance': float(anal['advance']),
        	    });
        	print('----------------------COMPUTE STOP')
	return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}
	#view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'prisme_contract_type', 'view_account_analytic_account_contract_list')
	#view_id = view_ref and view_ref[1] or False,
	#view_ref2 = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'prisme_contract_type', 'account_analytic_account_contract_search')
	#view_id2 = view_ref2 and view_ref2[1] or False,
	#return {
	#      'type': 'ir.actions.act_window',
	#      'name': 'Contracts simplified views',
	#      'view_mode': 'tree',
	#      'view_type': 'tree,form',
	#      'view_id': view_id,
	#      'search_view_id':view_id2,
	#      'res_model': 'account.analytic.account',
	#      'domain' : [('state', 'in', ['open', 'draft']),],
	#      'target': 'current',
	#      'limit': 80,
	#      'auto_refresh':1,
	#      'context':context,
	#      'auto_search': True,
	#'filter': True,
	#       }
		
        
contracts_compute_wizard()
