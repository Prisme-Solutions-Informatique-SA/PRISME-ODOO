{
    'name': "Prisme Lot Quarantine Expiry",
    'version': "2017-07-03 13:38",
    'author': "Prisme Solutions Informatique SA",
    'website': "https://www.prisme.ch",
    'category': "stock",
    'description': """
        If a batch / lot due date is overdue, the batch lot 
        will be moved to Quality management module (it is like a “quarantine” status)
        and picking will be created for quality check. 
        If quality agree for new due date, 
        batch / lot is accepted and comeback into inventory otherwise batch / lot must be scrapped.
    """,
    'depends': ['quality', 'product_expiry'],
    'data': [
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
        'data/stock_data.xml',
        'views/stock_pack_operation_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: