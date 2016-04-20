
{
'name': 'Prisme Lots Enhancement',
'version': '6.1',
'category': 'Warehouse',
'description': """
Add features to track products

- Add features to manage informations about products and warranties thanks to the production lots.
- Add recall e-mails when warranty come to end.

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
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
'images':[
          'images/lot_inventory.jpg',
          'images/lot_warranty.jpg',
          ],
}