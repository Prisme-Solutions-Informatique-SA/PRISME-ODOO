
{
"name": "Prisme Accounting Enhancement",
"version": "2018-03-08 15:00",
"category": "Finance",
'summary' : "amount discount, rounding subtotal",
"author": "Prisme Solutions Informatique SA",
"website": "http://www.prisme.ch",
"depends": [
    "analytic",
    "product",
    "sale",
    "stock",
    "account_accountant",
    "prisme_so_enhancement",
    "account_analytic_default"
 ],
"init_xml": [],
"update_xml": [
    "migration.sql",
    "account_invoice_view.xml",
    "account_invoice_line_view.xml",
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
