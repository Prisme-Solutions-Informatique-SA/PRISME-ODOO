# -*- coding: utf-8 -*-
##############################################################################
#
#    Loic Baechler
#    Prisme Solution Informatique SA
#    5 nov 2015
#
##############################################################################

from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp.osv import fields, osv
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _
import pytz
from openerp import SUPERUSER_ID


class stock_move(osv.osv):
    _inherit = 'stock.move'

    # Cette methode est appele lors de la creation d une facture depuis une commande de vente
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        if inv_type in ('out_invoice', 'out_refund') and move.procurement_id and move.procurement_id.sale_line_id:
            sale_line = move.procurement_id.sale_line_id
            res['discount_type'] = sale_line.discount_type
        return res
