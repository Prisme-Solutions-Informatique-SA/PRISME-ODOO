# -*- coding: utf-8 -*-
{
    'name': 'Reporting for Client Invoice with QR-bill',
    'version': '2017-09-28',
    'category': 'Accounting & Finance',
    'summary': """QR-bill for payment slips in Switzerland""",
    'description'  : """
Adds a QRCode to invoice with IBAN BIC Information according to https://www.paymentstandards.ch/en/home/schemes/payment-slips.html
""",
    'author': 'Prisme Solutions Informatique SA',
    'website': 'https://www.prisme.ch',
    'depends': [
        'account',
        'l10n_ch_payment_slip'
    ],
    'external_dependencies' : {
        'python' : [
            'png', # png is the import of pypng
            'pyqrcode'
        ]
    },
    'data': [
        'views/report_invoice.xml',
        'views/account_invoice.xml',
        'views/reports.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
