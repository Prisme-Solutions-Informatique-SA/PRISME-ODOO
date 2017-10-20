from osv import fields, osv

class account_move_line_prisme(osv.osv):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    # Method copied the 30.08.2012 (OpenERP 6.1) from 
    # addons/account/account_move_line.py, line 467.
    # Not modified, but necessary to be called from the field
    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result

    _columns = {
                # Override the existing code field 
                # addons/account/account_move_line.py, line, line 492
                # to set the field not required (see bug 2736).
                'journal_id': fields.related('move_id', 'journal_id', 
                                             string='Journal', type='many2one', 
                                             relation='account.journal', 
                                             select=True, readonly=True,
                                             store = {'account.move': 
                                                      (_get_move_lines, 
                                                       ['journal_id'], 20)
                                }),
                'period_id': fields.related('move_id', 'period_id', 
                                            string='Period', type='many2one', 
                                            relation='account.period', 
                                            select=True, readonly=True,
                                            store = {'account.move': 
                                                     (_get_move_lines, 
                                                      ['period_id'], 20)
                                }), 

    }

account_move_line_prisme()        