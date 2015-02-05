
{
    'name': 'Prisme Marketing Enhancement',
    'version': '1.0',
    'category': 'Marketing',
    'description': """
    Prisme - specific developments
    ------------------------------------------------------------------------

    Add features to manage Sales Order:
    * Partner exclusion from mailling

    Filter example:
    [('partner_id.marketingauth','=','false')]
    
    For more informations:
    david.olivier@prisme.ch
    """,
    'author': 'David Olivier | Prisme Solutions Informatique SA',
    'website': 'http://www.prisme.ch',
    'depends': [
        'base',
     ],
    'init_xml': [],
    'update_xml': [
        'res_partner_view.xml',
        'res_partner_address_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}