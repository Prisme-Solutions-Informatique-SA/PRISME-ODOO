
{
'name': 'Prisme Marketing Enhancement',
'version': '8.0',
'category': 'Sales',
'description': """
Add features to manage marketing:

- Partner exclusion from mailling

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
    'res_partner_view.xml',
    #'res_partner_address_view.xml',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': [
           'images/partner_no_marketing.jpg',
           ],
}