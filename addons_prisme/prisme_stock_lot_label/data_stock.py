from osv import osv, fields 
import netsvc
import hr_timesheet_invoice
from datetime import datetime
import openerp.addons.decimal_precision as dp
from math import fmod
from dateutil.relativedelta import relativedelta
import time


class stock_production_lot_cplg(osv.osv):
    _name = "stock.production.lot"
    _inherit = "stock.production.lot"
    _columns = {
        'no_lot': fields.char('No Lot', size=64, required=False, translate=False),
        'no_lot_supplier': fields.char('No Lot Supplier', size=64, required=False, translate=False),
	'createdate':fields.datetime('Creation Date', readonly=True, select=True),
	'entry_stock':fields.many2one('stock.location', 'Entry stock', required=False, select=True),
   }
    _defaults = {
        'createdate': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

stock_production_lot_cplg()


class stock_picking_cplg(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"

    def action_move(self, cr, uid, ids, context=None):
        result = super(stock_picking_cplg,self).action_move(cr, uid, ids, context)
        toPrint=True
        if context==None:
            context={}
            toPrint=False
        for pick in self.browse(cr, uid, ids, context=context):
            supplier_stock=False
	    location_pool=self.pool.get('stock.location')
            supplier_stock=location_pool.search(cr, uid,[('usage', 'ilike', 'supplier'),])[0]
            lots=[]
            lotsmin=[]
            for move in pick.move_lines:
              entry_stock=False
              if move.location_id.id==supplier_stock:
              	if move.location_dest_id:
                    entry_stock=move.location_dest_id.id 
              	if move.prodlot_id:
                    self.pool.get('stock.production.lot').write(cr,uid,[move.prodlot_id.id],{'entry_stock': entry_stock,})
                if move.prodlot_id:
                    if not(move.prodlot_id.id in lots):
                       if move.prodlot_id.product_id.label_print_type=="min":
                         lotsmin.append(move.prodlot_id.id)
                       else:
                         lots.append(move.prodlot_id.id)
            for lot in lots:
              if toPrint:
                 property_obj = self.pool.get('ir.property')
                 climid = property_obj.search(cr, uid, [('name','ilike','property_serial_report_id')])
                 if not climid:
                   raise osv.except_osv(_('Error!'), _('property_serial_report_id not exist'))
                 resul = property_obj.read(cr,uid,climid,['value_text'])
                 clim = resul[0]['value_text']
                 if str(clim)=="":
                   raise osv.except_osv(_('Error!'), _('property_serial_report_id is blank'))
                 report_action_id = int(clim)
                 context['report_action_id'] = report_action_id
                 print_actions_obj = self.pool.get('aeroo.print_actions')
                 printer = print_actions_obj._get_default_printer(cr, uid, context)
                 print_actions_obj.report_to_printer(cr, uid,[lot], report_action_id, printer, context=context)
            for lot in lotsmin:
              if toPrint:
                 property_obj = self.pool.get('ir.property')
                 climid = property_obj.search(cr, uid, [('name','ilike','property_serial_min_report_id')])
                 if not climid:
                   raise osv.except_osv(_('Error!'), _('property_serial_min_report_id not exist'))
                 resul = property_obj.read(cr,uid,climid,['value_text'])
                 clim = resul[0]['value_text']
                 if str(clim)=="":
                   raise osv.except_osv(_('Error!'), _('property_serial_min_report_id is blank'))
                 report_action_id = int(clim)
                 context['report_action_id'] = report_action_id
                 print_actions_obj = self.pool.get('aeroo.print_actions')
                 printer = print_actions_obj._get_default_printer(cr, uid, context)
                 print_actions_obj.report_to_printer(cr, uid,[lot], report_action_id, printer, context=context)

        return result

stock_picking_cplg()

