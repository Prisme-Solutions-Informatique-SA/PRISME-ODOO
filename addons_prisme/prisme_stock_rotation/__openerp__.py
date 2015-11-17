
{
'name': 'Prisme Stock Rotation',
'version': '6.1',
'category': 'Warehouse',
'description': """
Create a report that compute and display the stock rotation
for the products.

The stock rotation is calculated like this:

- Average stock = (Stock at beginning of the periode + Stock at end of the period) / 2   
- Stock Rotation = Quantity of item sold / Average stock 
       
For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'stock',
            'product',
            'prisme_analytic_plans',
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
