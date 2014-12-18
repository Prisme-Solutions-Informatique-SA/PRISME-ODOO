{
'name': 'Prisme Reporting for Accounting',
'version': '7.0',
'category': 'Finance',
'description': """
Adds specific reports (for paper or e-mail) and features needed to these reports related to accounting.

- Show the VAT number of the company in header
- Don't show the partner phone number, fax and VAT in the address
- Change the header informations
- Don't show discount if equals 0
- Misc. graphical changes.


For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA',
'website': 'http://www.prisme.ch',
'depends': [
            'ons_productivity_sale_layout',
],
'init_xml': [],
'update_xml': [
               'account_invoice_line_view.xml',
               'report/invoice.xml',
               ],
'demo_xml': [],
'test': [],
'installable': True,
'active': False,
'images': [
           'images/invoice_report.jpg',
           ],
}
