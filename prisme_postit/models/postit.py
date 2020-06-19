# -*- coding: utf-8 -*-
###########################################################################
#
#    Prisme Solutions Informatique SA
#    Copyright (c) 2016 Prisme Solutions Informatique SA <http://prisme.ch>
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
#    Project ID:    OERP-009-01 - T527
#
#    Modifications:
#
##########################################################################
from datetime import datetime
from odoo import models, fields, api, _

class prisme_postit(models.Model):
    """ Post It data """
    _name = 'prisme.postit'
    _description = 'Prisme postit'
    _inherit = ['mail.thread']
    _order = 'assigned_to, priority'
    
    team = fields.Many2one('prisme.postit.team', string="Team") 
    name= fields.Char(string="Name", required=True)
    names_users = fields.Char(string="Users Assigned")
    description = fields.Text()
    assigned_by = fields.Many2one('res.users', string="Assigned by")
    assigned_to = fields.Many2many('res.users', 'prisme_postit_assignedto_rel', string="Assigned to")
    copy_to = fields.Many2many('res.users', 'prisme_postit_copyto_rel', string="Copy to")
    partner_id = fields.Many2one('res.partner', string="Client")
    priority = fields.Integer(string="Priority")
    tags = fields.Many2many('prisme.postit.tag', string="Tags")
    days = fields.Many2many('prisme.postit.day', string="Days")
    date_start = fields.Date(string="Date start")
    date_end = fields.Date(string="Date end")
    recall_date = fields.Date(string="Recall Date")
    duration = fields.Char(string='Duration')
    state= fields.Selection([('active', 'Not Completed'),('get_started','Started'),('in_process','In process'),('terminated', 'Completed'),], default='active')

    def init(self):
        self.env.cr.execute("""DROP TRIGGER IF EXISTS postit_update ON prisme_postit_assignedto_rel;""")
        self.env.cr.execute("""CREATE OR REPLACE FUNCTION postit_update() RETURNS trigger AS $$ BEGIN IF pg_trigger_depth() <> 1 THEN RETURN NEW; END IF; UPDATE prisme_postit SET names_users = subquery.string_agg FROM (SELECT ppar.prisme_postit_id,string_agg(partner.name, ', ') FROM prisme_postit_assignedto_rel ppar JOIN res_users users ON users.id=ppar.res_users_id JOIN res_partner partner ON partner.id=users.partner_id GROUP BY ppar.prisme_postit_id) AS subquery Where prisme_postit.id=subquery.prisme_postit_id; RETURN NEW; END; $$ LANGUAGE plpgsql;""")
        self.env.cr.execute("""CREATE TRIGGER postit_update AFTER INSERT OR UPDATE OR DELETE ON prisme_postit_assignedto_rel WHEN (pg_trigger_depth() < 1) EXECUTE PROCEDURE postit_update();""")
    @api.model
    def action_start(self):
        return self.write({'state': 'get_started'})
    @api.model
    def action_in_process(self):
        return self.write({'state': 'in_process'})
    @api.model
    def action_close(self):
        return self.write({'state': 'terminated'})
    @api.model
    def action_active(self):
        return self.write( {'state': 'active'})
    
    def get_started(self):
        return self.write({'state': 'get_started'})

    def in_process(self):
        return self.write({'state': 'in_process'})

    def terminated(self):
        return self.write({'state': 'terminated'})

    def active(self):
        return self.write( {'state': 'active'})

    @api.model
    def scheduled_action(self):
        #cr, uid, context = self.env.args

        self._check_postit_dates()

    @api.model
    def _check_postit_dates(self):
        #postits_ids = self.search([("state", "!=", "closed")])
        
        postits = self.search([('state', '!=', 'closed'),('state', '!=', 'active')])
        for p in postits:

            if p.state != "closed" and p.state != "active":
                if p.recall_date:
                    recall_date = datetime.strptime(str(p.recall_date), "%Y-%m-%d")
                    
                    if  recall_date <= datetime.now():
                        if p.state == "get_started" or\
                            p.state == "in_process" or\
                            p.state == "active":
                            if p.days:
                                weekday = p.days
                                for day in weekday:
                                    if datetime.now().weekday() == day.nbr:
                                        p._notify_recall(_(" In process. End date")+": ")
    @api.model
    def _notify_recall(self,message):
        subject = self._construct_subject(message)
        body = self._construct_body()

        ass_by = None
        ass_to_list = None
        copy_to_list = None
        if self.assigned_by:
            ass_by = self.assigned_by.email
        if self.assigned_to:
            ass_to_list = self.assigned_to
        if self.copy_to:
            copy_to_list = self.copy_to
        
        sender = 'Prisme - OpenERP (' + self.env.cr.dbname + \
                 ') <system.openerp@prisme.ch>'
            
        # If the field assigned by has been filled
        if ass_by:
            
            # Sending e-mail to the user
            self._send_email(sender, ass_by, subject, body)
        if ass_to_list:
            for ass_to in ass_to_list:
                if not ass_to.email == ass_by:
                    self._send_email(sender, ass_to.email, subject, body)
        if copy_to_list:
            for copy_to in copy_to_list:
                if not copy_to.email == ass_by and not copy_to.email == ass_to.email:
                    self._send_email(sender, copy_to.email, subject, body)
    @api.model
    def _construct_subject(self,message):
        end_date_string = ""
        if self.date_end:
            end_date_string = "(" + str(self.date_end) + ")"
        subject = "Postit (" + self.name + ")"  +message+ end_date_string
        return subject
    @api.model
    def _construct_body(self):
       
        body = _("Task expiration reminder") + "\n"
        body = body + "-------------------------------\n\n"
            
        body = body + _("Task")+": "+ self.name +"\n"

        if self.team:
            body = body + _("Team")+": " + self.team.name + "\n"
        if self.assigned_by:
            body = body + _("Assigned by")+": " + self.assigned_by.name + "\n"
        if self.partner_id:
            body = body + _("Client") +": "+ self.partner_id.name + "\n"
        if self.date_start:
            body = body + _("Start date") +": "+ str(self.date_start) + "\n"
        if self.date_end:
            body = body + _("End date") +": "+str(self.date_end) + "\n" 
        if self.duration:
            body = body + _("Duration") +": "+ self.duration + "\n" 
        if self.recall_date:
            body = body + _("Recall date") +": "+ str(self.recall_date) + "\n\n" 

        if self.assigned_to:
            for ass_to in self.assigned_to:
                body = body + _("Assigned to")+": " + ass_to.name + "\n"
        if self.copy_to:
            for copy_to in self.copy_to:
                body = body + _("Copy to") +": "+ copy_to.name + "\n\n"
        if self.description:
            body = body + _("Description")+":\n" + self.description + "\n\n"

        if self.tags:
            body = body + _("Type")+": "
            for type_name in self.tags:
                body = body +" "+ type_name.name
            body = body + "\n"
        
        body = "<br />".join(body.split("\n"))
        
        return body
    
    @api.model
    def _send_email(self, sender, recipient, subject, body_html):        
        template_obj = self.env['mail.mail']
        template_data = {
                'subject': subject,
                'body_html': body_html,
                'email_from': sender,
                'email_to': ", ".join([recipient])
                }
        template_obj.create(template_data).send()
        print(", ".join([recipient]))
    @api.model
    def _log(self, message):
        print (message)





