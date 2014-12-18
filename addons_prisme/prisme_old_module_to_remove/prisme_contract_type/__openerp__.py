{
'name': 'Prisme Solutions Informatique SA - contract type',
'version': '7.0',
'category': 'Human Resources',
'description': """
Prisme Solutions Informatique SA specific developments

Add features to stock management:
    * Add contract type
    
For more informations:
www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'account',
        'account_analytic_analysis',
        ],
'init_xml': [],
'update_xml': [
	'view_contract_type.xml',
	'report/report.xml',
    ],
'js': [
	'static/src/js/contracts.js',
	],
'qweb' : [
	"static/src/xml/contracts.xml",
	],
'css':[
	'static/src/css/contracts.css',
	],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
