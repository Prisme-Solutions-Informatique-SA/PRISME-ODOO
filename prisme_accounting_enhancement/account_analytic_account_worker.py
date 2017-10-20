from osv import osv, fields
import decimal_precision as dp
import netsvc 

class account_analytic_account_prisme(osv.osv):
    _name = "account.analytic.account"
    _inherit = "account.analytic.account"
    
    #Method copied from account_analytic_account._debit_credit_bal_qtty
    # and modified to care about financial accounts filters.
    # Adapt this method in case of problem with updates.
    def _calc_values(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        if context is None:
            context = {}
        child_ids = tuple(self.search(cr, uid, [('parent_id', 'child_of', ids)]))
        for i in child_ids:
            res[i] =  {}
            for n in fields:
                res[i][n] = 0.0

        if not child_ids:
            return res

        where_date = ''
        where_clause_args = [tuple(child_ids)]
        if context.get('from_date', False):
            where_date += " AND l.date >= %s"
            where_clause_args  += [context['from_date']]
        if context.get('to_date', False):
            where_date += " AND l.date <= %s"
            where_clause_args += [context['to_date']]
        
        #Modification begin
        # Modification no:   1
        # Author(s):         Damien Raemy
        # Date:              26.02.2011
        # Last modification: 26.02.2011 
        # Description:       Create an argument to the request criteria
        # But:               Does that the analytic account values are calculated
        #                    taking in consideration the financial account
        #                    filter (added by this module)

        where_financial_account = ''
        if context.get('financial_account_filter_ids'):
            #Convert a list formated as string to a standard list
            import ast; 
            fa_filter_ids = ast.literal_eval(
                                context["financial_account_filter_ids"])
            obj_fa = self.pool.get('account.account')
            fa_child_ids = tuple(obj_fa.search(cr, uid, 
                                  [('parent_id', 'child_of', fa_filter_ids)]))
            
            where_financial_account += " AND l.general_account_id in %s"
            where_clause_args += [tuple(fa_child_ids)]
        
        #Modification end
            
        #Note: the request has been kept (and not replaced with line search 
        # method to improve speed.
        cr.execute("""
              SELECT a.id,
                     sum(
                         CASE WHEN l.amount > 0
                         THEN l.amount
                         ELSE 0.0
                         END
                          ) as debit,
                     sum(
                         CASE WHEN l.amount < 0
                         THEN -l.amount
                         ELSE 0.0
                         END
                          ) as credit,
                     COALESCE(SUM(l.amount),0) AS balance,
                     COALESCE(SUM(l.unit_amount),0) AS quantity
              FROM account_analytic_account a
                  LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
              WHERE a.id IN %s
              """ + where_date
              #Modification begin
              # Modification no:   2
              # Author(s):         Damien Raemy
              # Date:              26.02.2011
              # Last modification: 26.02.2011 
              # Description:       Adds the argument created by the modification
              #                    1 to the request
              # But:               See modification 1
              
              + where_financial_account
        
              #Modification end
              + """
              
              GROUP BY a.id""", where_clause_args)
        for row in cr.dictfetchall():
            res[row['id']] = {}
            for field in fields:
                res[row['id']][field] = row[field]
        return self._compute_level_tree(cr, uid, ids, child_ids, res, fields, 
                                        context)
        
    _columns = {
        'quantity': fields.function(_calc_values, method=True,
                                    type='float', string='Quantity',
                                    multi='_calc_values'),
        'debit': fields.function(_calc_values, method=True,
                                 type='float', string='Debit',
                                 multi='_calc_values',
                                 digits_compute=dp.get_precision('Account')),
        'credit': fields.function(_calc_values, method=True,
                                  type='float', string='Credit',
                                  multi='_calc_values',
                                  digits_compute=dp.get_precision('Account')),
        'balance': fields.function(_calc_values, method=True,
                                   type='float', string='Balance',
                                   multi='_calc_values',
                                   digits_compute=dp.get_precision('Account')),
    }
                
account_analytic_account_prisme()
