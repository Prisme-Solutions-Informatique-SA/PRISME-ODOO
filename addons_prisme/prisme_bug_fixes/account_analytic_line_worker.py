from osv import osv, fields
import time


class account_analytic_line_prisme(osv.osv):
    _name = 'account.analytic.line'
    _inherit = 'account.analytic.line'



    # Method copied the 30.08.2012 (OpenERP 6.1) from 
    # addons/hr_timesheet_invoice/wizard/hr_timesheet_final_invoice_create.py
    # to correct how the product is set on the invoice line created (must take
    # the product of the employee if no product to force to use is set.
    # See bug 2731
    def invoice_cost_create(self, cr, uid, ids, data={}, context=None):
        analytic_account_obj = self.pool.get('account.analytic.account')
        res_partner_obj = self.pool.get('res.partner')
        account_payment_term_obj = self.pool.get('account.payment.term')
        invoice_obj = self.pool.get('account.invoice')
        product_obj = self.pool.get('product.product')
        invoice_factor_obj = self.pool.get('hr_timesheet_invoice.factor')
        pro_price_obj = self.pool.get('product.pricelist')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        product_uom_obj = self.pool.get('product.uom')
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoices = []
        if context is None:
            context = {}

        account_ids = {}
        for line in self.pool.get('account.analytic.line').browse(cr, uid, ids, context=context):
            account_ids[line.account_id.id] = True

        account_ids = account_ids.keys() #data['accounts']
        for account in analytic_account_obj.browse(cr, uid, account_ids, context=context):
            partner = account.partner_id
            if (not partner) or not (account.pricelist_id):
                raise osv.except_osv(_('Analytic Account incomplete'),
                        _('Please fill in the Partner or Customer and Sale Pricelist fields in the Analytic Account:\n%s') % (account.name,))

            if not partner.address:
                raise osv.except_osv(_('Partner incomplete'),
                        _('Please fill in the Address field in the Partner: %s.') % (partner.name,))

            date_due = False
            if partner.property_payment_term:
                pterm_list= account_payment_term_obj.compute(cr, uid,
                        partner.property_payment_term.id, value=1,
                        date_ref=time.strftime('%Y-%m-%d'))
                if pterm_list:
                    pterm_list = [line[0] for line in pterm_list]
                    pterm_list.sort()
                    date_due = pterm_list[-1]

            curr_invoice = {
                'name': time.strftime('%d/%m/%Y')+' - '+account.name,
                'partner_id': account.partner_id.id,
                'address_contact_id': res_partner_obj.address_get(cr, uid,
                    [account.partner_id.id], adr_pref=['contact'])['contact'],
                'address_invoice_id': res_partner_obj.address_get(cr, uid,
                    [account.partner_id.id], adr_pref=['invoice'])['invoice'],
                'payment_term': partner.property_payment_term.id or False,
                'account_id': partner.property_account_receivable.id,
                'currency_id': account.pricelist_id.currency_id.id,
                'date_due': date_due,
                'fiscal_position': account.partner_id.property_account_position.id
            }
            last_invoice = invoice_obj.create(cr, uid, curr_invoice, context=context)
            invoices.append(last_invoice)

            context2 = context.copy()
            context2['lang'] = partner.lang
            cr.execute("SELECT product_id, to_invoice, sum(unit_amount), product_uom_id " \
                    "FROM account_analytic_line as line " \
                    "WHERE account_id = %s " \
                        "AND id IN %s AND to_invoice IS NOT NULL " \
                    "GROUP BY product_id,to_invoice,product_uom_id", (account.id, tuple(ids),))

            for product_id, factor_id, qty, uom in cr.fetchall():
                product = product_obj.browse(cr, uid, product_id, context2)
                if not product:
                    raise osv.except_osv(_('Error'), _('At least one line has no product !'))
                factor_name = ''
                factor = invoice_factor_obj.browse(cr, uid, factor_id, context2)
                if not data.get('product', False):
                    if factor.customer_name:
                        factor_name = product.name+' - '+factor.customer_name
                    else:
                        factor_name = product.name
                else:
                    data['product'] = data['product'][0]
                    factor_name = product_obj.name_get(cr, uid, [data['product']], context=context)[0][1]

                ctx =  context.copy()
                ctx.update({'uom':uom})
                if account.pricelist_id:
                    pl = account.pricelist_id.id
                    price = pro_price_obj.price_get(cr,uid,[pl], data.get('product', False) or product_id, qty or 1.0, account.partner_id.id, context=ctx)[pl]
                else:
                    price = 0.0

                taxes = product.taxes_id
                tax = fiscal_pos_obj.map_tax(cr, uid, account.partner_id.property_account_position, taxes)
                account_id = product.product_tmpl_id.property_account_income.id or product.categ_id.property_account_income_categ.id
                if not account_id:
                    raise osv.except_osv(_("Configuration Error"), _("No income account defined for product '%s'") % product.name)
                curr_line = {
                    'price_unit': price,
                    'quantity': qty,
                    'discount':factor.factor,
                    'invoice_line_tax_id': [(6,0,tax )],
                    'invoice_id': last_invoice,
                    'name': factor_name,
                    # Modification begin.
                    # If data['product'] is set to False (always, never not set)
                    # must use the product_id.
                    # Original line:
                    # 'product_id': data.get('product',product_id),
                     'product_id': data['product'] or product_id,
                    #Modification end
                    'invoice_line_tax_id': [(6,0,tax)],
                    'uos_id': uom,
                    'account_id': account_id,
                    'account_analytic_id': account.id,
                }

                #
                # Compute for lines
                #
                cr.execute("SELECT * FROM account_analytic_line WHERE account_id = %s and id IN %s AND product_id=%s and to_invoice=%s ORDER BY account_analytic_line.date", (account.id, tuple(ids), product_id, factor_id))

                line_ids = cr.dictfetchall()
                note = []
                for line in line_ids:
                    # set invoice_line_note
                    details = []
                    if data.get('date', False):
                        details.append(line['date'])
                    if data.get('time', False):
                        if line['product_uom_id']:
                            details.append("%s %s" % (line['unit_amount'], product_uom_obj.browse(cr, uid, [line['product_uom_id']],context2)[0].name))
                        else:
                            details.append("%s" % (line['unit_amount'], ))
                    if data.get('name', False):
                        details.append(line['name'])
                    note.append(u' - '.join(map(lambda x: unicode(x) or '',details)))

                curr_line['note'] = "\n".join(map(lambda x: unicode(x) or '',note))
                invoice_line_obj.create(cr, uid, curr_line, context=context)
                cr.execute("update account_analytic_line set invoice_id=%s WHERE account_id = %s and id IN %s", (last_invoice, account.id, tuple(ids)))

            invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
        return invoices
    
account_analytic_line_prisme()