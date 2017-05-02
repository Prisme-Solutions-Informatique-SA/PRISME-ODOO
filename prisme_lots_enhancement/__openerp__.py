
{
'name': 'Prisme Lots Enhancement',
'version': '2017-03-08 10:32',
'category': 'Warehouse',
'summary': 'warranties, extra fields',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
    'stock',
    'account_voucher',
 ],
'init_xml': [
    'init_scheduler.xml',
],
'update_xml': [
    'view_stock_production_lot.xml',
    'view_prisme_warranty_warranty.xml',
    'view_prisme_warranty_type.xml',
    'security/ir.model.access.csv',
	'view_stock_transfer_details.xml',
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