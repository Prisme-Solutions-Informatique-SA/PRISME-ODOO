{
'name': 'Prisme manufacturing tools',
'version': '6.1',
'category': 'Manufacturing',
'description': """

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'mrp',
            'mrp_operations',
            'sale_mrp',
            'report_webkit_sample',
],
'init_xml': [],
'update_xml': [
               'mrp_routing_workcenter_view.xml',
               'report/motools.xml',
               'report/motools_bis.xml',
               ],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': [
           'images/',
           ],
}