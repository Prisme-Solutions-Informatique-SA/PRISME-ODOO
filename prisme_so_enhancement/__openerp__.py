
{
'name': 'Prisme Sales Order Enhancement',
'version': '2017-05-02 14:43',
'category': 'Sales',
'summary': 'ammount discount, rounding on subtotal, partial refusal',
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