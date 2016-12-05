
{
'name': 'Prisme Reporting for Stock',
'version': '2016-05-20 16:24',
'category': 'Warehouse',
'summary': 'stock picking report, stock picking list',
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'stock',
            'sale_stock',
            'purchase',
],
'init_xml': [],
'update_xml': [
               'view/stock_picking.xml',
               'report/picking.xml',            
], 
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': [
           'image/picking_report.jpg',
           ],
}
