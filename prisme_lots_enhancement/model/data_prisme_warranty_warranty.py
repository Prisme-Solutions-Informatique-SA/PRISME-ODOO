# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2020 Prisme Solutions Informatique SA <http://prisme.ch>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#    You should have received a copy of the GNU Affero General Public Lic
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Project ID :    OERP-006-02
#    Phabricator :   T515
#
##########################################################################
import datetime
import logging
from . import prisme_file_logger
from odoo import fields, models, api

_logger = logging.getLogger('prisme_lots_enhancement')

class prisme_warranty_warranty(models.Model):
    _name = 'prisme.warranty.warranty'
    _description = 'prisme warranty'
    

    description = fields.Text('Description')
    
    assigned_by = fields.Many2one('res.partner', string='Assigned By')
    assigned_to =fields.Many2one('res.partner', string='Assigned To')
    copy_to = fields.Many2one('res.partner', string='Copy To')
    warranty_type_id = fields.Many2one('prisme.warranty.type', string='Type')
    state = fields.Selection([('active', 'Active'), ('cur_ren_suppl',
                                    'Current Renewal (Suppl.)'),
                                   ('cur_ren_cust',
                                    'Current Renewal (Cust.)'),
                                   ('closed', 'Closed')],
                                    'State', required=True)
                                    
    last_suppl_invoice = fields.Many2one('account.move',
                                string='Last Supplier Invoice',
                                domain="[('type','=','in_invoice')]")
                                
    last_cust_invoice = fields.Many2one('account.move',
                                string='Last Customer Invoice',
                                domain="[('type','=','out_invoice')]")
                                
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    recall_date = fields.Date('Reminder Date')
        
    internal_notes = fields.Text('Internal Notes')
    contact_notes = fields.Text('Notes for Contact')
        
    lot_id = fields.Many2one('stock.production.lot', ondelete='cascade',
                                string="Production Lot", required=True)
                                # required=True: /!\ Warning /!\
                                # When creating from a new lot, this field won't be filled until the new lot is saved, which will block the warranty save.
                                
    partner = fields.Many2one('res.partner', string='Partner',readonly=True)
    
    # Launched each minute, this scheduled action write the date and hour
    # into a file to allow to view if the vm is on
    def log_vm_on(self, automatic=False, use_new_cursor=False, \
                  context=None):
        import time
        current_date = time.strftime('%d.%m.%Y', time.localtime())
        current_time = time.strftime('%H:%M:%S', time.localtime())
        
        self._debug('Writing date in vm_on')
        
        logger = prisme_file_logger.prisme_file_logger(
                    '/var/log/prisme/vm_on-warranty/', 7)
        logger.log(current_date + ', ' + current_time + ' : ON')
    
    def scheduled_action(self, automatic=False, use_new_cursor=False,):
        import time
        self._log('Running scheduler (' + \
                  time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()) + ')')
        self._debug("Warranties scanning called by a trigger")
        self._check_warranty_dates()
        self._log('End of scheduler run.')
        self._log('\n')
     
    def _check_warranty_dates(self):
        self._log('')
        self._log('Scanning warranties from [' + self._cr.dbname + ']')
        warranties = self.search([("state", "!=", "closed")])
        for warranty in warranties:
            self._log('-------------------------------------------------------')
            self._log('Scanning warranty from lot [' + warranty.lot_id.name + ']')
            if warranty.recall_date:
                recall_date = warranty.recall_date
        
                # If reminder date has expired
                if  recall_date <= datetime.date.today():
                    self._log('Warranty reminder date from lot [' + \
                              warranty.lot_id.name + '] has expired.')
                    
                    # If warranty is in state of being renewed
                    if warranty.state == "cur_ren_suppl" or\
                        warranty.state == "cur_ren_cust": 
                        self._log('Warranty is currently being renewed.')
                        
                        # Sending the reminder only on Thursdays
                        if datetime.date.today().weekday() == 3:
                            self._log('Today\'s day is Thursday : sending reminder...')
                            self._notify_lot_recall(warranty)
                        else:
                            self._log('Today\'s day isn\'t Thursday : nothing to do.')
                    # Else it means the warranty has expired : sending the reminder every day
                    else:
                        self._log('Warranty has expired : sending reminder...')
                        self._notify_lot_recall(warranty)
                    
                
    def _notify_lot_recall(self, warranty):
        self._log('Generating email content...')
        subject = self._construct_subject(warranty)
        body = self._construct_body_html(warranty)
        self._log('Email content generated.')
               
        self._log('Retrieving assigned contacts (notification recipients)...')
        ass_by = None
        ass_to = None
        copy_to = None
        if warranty.assigned_by:
            ass_by = warranty.assigned_by.email
        if warranty.assigned_to:
            ass_to = warranty.assigned_to.email
        if warranty.copy_to:
            copy_to = warranty.copy_to.email
        self._log('Assigned contacts retrieved.')
            
        self._log('Creating sender (address and database name)...')
        sender = 'Prisme - ODOO (' + self._cr.dbname + \
                 ') <system.odoo@prisme.ch>'
            
        self._log('Checking for same e-mail addresses...')
        # If the field assigned by has been filled
        if ass_by:
            self._log('Checking [' + ass_by + ']...')            
            # Sending e-mail to the user            
            self._send_email(sender, ass_by, subject, body)
        if ass_to:
            self._log('Checking [' + ass_to + ']...')
            if not ass_to == ass_by:
                self._log(ass_to + ' different from ' + ass_by)
                self._send_email(sender, ass_to, subject, body)
            else:
                self._log(ass_to + ' same as ' + ass_by + ': already sent.')
        if copy_to:
            self._log('Checking [' + copy_to + ']...')
            if not copy_to == ass_by and not copy_to == ass_to:
                self._log(copy_to + ' different from ' + ass_by + ' and ' + ass_to)
                self._send_email(sender, copy_to, subject, body)
            else:
                self._log(copy_to + ' same as ' + ass_by + ' or ' + ass_to + ': already sent.')
    
    def _construct_subject(self, warranty):
        self._log('Creating subject...')
        lot = warranty.lot_id
        end_date_string = ""
        
        if warranty.end_date:
            self._log('End date found.')
            
            # Checking if warranty has already expired or not and creating the end part of the string depending on the result
            if(warranty.end_date >= datetime.date.today()):
                expiration_string = " will soon expire"
            else:
                expiration_string = " has expired"
            end_date_string = expiration_string + " (End date : " + datetime.datetime.strftime(warranty.end_date,"%d-%m-%Y") + ")."
           
            if lot:
                self._log('Lot found.')
                customer_string = ""
                
                if lot.customer:
                    self._log('Customer found.')
                    customer_string = ", customer : " + lot.customer.name
                    
                    
                subject = "ODOO reminder : warranty from [" + lot.product_id.name + " (S/N : " + lot.name + customer_string + ")]"
            else:
                self._log('Lot not found')
                subject = "ODOO reminder : warranty from an unknown lot"
            
            subject += end_date_string
            
        self._log('Subject created.')
        return subject
    
    def _construct_body_html(self, warranty):
        self._log('Creating body...')
        
        body = "Warranty expiration reminder <br/>"
        body = body + "------------------------------- <br/><br/>"
            
        body = body + "Warranty informations : <br/>"
        description = warranty.description
        ass_by = warranty.assigned_by.name
        ass_to = warranty.assigned_to.name
        copy_to = warranty.copy_to.name
        type = warranty.warranty_type_id.name
        state = warranty.state
        start_date = warranty.start_date
        end_date = warranty.end_date
        recall_date = warranty.recall_date
        notes = warranty.contact_notes
        if description:
            self._log('Description found.')
            body = body + "Description: <br/>" + description + "<br/><br/>"
            
        if type:
            self._log('Type found.')
            body = body + "Type: " + type + "<br/>"
        if state:
            self._log('State found.')
            body = body + "Statut: " + state + "<br/><br/>"
            
        if ass_by:
            self._log('Assigned by found.')
            body = body + "Assigned by : " + ass_by + "<br/>"
        if ass_to:
            self._log('Assigned to found.')
            body = body + "Assigned to : " + ass_to + "<br/>"
        if copy_to:
            self._log('Copy to found.')
            body = body + "Copy to : " + copy_to + "<br/><br/>"
            
        if start_date:
            self._log('Start date found.')
            body = body + "Start date : " + datetime.datetime.strftime(start_date,"%d-%m-%Y") + "<br/>"
        if end_date:
            self._log('End date found.')
            body = body + "End date : " + datetime.datetime.strftime(end_date,"%d-%m-%Y") + "<br/>" 
        if recall_date:
            self._log('Reminder date found.')
            body = body + "Reminder date : " + datetime.datetime.strftime(recall_date,"%d-%m-%Y") + "<br/><br/>" 
            
        if notes:
            self._log('Notes found.')
            body = body + "Notes : <br/>" + notes 
        
        lot = warranty.lot_id
        if lot:
            self._log('Lot found.')
            body = body + "<br/><br/><br/>Lot informations : <br/>"
            s_n = lot.name
            product = lot.product_id.name
            description = lot.description
            customer = lot.customer
            end_user = lot.user
            end_user_dept = lot.user_department
            manufacturer = lot.manufacturer
            supplier = lot.supplier.name
            remarks = lot.remarks
            
            body = body + "S/N : " + s_n + "<br/>"
            body = body + "Product : " + product + "<br/><br/>"
             
            if description:
                self._log('Description found.')
                body = body + "Description : <br/>" + description + "<br/><br/>"
                  
            if customer:
                self._log('Customer found.')
                body = body + "Customer : " + customer.name + "<br/>" 
            if end_user_dept:
                self._log('End user dept found.')
                body = body + "End user department : " + \
                    end_user_dept + "<br/>" 
            if end_user:
                self._log('End user found.')
                body = body + "End user : " + end_user + "<br/><br/>"
            
            if manufacturer:
                self._log('Manufacturer found.')
                body = body + "Manufacturer : " + manufacturer + "<br/>" 
            if supplier:
                self._log('Supplier found.')
                body = body + "Supplier : " + supplier + "<br/><br/>" 
            if remarks:
                self._log('Remarks found.')
                body = body + "Remarks : <br/>" + remarks
            
            body = "<br />".join(body.split("\n"))
        return body
    
    def _send_email(self, sender, recipient, subject, body_html):
        self._log('Sending mail...')
        self._log('Sending to ' + recipient + '. Subject : ' + subject)
        
        template_obj = self.env['mail.mail']
        template_data = {
                'subject': subject,
                'body_html': body_html,
                'email_from': sender,
                'email_to': ", ".join([recipient])
                }
        template_id = template_obj.create(template_data).send()
        self._log('Mail sent...')
    
        self._debug("Sending email to " + recipient + ". " + \
            "Subject: \"" + subject + "\"")
        
    def _log(self, message):
        logger = prisme_file_logger.prisme_file_logger()
        logger.log(message)
        
    def _debug(self, message):
        _logger.debug(message)
