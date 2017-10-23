from osv import osv, fields
import decimal_precision as dp

class res_partner_prisme(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'marketingauth': fields.boolean('No marketing', help="Check this box if the partner does not accept marketing"),
    }
res_partner_prisme()
