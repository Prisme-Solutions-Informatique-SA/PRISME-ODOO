
{
'name': 'Prisme Stock Rotation',
'version': '2016-05-17 11:26',
'category': 'Warehouse',
'summary': 'stock period analysis, stock rotation, stock average',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'stock',
            'product',
            'account_analytic_plans',
],
'init_xml': [],
'update_xml': [
               'stock_rotation_wizard_prisme_view.xml',
               'product_product_stock_rotation_view.xml',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': [
           'images/period.jpg',
           'images/stock_rotation.jpg',
           ],
}
