{
'name': 'Prisme Additonal Quantities',
'version': '6.1',
'category': 'Warehouse',
'description': """
Compute and show additional data on virtual stocks

- Entering quantity
- Outgoing quantity

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': ['base','account','sale','stock',],
'init_xml': [],
'update_xml': [
    'product_view.xml',
],
'demo_xml': [],
'installable': True,
'active': False,
'images': [
           'images/qty_tree.jpg',
           'images/qty_form.jpg',
           ],
}
