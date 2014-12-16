from osv import osv, fields 
import netsvc
import hr_timesheet_invoice
from datetime import datetime
import openerp.addons.decimal_precision as dp
from math import fmod


class stock_move_cplg(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
   }
    
stock_move_cplg()

class stock_production_lot_cplg(osv.osv):
    _name = "stock.production.lot"
    _inherit = "stock.production.lot"
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
   }

stock_production_lot_cplg()


class stock_picking_cplg(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee',required=True),
   }


    def action_move(self, cr, uid, ids, context=None):
        result = super(stock_picking_cplg,self).action_move(cr, uid, ids, context)
        """Process the Stock Moves of the Picking
        This method is called by the workflow by the activity "move".
        Normally that happens when the signal button_done is received (button
        "Done" pressed on a Picking view).
        @return: True
        """
        for pick in self.browse(cr, uid, ids, context=context):
            linked = pick.partner_id.id
            employee=False
            if pick.employee_id:
                employee=pick.employee_id.id
            for move in pick.move_lines:
              self.pool.get('stock.move').write(cr,uid,[move.id],{'employee_id': employee,})
              if move.prodlot_id:
                    self.pool.get('stock.production.lot').write(cr,uid,[move.prodlot_id.id],{'employee_id': employee,})
        return result

stock_picking_cplg()

class stock_picking_in_cplg(osv.osv):
    _name = "stock.picking.in"
    _inherit = "stock.picking.in"
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee',required=True),
   }

stock_picking_in_cplg()

class stock_picking_out_cplg(osv.osv):
    _name = "stock.picking.out"
    _inherit = "stock.picking.out"
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
   }

stock_picking_out_cplg()



