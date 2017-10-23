{
'name': 'Prisme Reporting for Sales',
'version': '7.0',
'category': 'Sales',
'description': """
Adds specific reports (for paper or e-mail) and features needed to these 
reports related to sales.

- Don't show discount if equals 0
- Adds an option to show or not the taxes or the totals on the output
- Misc. graphical changes

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
	'author': 'Prisme Solutions Informatique SA',
	'website': 'http://www.prisme.ch',
	'depends': [
				'ons_productivity_sale_layout',
				'prisme_so_enhancement',
				'sale',
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
