{
'name': 'Prisme Reporting for Sales',
'version': '2016-05-04 10:10',
'category': 'Sales',
'summary': 'sale order report, quotation report',
	'author': 'Prisme Solutions Informatique SA',
	'website': 'http://www.prisme.ch',
	'depends': [
				'ons_productivity_sale_layout',
				'prisme_so_enhancement',
				'sale',
				'sale_stock',
	],
	'data': [
				   'sale_order_view.xml',
				   'report/sale_order.xml',
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
