from report import report_sxw
    
report_sxw.report_sxw(
        'report.purchase.order.paper.prisme',
        'purchase.order',
        rml='addons/prisme_outputs_purchase/report/purchase_order.rml',
        header=None
    )

report_sxw.report_sxw(
        'report.purchase.order.email.prisme',
        'purchase.order',
        rml='addons/prisme_outputs_purchase/report/purchase_order.rml'
    )
