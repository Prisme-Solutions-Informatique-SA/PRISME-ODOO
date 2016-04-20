from openerp import netsvc
from openerp.osv import fields, osv, expression


class stock_picking_prisme(osv.osv):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    # Methode appelee lorsqu'on cree une facture depuis un picking
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        # Appel de la methode originale (faite par OpenERP) et recuperation
        # du resultat
        res = super(stock_picking_prisme, self).action_invoice_create(cr, \
                    uid, ids, journal_id, group, type, context)
        # Creation d'objets correspondants aux objets factures et ligne de 
        # facutre
        obj_invoice = self.pool.get('account.invoice')
        obj_line = self.pool.get('account.invoice.line')
        # Pour chaque ligne du resultat (chaque facture creee par la methode
        # originale
        for inv in self.pool.get('account.invoice').browse(cr, uid, res, context=context):
            if inv.type == 'out_invoice':
                for ol in inv.invoice_line:
                    # Recuperation de l'id du produit de la ligne
                    product_id = ol.product_id.id
                    # Si le produit est definit
                    if product_id:
                        # Recuperation du produit depuis son ID
                        product = self.pool.get('product.product').browse(cr, 
                                                    uid, product_id)
                        # Recuperation du compte analytique du produit
                        prod_analytic_acc = product.sale_analytic_account_id
                        # Si le compte analytique est definit
                        if prod_analytic_acc:
                            # Mise a jour de la ligne de la facture (avec son
                            # ID) pour avoir le compte analytique correspondant
                            # au compte analytique du produit
                            obj_line.write(cr, uid, line.id,\
                                {'account_analytic_id': prod_analytic_acc.id})                            
        # Discount type from sale order line to invoice line
        #obj_invoice_line = self.pool.get('account.invoice.line')
        #for picking in self.browse(cr, uid, ids):
         #   for move in picking.move_lines:
          #      if move.sale_line_id:
           #         discount_type = move.sale_line_id.discount_type
            #        for inv_line in move.sale_line_id.invoice_lines:
             #           obj_invoice_line.write(cr, uid, inv_line.id,\
              #                                 {'discount_type': discount_type})
                
        return res
    
stock_picking_prisme()
