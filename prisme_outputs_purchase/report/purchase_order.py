from report import report_sxw
from osv import osv
import netsvc

# Change default print button report with custom prisme report
class purchase_order(osv.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"

    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the request for quotation and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'purchase.order', ids[0], 'send_rfq', cr)
        datas = {
                 'model': 'purchase.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'purchase.order.email.prisme', 'datas': datas, 'nodestroy': True}

purchase_order()
    
report_sxw.report_sxw(
        'report.purchase.order.paper.prisme',
        'purchase.order',
        rml='addons/prisme_outputs_purchase/report/purchase_order.rml',
        header=None
    )

report_sxw.report_sxw(
        'report.purchase.order.email.prisme',
        'purchase.order',
        rml='addons/prisme_outputs_purchase/report/purchase_order.rml'
    )
