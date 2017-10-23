{
'name': 'Prisme Reporting for Purchases',
'version': '7.0',
'category': 'Purchases',
'description': """
Adds specific reports (for paper or e-mail) and features needed to these reports related to purchases.

- Sorting PO lines
- PO lines page break
- Delivery terms on PO
- Misc. graphical changes

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'sequence': 150,
'website': 'http://www.prisme.ch',
'depends': [
            'purchase',
],
'init_xml': [],
'update_xml': [
               'purchase_order_view.xml',
               'purchase_order_line_view.xml',
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
