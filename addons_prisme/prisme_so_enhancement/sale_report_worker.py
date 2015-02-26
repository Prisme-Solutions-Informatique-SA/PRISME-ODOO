from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.osv import fields, osv, expression
import openerp.addons.decimal_precision as dp

class sale_report(osv.osv):
    _name = 'sale.report'
    _inherit = 'sale.report'

    def _compute_discount(self, cr, uid, ids, field_name, arg, context=None):
        import pdb; pdb.set_trace()
        res = {}
        
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.total_price - line.net_price_total
        
        return res
    
    _columns = {
                'so_name': fields.char('Sale Order', 255, readonly=True),
                'discount_total': fields.float('Total Discount', digits=(16, 2)),
                'net_price_total': fields.float('Total Price (Net)', digits=(16, 2)),
                'purchase_total': fields.float('Total Purchase', digits=(16, 2)),
                'margin_total': fields.float('Total Margin', digits=(16, 2)),
                }

    def _select(self):
        select_str = """
             SELECT min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.product_uom_qty * l.price_unit * (100.0-l.discount) / 100.0) as price_total,
                    sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total,
                    sum(l.price_subtotal) as net_price_total,
                    sum(l.product_uom_qty * l.purchase_price) as purchase_total,
                    sum(l.margin) as margin_total,
                    1 as nbr,                  
                    s.date_order as date,
                    s.date_confirm as date_confirm,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    s.state,
                    t.categ_id as categ_id,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    s.section_id as section_id

        """
        return select_str

    def _from(self):
        from_str = """
                sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.company_id,
                    s.state,
                    s.pricelist_id,
                    s.project_id,
                    s.section_id,
                    s.name
        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
           
    # def _select(self):
    #     select_str = """
    #          SELECT min(l.id) as id,
    #                 l.product_id as product_id,
    #                 t.uom_id as product_uom,
    #                 sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
    #                 sum(l.product_uom_qty * l.price_unit * (100.0-l.discount) / 100.0) as price_total,
    #                 sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total,
    #                 sum(l.price_subtotal) as net_price_total,
    #                 sum(l.product_uom_qty * l.purchase_price) as purchase_total,
    #                 sum(l.margin) as margin_total,
    #                 count(*) as nbr,
    #                 s.date_order as date,
    #                 s.date_confirm as date_confirm,
    #                 s.partner_id as partner_id,
    #                 s.user_id as user_id,
    #                 s.shop_id as shop_id,
    #                 s.company_id as company_id,
    #                 extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
    #                 s.state,
    #                 t.categ_id as categ_id,
    #                 s.pricelist_id as pricelist_id,
    #                 s.project_id as analytic_account_id,
    #                 s.section_id as section_id,
    #                 s.name as so_name

    #     """
    #     return select_str

    # def _from(self):
    #     from_str = """
    #               sale_order s
    #                 join sale_order_line l on (s.id=l.order_id)
    #                     left join product_product p on (l.product_id=p.id)
    #                         left join product_template t on (p.product_tmpl_id=t.id)
    #                 left join product_uom u on (u.id=l.product_uom)
    #                 left join product_uom u2 on (u2.id=t.uom_id)


    #     """
    #     return from_str

    # def _group_by(self):
    #     group_by_str = """
    #         GROUP BY l.product_id,
    #                 l.order_id,
    #                 t.uom_id,
    #                 t.categ_id,
    #                 s.date_order,
    #                 s.date_confirm,
    #                 s.partner_id,
    #                 s.user_id,
    #                 s.company_id,
    #                 s.state,
    #                 s.pricelist_id,
    #                 s.project_id,
    #                 s.section_id,
    #                 s.name
    #     """
    #     return group_by_str

    # def init(self, cr):
    #     # self._table = sale_report
    #     tools.drop_view_if_exists(cr, self._table)
    #     cr.execute("""CREATE or REPLACE VIEW %s as (
    #         %s
    #         FROM ( %s )
    #         %s
    #         )""" % (self._table, self._select(), self._from(), self._group_by()))


sale_report()
