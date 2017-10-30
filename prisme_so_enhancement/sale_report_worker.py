from osv import fields, osv
import tools

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
    
    # Method overriden to add the sale order and the margin of a so line
    # Old method in 6.0.2
    # def init(self, cr):
    #    tools.drop_view_if_exists(cr, 'sale_report')
    #    cr.execute("""
    #        create or replace view sale_report as (
    #            select el.*,
    #               -- (select count(1) from sale_order_line where order_id = s.id) as nbr,
    #                (select 1) as nbr,
    #                 s.date_order as date,
    #                 s.date_confirm as date_confirm,
    #                 to_char(s.date_order, 'YYYY') as year,
    #                 to_char(s.date_order, 'MM') as month,
    #                 to_char(s.date_order, 'YYYY-MM-DD') as day,
    #                 s.partner_id as partner_id,
    #                 s.user_id as user_id,
    #                 s.shop_id as shop_id,
    #                 s.company_id as company_id,
    #                 extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
    #                 s.state,
    #                 s.shipped,
    #                 s.shipped::integer as shipped_qty_1,
    #                 s.pricelist_id as pricelist_id,
    #                 s.project_id as analytic_account_id,
    #                 s.name as so_name
    #            from
    #            sale_order s,
    #                (
    #                select l.id as id,
    #                    l.product_id as product_id,
    #                    (case when u.uom_type not in ('reference') then
    #                        (select name from product_uom where uom_type='reference' and category_id=u.category_id)
    #                    else
    #                        u.name
    #                    end) as uom_name,
    #                    sum(l.product_uom_qty * u.factor) as product_uom_qty,
    #                    sum(l.product_uom_qty * l.price_unit) as price_total,
    #                    sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total,
    #                    sum(l.price_subtotal) as net_price_total,
    #                    sum(l.product_uom_qty * l.purchase_price) as purchase_total,
    #                    sum(l.margin) as margin_total,
    #                    pt.categ_id, l.order_id
    #                from
    #                 sale_order_line l ,product_uom u, product_product p, product_template pt
    #                 where u.id = l.product_uom
    #                 and pt.id = p.product_tmpl_id
    #                 and p.id = l.product_id
    #                 and l.refused <> true
    #                  group by l.id, l.order_id, l.product_id, u.name, pt.categ_id, u.uom_type, u.category_id) el
    #            where s.id = el.order_id
    #              and s.state <> 'cancel'
    #            group by el.id,
    #                el.product_id,
    #                el.uom_name,
    #                el.product_uom_qty,
    #                el.price_total,
    #                el.discount_total,
    #                el.net_price_total,
    #                el.purchase_total,
    #                el.margin_total,
    #                el.categ_id,
    #                el.order_id,
    #                s.date_order,
    #                s.date_confirm,
    #                s.partner_id,
    #                s.user_id,
    #                s.shop_id,
    #                s.company_id,
    #                s.state,
    #                s.shipped,
    #                s.pricelist_id,
    #                s.project_id,
    #                s.name
    #        )
    #    """)
        
    # Method copied the 28.08.2012 from addons/sale/report/sale_report.py
    # (sale.report.init) in OpenERP 6.1
    # overriden to add the sale order and the margin of a so line
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sale_report')
        cr.execute("""
            create or replace view sale_report as (
                select
                    min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.product_uom_qty * l.price_unit) as price_total,
                    sum((l.product_uom_qty * l.price_unit) - l.price_subtotal) as discount_total,
                    sum(l.price_subtotal) as net_price_total,
                    sum(l.product_uom_qty * l.purchase_price) as purchase_total,
                    sum(l.margin) as margin_total,
                    1 as nbr,
                    s.date_order as date,
                    s.date_confirm as date_confirm,
                    to_char(s.date_order, 'YYYY') as year,
                    to_char(s.date_order, 'MM') as month,
                    to_char(s.date_order, 'YYYY-MM-DD') as day,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.shop_id as shop_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    s.state,
                    t.categ_id as categ_id,
                    s.shipped,
                    s.shipped::integer as shipped_qty_1,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    s.name as so_name
                from
                    sale_order s
                    join sale_order_line l on (s.id=l.order_id)
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                where
                    l.refused <> true 
                    and s.state <> 'cancel'
                group by
                    l.product_id,
                    l.product_uom_qty,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.shop_id,
                    s.company_id,
                    s.state,
                    s.shipped,
                    s.pricelist_id,
                    s.project_id,
                    s.name
            )
        """)

sale_report()
