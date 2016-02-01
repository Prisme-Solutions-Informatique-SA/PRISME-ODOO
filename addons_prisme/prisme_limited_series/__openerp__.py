{
'name': 'Prisme Limited Series',
'version': '6.1',
'category': 'Warehouse',
'description': """
Adds the possibility to manage production lots by limited series number. 
Example: piece 3 of 10.

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'stock',
            'stock_account',
],
'init_xml': [],
'update_xml': [
               'stock_production_lot_view.xml',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images':[
          'images/limited_series_no.jpg',
          ],
}
