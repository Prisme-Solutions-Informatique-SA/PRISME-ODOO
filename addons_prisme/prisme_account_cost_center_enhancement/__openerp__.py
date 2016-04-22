{
    'name': 'Prisme account_cost_center enhancement',
    'summary': """improve account_cost_center to add cost center for Entries Analysis""",
    'description': """
Costcenter
================================================================
This module adds possibility to group and filter by cost center in Entries Analysis
    """,
    'depends': [
        'account',
        'account_accountant',
        'account_cost_center',
    ],
    'author': "Prisme Solutions Informatique SA",
    'website': 'http://www.prisme.ch',
    'category': 'Accounting',
    'version': '1.1',
    'data': [
        'account_entries_report_prisme.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
