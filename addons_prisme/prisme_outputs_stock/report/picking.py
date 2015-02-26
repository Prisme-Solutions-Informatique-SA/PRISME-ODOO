from openerp.report import report_sxw
from openerp.osv import fields, osv, expression
from openerp import netsvc
from macpath import split

class prisme_picking_parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(prisme_picking_parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            "shipping_date": self._get_shipping_date,
            "shipped_quantity": self._get_shipped_quantity,
            "back_order_quantity": self._get_back_order_quantity,
            "back_order_lines": self._get_back_order_lines,

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
                if  bo_line.sale_line_id.id == line.sale_line_id.id \
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
                            if related_line.sale_line_id.id == \
                                picking_line.sale_line_id.id:
                                already_managed = True
                        if not already_managed:
                            result.append(related_line)
        return result
                            
        
    def _get_back_order_pickings(self, picking):
        related_pickings = []
        obj_picking = self.pool.get("stock.picking")
        related_picking_ids = obj_picking.search(self.cr, self.uid,
                              [("backorder_id", "=", picking.id),
                              ])
        if related_picking_ids:
            related_pickings = obj_picking.browse(self.cr, self.uid, \
                                                     related_picking_ids)
        return related_pickings
    
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
