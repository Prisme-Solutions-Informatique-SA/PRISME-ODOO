{
'name': 'Prisme Timesheet Invoice Cancelable',
'version': '8.0',
'category': 'Sale',
'description': """
Prisme specific developments

Allow user to cancel invoices and unlink timesheet lines,
    
For more informations:
www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
    "depends" : ["account",
                 "account_payment",
                 "account_cancel"
                ],
'init_xml': [],
    'update_xml': [
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
