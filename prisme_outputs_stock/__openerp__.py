
{
'name': 'Prisme Reporting for Stock',
'version': '6.1',
'category': 'Warehouse',
'description': """
Adds specific reports (for paper or e-mail) and features needed to these 
reports related to stock management.

- Transporter on picking
- Modifying header informations
- Shipped quantity / back-office
- Remarks
- Misc. graphical changes

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'stock',
],
'init_xml': [],
'update_xml': [
               'stock_picking_view.xml',
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
