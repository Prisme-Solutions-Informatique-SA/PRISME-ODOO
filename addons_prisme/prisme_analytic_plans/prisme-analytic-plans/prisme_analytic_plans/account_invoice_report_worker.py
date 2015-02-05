import tools
from osv import fields, osv

class account_invoice_report(osv.osv):
    _name = 'account.invoice.report'
    _inherit = 'account.invoice.report'
    
    _columns = {
                'analytic_distribution': fields.many2one('account.analytic.plan.instance', 'Analytic Distribution', readonly=True),
                'cost_price': fields.float('Cost Price', readonly=True),
    }
    
    # Method copied from addons/account/report/account_invoice_report.py 
    # to add columns
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_invoice_report')
        cr.execute("""        
CREATE OR REPLACE VIEW account_invoice_report AS (
 SELECT min(ail.id) AS id, ai.date_invoice AS date, to_char(ai.date_invoice::timestamp with time zone, 'YYYY'::text) AS year, to_char(ai.date_invoice::timestamp with time zone, 'MM'::text) AS month, to_char(ai.date_invoice::timestamp with time zone, 'YYYY-MM-DD'::text) AS day, ail.product_id, ai.partner_id, ai.payment_term, ai.period_id, 
        CASE
            WHEN u.uom_type::text <> 'reference'::text THEN ( SELECT product_uom.name
               FROM product_uom
              WHERE product_uom.uom_type::text = 'reference'::text AND product_uom.active AND product_uom.category_id = u.category_id
             LIMIT 1)
            ELSE u.name
        END AS uom_name, ai.currency_id, ai.journal_id, ai.fiscal_position, ai.user_id, ai.company_id, count(ail.*) AS nbr, ai.type, ai.state, pt.categ_id, ai.date_due, ai.address_contact_id, ai.address_invoice_id, ai.account_id, ai.partner_bank_id, sum(
        CASE
            WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ail.quantity / u.factor::double precision * (-1)::double precision
            ELSE ail.quantity / u.factor::double precision
        END) AS product_qty, sum(
        CASE
            WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ai.amount_total * (-1)::numeric
            ELSE ai.amount_total
        END) / 
        CASE
            WHEN (( SELECT count(l.id) AS count
               FROM account_invoice_line l
          LEFT JOIN account_invoice a ON a.id = l.invoice_id
         WHERE a.id = ai.id)) <> 0 THEN ( SELECT count(l.id) AS count
               FROM account_invoice_line l
          LEFT JOIN account_invoice a ON a.id = l.invoice_id
         WHERE a.id = ai.id)
            ELSE 1::bigint
        END::numeric / cr.rate AS price_total_tax, 
        CASE
            WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN sum(ail.quantity * ail.price_unit::double precision * (-1)::double precision)
            ELSE sum(ail.quantity * ail.price_unit::double precision)
        END / 
        CASE
            WHEN 
            CASE
                WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN sum(ail.quantity / u.factor::double precision * (-1)::double precision)
                ELSE sum(ail.quantity / u.factor::double precision)
            END <> 0::double precision THEN 
            CASE
                WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN sum(ail.quantity / u.factor::double precision * (-1)::double precision)
                ELSE sum(ail.quantity / u.factor::double precision)
            END
            ELSE 1::double precision
        END / cr.rate::double precision AS price_average, cr.rate AS currency_rate, sum(( SELECT date_part('epoch'::text, avg(date_trunc('day'::text, aml.date_created::timestamp with time zone) - date_trunc('day'::text, l.create_date)::timestamp with time zone)) / (24 * 60 * 60)::numeric(16,2)::double precision
           FROM account_move_line aml
      LEFT JOIN account_invoice a ON a.move_id = aml.move_id
   LEFT JOIN account_invoice_line l ON a.id = l.invoice_id
  WHERE a.id = ai.id)) AS delay_to_pay, sum(( SELECT date_part('epoch'::text, avg(date_trunc('day'::text, a.date_due::timestamp with time zone) - date_trunc('day'::text, a.date_invoice::timestamp with time zone))) / (24 * 60 * 60)::numeric(16,2)::double precision
           FROM account_move_line aml
      LEFT JOIN account_invoice a ON a.move_id = aml.move_id
   LEFT JOIN account_invoice_line l ON a.id = l.invoice_id
  WHERE a.id = ai.id)) AS due_delay, 
        CASE
            WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ai.residual * (-1)::numeric
            ELSE ai.residual
        END / 
        CASE
            WHEN (( SELECT count(l.id) AS count
               FROM account_invoice_line l
          LEFT JOIN account_invoice a ON a.id = l.invoice_id
         WHERE a.id = ai.id)) <> 0 THEN ( SELECT count(l.id) AS count
               FROM account_invoice_line l
          LEFT JOIN account_invoice a ON a.id = l.invoice_id
         WHERE a.id = ai.id)
            ELSE 1::bigint
        END::numeric / cr.rate AS residual, ail.analytics_id AS analytic_distribution, sum(
        CASE
    WHEN tax.price_include::boolean = TRUE THEN
    CASE
            WHEN ail.discount_type::text = 'amount'::text THEN 
            CASE
                WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ail.quantity * ((ail.price_unit - ail.discount)*(1/(1+tax.amount)))::double precision * (-1)::double precision
                ELSE ail.quantity * (ail.price_unit - ail.discount)*(1/(1+tax.amount))::double precision
            END
            WHEN ail.discount_type::text = 'percent'::text THEN 
            CASE
                WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ail.quantity * ((ail.price_unit * ((100::numeric - ail.discount) / 100.0))*(1/(1+tax.amount)))::double precision * (-1)::double precision
                ELSE ail.quantity * (ail.price_unit * ((100::numeric - ail.discount) / 100.0)*(1/(1+tax.amount)))::double precision
            END
            ELSE 
            CASE
                WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ail.quantity * (ail.price_unit*(1/(1+tax.amount)))::double precision * (-1)::double precision
                ELSE (ail.quantity * ail.price_unit)*(1/(1+tax.amount))::double precision
            END
    END
    ELSE
        CASE
            WHEN ail.discount_type::text = 'amount'::text THEN 
            CASE
                WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ail.quantity * (ail.price_unit - ail.discount)::double precision * (-1)::double precision
                ELSE ail.quantity * (ail.price_unit - ail.discount)::double precision
            END
            WHEN ail.discount_type::text = 'percent'::text THEN 
            CASE
                WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ail.quantity * (ail.price_unit * ((100::numeric - ail.discount) / 100.0))::double precision * (-1)::double precision
                ELSE ail.quantity * (ail.price_unit * ((100::numeric - ail.discount) / 100.0))::double precision
            END
            ELSE 
            CASE
                WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text]) THEN ail.quantity * ail.price_unit::double precision * (-1)::double precision
                ELSE ail.quantity * ail.price_unit::double precision
            END
        END
        END) AS price_total
   FROM account_invoice_line ail
   LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
   LEFT JOIN product_template pt ON pt.id = ail.product_id
   LEFT JOIN account_invoice_line_tax ailt ON ailt.invoice_line_id = ail.id
   LEFT JOIN account_tax tax ON tax.id = ailt.tax_id
   LEFT JOIN product_uom u ON u.id = ail.uos_id, res_currency_rate cr
  WHERE (cr.id IN ( SELECT cr2.id
   FROM res_currency_rate cr2
  WHERE cr2.currency_id = ai.currency_id AND (ai.date_invoice IS NOT NULL AND cr.name <= ai.date_invoice OR ai.date_invoice IS NULL AND cr.name <= now())
 LIMIT 1))
  GROUP BY ail.product_id, ai.date_invoice, ai.id, cr.rate, to_char(ai.date_invoice::timestamp with time zone, 'YYYY'::text), to_char(ai.date_invoice::timestamp with time zone, 'MM'::text), to_char(ai.date_invoice::timestamp with time zone, 'YYYY-MM-DD'::text), ai.partner_id, ai.payment_term, ai.period_id, u.name, ai.currency_id, ai.journal_id, ai.fiscal_position, ai.user_id, ai.company_id, ai.type, ai.state, pt.categ_id, ai.date_due, ai.address_contact_id, ai.address_invoice_id, ai.account_id, ai.partner_bank_id, ai.residual, ai.amount_total, u.uom_type, u.category_id, ail.analytics_id

  )
        """)
account_invoice_report()
