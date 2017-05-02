{
'name': 'Prisme Reporting for Sales',
'version': '2017-05-02 14:38',
'category': 'Sales',
'summary': 'sale order report, quotation report',
	'author': 'Prisme Solutions Informatique SA',
	'website': 'http://www.prisme.ch',
	'depends': [
				'ons_productivity_sale_layout',
				'prisme_so_enhancement',
				'sale',
				'sale_stock',
				'crm',
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
