{
'name': 'Prisme Analytic Plans',
'version': '6.1',
'category': 'Finance',
'description': """
Extension of the module prisme_accounting_enhancement to use analytic plans.

- Replace the Sale Analytic Account by a Sale Analytic Distribution
- Adapt the flow SO->(Picking)->Invoice to follow this rule

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'prisme_accounting_enhancement',
            'account_analytic_plans',
			'sale_margin',
            'purchase',
],
'init_xml': [],
'update_xml': [
               'product_product_view.xml',
               'account_analytic_plan_instance_view.xml',
               'account_invoice_report_view.xml',
],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images':[
         'images/product_analytic',
         'images/invoice_analysis.jpg',
         ],
}
