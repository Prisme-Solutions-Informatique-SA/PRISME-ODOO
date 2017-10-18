from odoo import api, fields, models, _


class Quant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def quants_get_preferred_domain(self, qty, move, ops=False, lot_id=False, domain=None, preferred_domain_list=[]):
        ''' @override: Override this method to allocate quants of that lot which is passed in context '''
        if self.env.context.get('expiry_lot_batch_id'):
            lot_id = self.env.context['expiry_lot_batch_id'].id
        return self.quants_get_reservation(
            qty, move,
            pack_operation_id=ops and ops.id or False,
            lot_id=lot_id,
            company_id=self.env.context.get('company_id', False),
            domain=domain,
            preferred_domain_list=preferred_domain_list)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: