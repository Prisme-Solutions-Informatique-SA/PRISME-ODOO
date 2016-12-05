{
'name': 'Prisme Reporting for Purchases',
'version': '2016-05-19 14:18',
'category': 'Purchases',
'summary': 'purchase order report, PO, report, sequence',
'author': 'Prisme Solutions Informatique SA',
'sequence': 150,
'website': 'http://www.prisme.ch',
'depends': [
            'purchase',
],
'init_xml': [],
'update_xml': [
               'purchase_order_view.xml',
               'report/purchase_order.xml',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': [
           'images/purchase_order.jpg',
           'po_line.jpg',
           ],
}
