
{
'name': 'Prisme Reporting for Sales',
'version': '6.1',
'category': 'Sales',
'description': """
Adds specific reports (for paper or e-mail) and features needed to these 
reports related to sales.

- Don't show discount if equals 0
- Adds an option to show or not the taxes or the totals on the output
- Misc. graphical changes

For more informations:

- info@prisme.ch
- http://www.prisme.ch
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'sale_layout',
            'prisme_so_enhancement',
],
'init_xml': [],
'update_xml': [
               'sale_order_view.xml',
               'report/sale_order.xml',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
}
