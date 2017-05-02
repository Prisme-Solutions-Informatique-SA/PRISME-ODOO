from openerp.report import report_sxw
from openerp import models, fields, api, _
from openerp import netsvc
from os.path import split

class prisme_picking_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(prisme_picking_parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            "shipping_date": self._get_shipping_date,
            "shipped_quantity": self._get_shipped_quantity,
            "back_order_quantity": self._get_back_order_quantity,
            "back_order_lines": self._get_back_order_lines,
            "serial_numbers": self._get_SNs,

            })
    

    
    def _get_shipping_date(self, picking):
        shipping_date = None
        try:
            for line in picking.move_lines:
                if line.state == "done":
                    if shipping_date:
                        if line.date > shipping_date:
                            shipping_date = line.date
                    else:
                        shipping_date = line.date
            # To improve. Remove the time part of the date
            if shipping_date:
                splitted_date = str(shipping_date).split(" ")
                shipping_date = ""
                for part in splitted_date:
                    if ":" in part:
                        break
                    shipping_date = shipping_date + part
        except Exception, e:
            nothing
        return shipping_date
    
    def _get_shipped_quantity(self, line):
        quantity = 0.0
        if line.state == "done":
            quantity = quantity + line.product_qty
        return quantity
    
    def _get_back_order_quantity(self, picking, line):
        
        quantity = 0.0
        bo_pickings = []
        bo_pickings = self._get_back_order_pickings(picking)
        bo_pickings.append(picking)
        for bo_picking in bo_pickings:
            for bo_line in bo_picking.move_lines:
                if  bo_line.procurement_id.sale_line_id.id == line.procurement_id.sale_line_id.id \
                    and not bo_line.state == "done":
                    quantity = quantity + bo_line.product_qty
        return quantity
    
    def _get_back_order_lines(self, picking):
        
        result = []
        related_pickings = self._get_back_order_pickings(picking)
        related_pickings.append(picking)
        if related_pickings:
            for related_picking in related_pickings:
                for related_line in related_picking.move_lines:
                    if not related_line.state == "done": 
                        already_managed = False
                        for picking_line in picking.move_lines:
                            if related_line.procurement_id.sale_line_id.id == \
                                picking_line.procurement_id.sale_line_id.id:
                                already_managed = True
                        if not already_managed:
                            result.append(related_line)
        return result
                            
        
    def _get_back_order_pickings(self, picking):
        related_pickings = []
        id = picking.id
        related_picking_ids = picking.env["stock.picking"].search([("backorder_id", "=", id)])
        if related_picking_ids:
            for related_picking in related_picking_ids:
                related_pickings.append(related_picking)
                
        return related_pickings
    
    def _get_SNs(self, move_line):
        sns = []
        if move_line.quant_ids:
            for quant_id in move_line.quant_ids :
                if quant_id.lot_id and not(quant_id.negative_move_id):
                    sns.append(quant_id.lot_id)
        if not sns:
            sns.append('')           
        return sns
                
        
    
report_sxw.report_sxw(
        "report.stock.picking.paper.prisme",
        "stock.picking",
        "addons/prisme_outputs_stock/report/picking.rml",
        parser=prisme_picking_parser
    )

report_sxw.report_sxw(
        "report.stock.picking.email.prisme",
        "stock.picking",
        "addons/prisme_outputs_stock/report/picking.rml",
        parser=prisme_picking_parser
    )
