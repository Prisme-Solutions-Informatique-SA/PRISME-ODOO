
{
    'name': 'Prisme Lots Enhancement',
    'version': '1.0',
    'category': 'Inventory Control',
    'description': """
    Prisme - specific developments
    ------------------------------------------------------------------------

    Add features to manage informations about products and warranty
    thanks to the production lots.
    Add recall when warranty come to end (To use that, please configure and
    activate the scheduler named Warranty Management Scheduler)

    For more informations:
    damien.raemy@prisme.ch
    """,
    'author': 'Damien Raemy | Prisme Solutions Informatique SA',
    'website': 'http://www.prisme.ch',
    'depends': [
        'stock',
     ],
    'init_xml': [
        'init_scheduler.xml',
    ],
    'update_xml': [
        'view_stock_production_lot.xml',
        'view_prisme_warranty_warranty.xml',
        'view_prisme_warranty_type.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}