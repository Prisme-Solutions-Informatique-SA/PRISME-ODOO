from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby
#test3
from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import logging

class stock_location_prisme(osv.osv):
  _name = "stock.location"
  _inherit = "stock.location"
  
  def _product_value(self, cr, uid, ids, field_names, arg, context=None):
        """Computes stock value (real and virtual) for a product, as well as stock qty (real and virtual).
        @param field_names: Name of field
        @return: Dictionary of values
        """
        prod_id = context and context.get('product_id', False)
       
        product_product_obj = self.pool.get('product.product')

        cr.execute('select distinct product_id, location_id from stock_move where location_id in %s', (tuple(ids), ))
        dict1 = cr.dictfetchall()
        cr.execute('select distinct product_id, location_dest_id as location_id from stock_move where location_dest_id in %s', (tuple(ids), ))
        dict2 = cr.dictfetchall()
        res_products_by_location = sorted(dict1+dict2, key=itemgetter('location_id'))
        products_by_location = dict((k, [v['product_id'] for v in itr]) for k, itr in groupby(res_products_by_location, itemgetter('location_id')))

        result = dict([(i, {}.fromkeys(field_names, 0.0)) for i in ids])
        result.update(dict([(i, {}.fromkeys(field_names, 0.0)) for i in list(set([aaa['location_id'] for aaa in res_products_by_location]))]))

        currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
        currency_obj = self.pool.get('res.currency')
        currency = currency_obj.browse(cr, uid, currency_id, context=context)
        for loc_id, product_ids in products_by_location.items():
            if prod_id:
                product_ids = [prod_id]
            c = (context or {}).copy()
            c['location'] = loc_id
            for prod in product_product_obj.browse(cr, uid, product_ids, context=c):
                for f in field_names:
                    if f == 'stock_real':
                        if loc_id not in result:
                            result[loc_id] = {}
                        result[loc_id][f] += prod.qty_available
                    elif f == 'stock_virtual':
                        result[loc_id][f] += prod.virtual_available
                    elif f == 'stock_real_value':
                        amount = prod.qty_available * prod.standard_price
                        amount = currency_obj.round(cr, uid, currency, amount)
                        result[loc_id][f] += amount
                    elif f == 'stock_virtual_value':
                        amount = prod.virtual_available * prod.standard_price
                        amount = currency_obj.round(cr, uid, currency, amount)
                        result[loc_id][f] += amount
                    elif f == 'stock_incoming':
                        result[loc_id][f] += prod.incoming_qty
                    elif f == 'stock_outgoing':
                        result[loc_id][f] += prod.outgoing_qty
        return result

# Old V6 beta    
#  def _product_value(self, cr, uid, ids, field_names, arg, context=None):
#        """Computes stock value (real and virtual) for a product, as well as stock qty (real and virtual).
#        @param field_names: Name of field
#        @return: Dictionary of values
#        """
#       
#        product_product_obj = self.pool.get('product.product')
#
#        cr.execute('select distinct product_id, location_id from stock_move where location_id in %s or location_dest_id in %s', (tuple(ids), tuple(ids)))
#        res_products_by_location = sorted(cr.dictfetchall(), key=itemgetter('location_id'))
#        products_by_location = dict((k, [v['product_id'] for v in itr]) for k, itr in groupby(res_products_by_location, itemgetter('location_id')))
#
#        result = dict([(i, {}.fromkeys(field_names, 0.0)) for i in ids])
#        result.update(dict([(i, {}.fromkeys(field_names, 0.0)) for i in list(set([aaa['location_id'] for aaa in res_products_by_location]))]))
#
#        currency_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
#        currency_obj = self.pool.get('res.currency')
#        currency = self.pool.get('res.currency').browse(cr, uid, currency_id)
#        currency_obj.round(cr, uid, currency, 300)
#        for loc_id, product_ids in products_by_location.items():
#            c = (context or {}).copy()
#            c['location'] = loc_id
#            for prod in product_product_obj.browse(cr, uid, product_ids, context=c):
#                for f in field_names:
#                    if f == 'stock_real':
#                        if loc_id not in result:
#                            result[loc_id] = {}
#                        result[loc_id][f] += prod.qty_available
#                    elif f == 'stock_virtual':
#                        result[loc_id][f] += prod.virtual_available
#                    elif f == 'stock_real_value':
#                        amount = prod.qty_available * prod.standard_price
#                        amount = currency_obj.round(cr, uid, currency, amount)
#                        result[loc_id][f] += amount
#                    elif f == 'stock_virtual_value':
#                        amount = prod.virtual_available * prod.standard_price
#                        amount = currency_obj.round(cr, uid, currency, amount)
#                        result[loc_id][f] += amount
#                    elif f == 'stock_incoming':
#                        result[loc_id][f] += prod.incoming_qty
#                    elif f == 'stock_outgoing':
#                        result[loc_id][f] += prod.outgoing_qty
#        return result

  _columns = {
	'stock_incoming': fields.function(_product_value, method=True, type='float', string='Virtual IN', multi="stock"),
	'stock_outgoing': fields.function(_product_value, method=True, type='float', string='Virtual OUT', multi="stock"),
  }
stock_location_prisme()
