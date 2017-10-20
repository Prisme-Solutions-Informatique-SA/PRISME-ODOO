from osv import osv, fields

class account_journal_prisme(osv.osv):
    _name = 'account.journal'
    _inherit = 'account.journal'

    # Method copied the 30.08.2012 (OpenERP 6.1) 
    # from addons/account/account.py line 766
    # Overriden because don't tain count if no journal currency or no account
    # currency is defined (False != 12, for example). See bug 2737.
    def _check_currency(self, cr, uid, ids, context=None):
        for journal in self.browse(cr, uid, ids, context=context):
            if journal.currency:
                if journal.default_credit_account_id and \
                        journal.currency.id and \
                        journal.default_credit_account_id.currency_id.id \
                        and not \
                        journal.default_credit_account_id.currency_id.id == \
                        journal.currency.id:
                    return False
                if journal.default_debit_account_id and \
                        journal.currency.id and \
                        journal.default_credit_account_id.currency_id.id \
                        and not \
                        journal.default_debit_account_id.currency_id.id == \
                        journal.currency.id:
                    return False
        return True

    # Overrriden to use the overriden method _check_currency. See below.
    _constraints = [
        (_check_currency, 'Configuration error! The currency chosen should be shared by the default accounts too.', ['currency','default_debit_account_id','default_credit_account_id']),
    ]

    _columns = {
                # Override the existing code field to allow to use more than
                # 5 chars in codes.
                'code': fields.char('Code', size=16, required=True, 
                help='The code will be used to generate the numbers of the ' +\
                     'journal entries of this journal.'),
    }
    
account_journal_prisme()