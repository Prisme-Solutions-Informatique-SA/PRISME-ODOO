
{
'name': 'Prisme Sales Order Enhancement',
'version': '6.1',
'category': 'Sales',
'description': """
Add features to manage Sales

- Delivery Date in the SO Lines
- Rounding on subtotal in SO
- Quotation validity and comment
- SO and SO lines refused
- Discounts in percent or amount
- Misc. changes in the views


For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
    'sale',
    'sale_layout',
    'sale_margin',
 ],
'init_xml': [],
'update_xml': [
    'sale_order_view.xml',
    'sale_report_view.xml',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images':[
          'images/so_rounding.jpg',
          'images/so_refused_quotation_details.jpg',
          'images/so_line_disc_refused.jpg',
          'images/so_line_delivery_date.jpg',
          'images/sale_analysis.jpg',
          ],
}