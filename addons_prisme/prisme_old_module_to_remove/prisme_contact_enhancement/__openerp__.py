
{
'name': 'Prisme Contact Enhancement',
'version': '6.1',
'category': 'Tools',
'description': """
Add features to manage old contacts:

- Partner set to inactive state and not default visible
- Contact set to inactive state and not default visible

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
    'base',
 ],
'init_xml': [],
'update_xml': [
    'res_partner_address_view.xml',
    'res_partner_view.xml',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images':[
          'images/address.jpg',
          ],
}