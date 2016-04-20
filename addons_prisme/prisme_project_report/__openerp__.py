{
'name': 'Prisme Project Report',
'version': '8.0',
'category': 'Project',
'description': """
Prisme specific developments

Add print report for Project:
    * Creat PDF with all need informations
    
For more informations:
www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
        'project',
        'mail',
        'purchase',
        'sale',
        'prisme_po_enhancement',
        'prisme_so_enhancement',   
        ],
'init_xml': [],
    'update_xml': [
        'report.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
