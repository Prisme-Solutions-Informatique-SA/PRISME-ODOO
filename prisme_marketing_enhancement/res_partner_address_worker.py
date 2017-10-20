from osv import osv, fields

class res_partner_address_prisme(osv.osv):
    _name='res.partner.address'
    _inherit='res.partner.address'
    
    _columns = {
        'marketingauth': fields.boolean('No marketing', help="Check this box " + 
                                    'if the partner does not accept marketing'),
    }

res_partner_address_prisme()