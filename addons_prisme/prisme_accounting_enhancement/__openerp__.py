
{
"name": "Prisme Accounting Enhancement",
"version": "2016-05-23 16:30",
"category": "Finance",
'summary' : "amount discount, rounding subtotal",
"author": "Prisme Solutions Informatique SA",
"website": "http://www.prisme.ch",
"depends": [
    "analytic",
    "product",
    "sale",
    "stock",
    "account_payment",
    "prisme_so_enhancement",
 ],
"init_xml": [],
"update_xml": [
    "account_analytic_chart_view.xml",
    "account_invoice_view.xml",
    "account_invoice_line_view.xml",
    "account_account_view.xml",
    "account_analytic_account_view.xml",
],
"demo_xml": [],
"test": [],
"installable": True,
"active": False,
"images": [
           "images/product_analytic_acc.jpg",
           "images/chart_analytic_acc_filter.jpg",
           "images/invoice_line_disc_type.jpg",
           "images/invoice_rounding.jpg",
           ],
}
