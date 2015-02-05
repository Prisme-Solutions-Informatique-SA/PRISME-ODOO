from osv import osv

class res_partner_prisme(osv.osv):
    _inherit = 'res.partner'

    # Corrige le fait que la verification du no de TVA Suisse n'est pas gere.
    # Annule juste les erreurs. Ne verifie pas les donnees.
    def check_vat_ch(self, vat):
        return True
    
res_partner_prisme()