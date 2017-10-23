{
'name': 'Nexan analytic',
'version': '7.0',
'category': 'Sales',
'description': """
Add features to manage analytic account

Create new analytic accout on merge of product account and sale account.

IMPORTANT:
You need to create a new property
property_nexan_analytic_model,type text, with the value Clim  
This value is replace by the customer name

Sale order analytic account must havec a selected "current" account.

For more informations:

- info@prisme.ch
- http://www.prisme.ch/openerp
""",
'author': 'Prisme Solutions Informatique SA | David Olivier',
'sequence': 10,
'website': 'http://www.prisme.ch',
'depends': [
    'prisme_accounting_enhancement',
],
'data': [
],
'js':[
],
'qweb' : [
],
'css':[
],
'demo': [
],
'test': [
],
'update_xml': [
  'view_account_analytic_account.xml',
],
'installable': True,
'application': True,
'auto_install': False,
}
