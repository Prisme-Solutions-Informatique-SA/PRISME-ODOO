from openerp import models, fields, api, _
from openerp import netsvc
from openerp.osv.orm import browse_record_list, browse_record, browse_null
from openerp.tools.translate import _

class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    prescriber = fields.Many2one('res.partner', 'Prescriber', store=True)

