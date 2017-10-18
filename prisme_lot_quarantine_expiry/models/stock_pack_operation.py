from odoo import api, fields, models, _


class PackOperationLot(models.Model):
    '''To assign use_date and removal_date to lot while creating or selecting
        lot for pack_operation_product_ids
    '''
    _inherit = "stock.pack.operation.lot"

    use_date = fields.Datetime(string='Best before Date',
        help='This is the date on which the goods with this Serial Number start deteriorating, without being dangerous yet.')
    removal_date = fields.Datetime(string='Removal Date',
        help='This is the date on which the goods with this Serial Number may become dangerous and must not be consumed.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
