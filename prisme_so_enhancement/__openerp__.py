
{
'name': 'Prisme Sales Order Enhancement',
'version': '7.0',
'category': 'Sales',
'description': """
Add features to manage Sales

- Delivery Date in the SO Lines
- Rounding on subtotal in SO
- Quotation validity and comment
- SO and SO lines refused
- Discounts in percent or amount
- Misc. changes in the views


For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
    'sale',
	'ons_productivity_sale_layout',
    'sale_margin',
 ],
'data': [
    'sale_report_view.xml',
    'sale_order_view.xml',
],
	'js': [
	],
	'qweb' : [
	],
	'css':[
	],
	'demo': [
	],
	'test': [
	],
	'installable': True,
	'application': True,
	'auto_install': False,
}