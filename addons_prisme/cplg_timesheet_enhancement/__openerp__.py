{
'name': 'CPLG SA - timesheet enhancement',
'version': '7.0',
'category': 'Human Resources',
'description': """
CPLG SA specific developments

Add features to manage human resources:
    * Add employee field
    * Invoiceable base analytic account
    * Display customer based on analytic account
    
For more informations:
www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'hr_timesheet',
        'hr_timesheet_sheet',
        'hr_timesheet_invoice',        
        ],
'init_xml': [],
    'update_xml': [
        'view_hr_timesheet_line.xml',
        'view_account_analytic.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
