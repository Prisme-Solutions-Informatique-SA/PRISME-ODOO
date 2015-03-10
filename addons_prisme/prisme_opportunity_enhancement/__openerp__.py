{
'name': 'Prisme Opportunity enhancement',
'version': '8.0',
'category': 'Sale',
'description': """
Prisme specific developments

Add print report for Opportunity:
    * Creat PDF with all need informations
    
For more informations:
www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'crm',
        'mail',      
        ],
'init_xml': [],
    'update_xml': [
        'header.xml',
        'report.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
