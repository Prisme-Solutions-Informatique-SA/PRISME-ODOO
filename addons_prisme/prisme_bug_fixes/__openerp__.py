
{
    'name': 'Prisme Bugs Fix',
    'version': '1.0',
    'category': 'Tools',
    'description': """
    Prisme - OpenERP Enhancement
    ------------------------------------------------------------------------

    Correct the found bugs that pose problems.
    
    That has been created under a module form to avoid the need to correct
    each bug for each OpenERP version.
    
    Bug corrected:
    * Journal code lenght limited
    * Swiss VAT verification not implemented
    * Cost price based on product standard price in sale_margin 
      see - https://bugs.launchpad.net/openobject-addons/+bug/848867
          - Bug 2389 in hotline
    * sale_margin and sale_layout modules not compatibles
      see - https://bugs.launchpad.net/openobject-addons/+bug/808683
          - Bug 2330 in hotline
    
    For more informations:
    damien.raemy@prisme.ch
    """,
    'author': 'Damien Raemy | Prisme Solutions Informatique SA',
    'website': 'http://www.prisme.ch',
    'depends': [
        'base_vat',
        'sale_margin',
     ],
    'init_xml': [
    ],
    'update_xml': [
        'sale_order_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}