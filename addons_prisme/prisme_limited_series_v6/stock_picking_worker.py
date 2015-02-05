from osv import osv, fields
import netsvc

class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    # Method overriden to add the serial no and limited serie no in
    # the description of the invoice line.
    # TODO Adapt, see below
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cr, \
                    uid, ids, journal_id, group, type, context)
        obj_invoice_line = self.pool.get('account.invoice.line')
        for picking in self.browse(cr, uid, ids):
            if picking.type == 'out': 
                for move_line in picking.move_lines:
                    if move_line.sale_line_id:
                        for inv_line in move_line.sale_line_id.invoice_lines:
                            obj_invoice_line.write(cr, uid, inv_line.id, \
                                        {'note': move_line.sale_line_id.notes})
                    
                    if move_line.prodlot_id:
                        lot = move_line.prodlot_id
                        lot_descr = lot.name
                        
                        if lot.limited_series_no:
                            lot_descr += '\n(' + lot.limited_series_no
                            
                            if lot.limited_series_of:
                                lot_descr += ' / ' + lot.limited_series_of
     
                            lot_descr += ')'
                            
                        if move_line.sale_line_id:
                            for inv_line in move_line.sale_line_id.invoice_lines:
                                old_note = inv_line.note
                                if not old_note:
                                    old_note = ''
                                new_note = old_note + '\n' + lot_descr
                                obj_invoice_line.write(cr, uid, inv_line.id, \
                                                       {'note': new_note})
                
        return res
    
# TODO Adapt this method for 6.1
    # Method copied from addons/stock/stock.py
    # Modified the 11.02.2013 by Damien Raemy to put lot number and limited 
    # serie number in description
    def action_invoice_create_V602(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        address_obj = self.pool.get('res.partner.address')
        invoices_group = {}
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.invoice_state != '2binvoiced':
                continue
            payment_term_id = False
            partner =  picking.address_id and picking.address_id.partner_id
            if not partner:
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)

            if inv_type in ('out_invoice', 'out_refund'):
                account_id = partner.property_account_receivable.id
                payment_term_id = self._get_payment_term(cr, uid, picking)
            else:
                account_id = partner.property_account_payable.id

            address_contact_id, address_invoice_id = \
                    self._get_address_invoice(cr, uid, picking).values()
            address = address_obj.browse(cr, uid, address_contact_id, context=context)

            comment = self._get_comment_invoice(cr, uid, picking)
            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals = {
                    'name': (invoice.name or '') + ', ' + (picking.name or ''),
                    'origin': (invoice.origin or '') + ', ' + (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
                    'comment': (comment and (invoice.comment and invoice.comment+"\n"+comment or comment)) or (invoice.comment and invoice.comment or ''),
                    'date_invoice':context.get('date_inv',False),
                    'user_id':uid
                }
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals, context=context)
            else:
                invoice_vals = {
                    'name': picking.name,
                    'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
                    'type': inv_type,
                    'account_id': account_id,
                    'partner_id': address.partner_id.id,
                    'address_invoice_id': address_invoice_id,
                    'address_contact_id': address_contact_id,
                    'comment': comment,
                    'payment_term': payment_term_id,
                    'fiscal_position': partner.property_account_position.id,
                    'date_invoice': context.get('date_inv',False),
                    'company_id': picking.company_id.id,
                    'user_id':uid
                }
                cur_id = self.get_currency_id(cr, uid, picking)
                if cur_id:
                    invoice_vals['currency_id'] = cur_id
                if journal_id:
                    invoice_vals['journal_id'] = journal_id
                invoice_id = invoice_obj.create(cr, uid, invoice_vals,
                        context=context)
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                origin = move_line.picking_id.name or ''
                if move_line.picking_id.origin:
                    origin += ':' + move_line.picking_id.origin
                if group:
                    name = (picking.name or '') + '-' + move_line.name
                else:
                    name = move_line.name

                if inv_type in ('out_invoice', 'out_refund'):
                    account_id = move_line.product_id.product_tmpl_id.\
                            property_account_income.id
                    if not account_id:
                        account_id = move_line.product_id.categ_id.\
                                property_account_income_categ.id
                else:
                    account_id = move_line.product_id.product_tmpl_id.\
                            property_account_expense.id
                    if not account_id:
                        account_id = move_line.product_id.categ_id.\
                                property_account_expense_categ.id

                price_unit = self._get_price_unit_invoice(cr, uid,
                        move_line, inv_type)
                discount = self._get_discount_invoice(cr, uid, move_line)
                tax_ids = self._get_taxes_invoice(cr, uid, move_line, inv_type)
                account_analytic_id = self._get_account_analytic_invoice(cr, uid, picking, move_line)

                #set UoS if it's a sale and the picking doesn't have one
                uos_id = move_line.product_uos and move_line.product_uos.id or False
                if not uos_id and inv_type in ('out_invoice', 'out_refund'):
                    uos_id = move_line.product_uom.id
                account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, partner.property_account_position, account_id)
                
                # Modification begin
                # Modified the 11.02.2013 by Damien Raemy to add the production lot name and limited serie numero in note.
                
                note = "" 
                if move_line.sale_line_id:
                    note = move_line.sale_line_id.notes
                    if isinstance(note,bool):
                        note=""
                    
                if move_line.prodlot_id:
                    lot = move_line.prodlot_id
                    lot_descr = '\n' + lot.name
                        
                    if lot.limited_series_no:
                        lot_descr += '\n(' + lot.limited_series_no
                            
                        if lot.limited_series_of:
                            lot_descr += ' / ' + lot.limited_series_of
     
                        lot_descr += ')'
                    note += lot_descr
                
                # Modification end
                
                invoice_line_id = invoice_line_obj.create(cr, uid, {
                    'name': name,
                    'origin': origin,
                    'invoice_id': invoice_id,
                    'uos_id': uos_id,
                    'product_id': move_line.product_id.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'discount': discount,
                    'quantity': move_line.product_uos_qty or move_line.product_qty,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'account_analytic_id': account_analytic_id,
                    # Modification begin
                    # Modified the 11.02.2013 by Damien Raemy to add the production lot name and limited serie numero in note.
                    'note': note,
                    # Modification end
                }, context=context)
                self._invoice_line_hook(cr, uid, move_line, invoice_line_id)

            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    set_total=(inv_type in ('in_invoice', 'in_refund')))
            self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            self._invoice_hook(cr, uid, picking, invoice_id)
        self.write(cr, uid, res.keys(), {
            'invoice_state': 'invoiced',
            }, context=context)
        return res


stock_picking()
