from openerp.osv import osv


class ResCurrency(osv.Model):

    _inherit = "account.journal"
"""
    def exchange(self, cr, uid, ids, from_amount, to_currency_id,
                 from_currency_id, exchange_date, context=None):
        
        Exchange an amount between the two currencies. Return the amount
        with the conversion.
        @param from_amount: the amount where the exchange will be done.
        @param to_currency_id: id of the currency to be convert.
        @param from_currency_id: id of the currency from the amount will be
        convert.
        @param exchange_date: date were the exchange will be done, this date
        will indicate the conversio rate to use.
        
        context = context or {}
        context = dict(context)
        if from_currency_id == to_currency_id:
            return from_amount
        context['date'] = exchange_date
        return self.compute(cr, uid, from_currency_id, to_currency_id,
                            from_amount, context=context)
"""