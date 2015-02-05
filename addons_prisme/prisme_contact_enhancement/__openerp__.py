
{
    'name': 'Prisme Contact Enhancement',
    'version': '1.0',
    'category': 'Partner',
    'description': """
    Prisme - specific developments
    ------------------------------------------------------------------------

    Add features to manage old contacts:
    * Contact set to inactive state and not default visible


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
        'res_partner_address_view.xml',
        'res_partner_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}