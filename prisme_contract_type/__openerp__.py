{
'name': 'Prisme Solutions Informatique SA - contract type',
'version': '7.0',
'category': 'Human Resources',
'description': """
Prisme Solutions Informatique SA specific developments

Add features to contract management:
    * Add contract type management in sales
    * Add contract simplified view in sales
    * Add journal analytic type (to define purchase,timesheet,advance,sale)
    * Add compute to date contract fields
    	- Analytical purchase sum internal price
	- Analytical purchase sum public price (invoice price if exist)
	- Analytical advance sum internal price
	- Analytical advance sum public price (invoice price if exist)
	- Analytical timesheet sum internal price 
	- Analytical timesheet sum public price (invoice price if exist)
	- Analytical sale sum internal price
	- Analytical sale sum public price (invoice price if exist)
	- Prepaid service: unit/hours estimated
	- Unit/hours consumed
	- Unit/hours to invoice
	- Timesheet estimated
	- Timesheet invoiced
	- Timesheet to invoiced
	- Contract total estimated
	- Contract total invoiced
	- Contract total to invoice
     * Add public price to Cost and Gain view in contract
    
For more informations:
David Olivier
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
