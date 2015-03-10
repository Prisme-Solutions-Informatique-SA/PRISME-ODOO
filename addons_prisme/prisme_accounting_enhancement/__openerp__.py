
{
"name": "Prisme Accounting Enhancement",
"version": "8.0",
"category": "Finance",
"description": """
Add features to manage financial/analytic accounting:

- Add the possibility to set an analytic account directly on a product
- Add a filter to select only the line corresponding to some financial accounts.
- Add the possibility to select a discount in percent or in amount
- Add the possiblity to round subtotals

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
"author": "Prisme Solutions Informatique SA",
"website": "http://www.prisme.ch",
"depends": [
    "analytic",
    "product",
    "sale",
    "prisme_so_enhancement",
 ],
"init_xml": [],
"update_xml": [
    "product_product_view.xml",
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
