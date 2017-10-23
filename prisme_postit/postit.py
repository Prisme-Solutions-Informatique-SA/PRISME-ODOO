# -*- coding: utf-8 -*-

import datetime
import tools
from osv import osv, fields
import prisme_file_logger
import logging

_logger = logging.getLogger('prisme_postit')

class prisme_postit(osv.osv):
    """ Post It data """
    _name = "prisme.postit"
    _description = "Prisme postit"
    _columns = {
        'name': fields.char('Name', required=True),
        'description': fields.text(),
        'assigned_by' : fields.many2one('res.users', string="Assigned by"),
        'assigned_to' : fields.many2many('res.users', 'prisme_postit_assignedto_rel', string="Assigned to"),
        'copy_to' : fields.many2many('res.users', 'prisme_postit_copyto_rel', string="Copy to"),
        'partner_id' : fields.many2one('res.partner', string="Client"),
        'priority' : fields.integer(string="Priority"),
        'tags' : fields.many2many('prisme.postit.tag', string="Tags"),
        'days' : fields.many2many('prisme.postit.day', string="Days"),
        'date_start' : fields.date(default=fields.date.today, string="Date start"),
        'date_end' : fields.date(string="Date end"),
        'recall_date' : fields.date(string="Recall Date"),
        'duration' : fields.char(string='Duration'),
        'state': fields.selection(string="State", [('active', 'Non termine'),
                                   ('start','Demarre'),
                                   ('in_process','En cours'),
                                   ('closed', 'Termine'),
                                   ], default='active')
    }

    def action_start(self, cr, uid, ids, context=None):
        self._log('start postit')
        return self.write(cr, uid, ids, {'state': 'start'}, context=context)

    def action_in_process(self, cr, uid, ids, context=None):
        self._log('in process postit')
        return self.write(cr, uid, ids, {'state': 'in_process'}, context=context)

    def action_close(self, cr, uid, ids, context=None):
        self._log('close postit')
        return self.write(cr, uid, ids, {'state': 'closed'}, context=context)

    def action_active(self, cr, uid, ids, context=None):
        self._log('active postit')
        return self.write(cr, uid, ids, {'state': 'active'}, context=context)

    # Launched each minute, this scheduled action write the date and hour
    # into a file to allow to view if the vm is on
    def log_vm_on(self, cr, uid, automatic=False, use_new_cursor=False, \
                  context=None):
        import time
        current_date = time.strftime('%d.%m.%Y', time.localtime())
        current_time = time.strftime('%H:%M:%S', time.localtime())
    
    def scheduled_action(self, cr, uid, automatic=False, use_new_cursor=False, \
                       context=None):
        import time

        self._log('Lancement du planificateur (' + \
                  time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()) + ')')
        self._debug("postits scanning called by a trigger")
        self._check_postit_dates(cr, uid, context)
        self._log('Fin')
        self._log('\n')

    def _check_postit_dates(self, cr, uid, context=None):
        self._log('')
        self._log('Scan des postit de la base ' + cr.dbname)
        postits_ids = self.search(cr, uid, [("state", "!=", "closed")])
        postits = self.browse(cr, uid, postits_ids)
        for postit in postits:
            self._log('-------------------------------------------------------')
            self._log('Postit '+postit.name+ ' en traitement')
            # self._log('Scan d\'un  du lot ' + warranty.lot_id.name)
            if postit.state != "closed":
                self._log('Satut ouvert')
                if postit.recall_date:
                    
                    recall_date = \
                    datetime.datetime.strptime(postit.recall_date, \
                        "%Y-%m-%d").date()            
                    # Si la date de rappelle est passee
                    if  recall_date <= datetime.date.today():
                        self._log('Date de rappel depasse')
                        # Si la garantie est en cours de renouvellement
                        if postit.state == "start" or\
                            postit.state == "in_process" or\
                            postit.state == "active":
                            #self._log('Garantie en cours de renouvellement')
                            # On envoie un rappel uniquement si on est jeudi
                            if postit.days:
                                weekday = postit.days
                                for day in weekday:
                                    self._log('Control pour le jour: '+day.name)
                                    if datetime.date.today().weekday() == day.nbr:
                                        self._log('Jour du rappel... envoie du message')
                                        self._notify_recall(cr, uid, postit," en cours, echeance le ")

    def _notify_recall(self, cr, uid, postit,message):
        self._log('Construction de l\'e-mail')
        subject = self._construct_subject(cr, uid, postit,message)
        body = self._construct_body(cr, uid, postit)
               
        self._log('Recuperation des personnes a notifier')
        ass_by = None
        ass_to_list = None
        copy_to_list = None
        if postit.assigned_by:
            ass_by = postit.assigned_by.email
        if postit.assigned_to:
            ass_to_list = postit.assigned_to
        if postit.copy_to:
            copy_to_list = postit.copy_to
            
        self._log('Recuperation du nom de la base de donnees')
        sender = 'Prisme - OpenERP (' + cr.dbname + \
                 ') <system.openerp@prisme.ch>'
            
        self._log('Calcul pour eviter les envois a double')
        # If the field assigned by has been filled
        if ass_by:
            self._log('Calcul pour ' + ass_by)
            
            # Sending e-mail to the user
            self._send_email(cr, uid, sender, ass_by, subject, body)
        if ass_to_list:
            for ass_to in ass_to_list:
                self._log('Calcul pour ' + ass_to.email)
                if not ass_to.email == ass_by:
                    self._log(ass_to.email + ': Envoi')
                    self._send_email(cr, uid, sender, ass_to.email, subject, body)
        if copy_to_list:
            for copy_to in copy_to_list:
                self._log('Calcul pour ' + copy_to.email)
                if not copy_to == ass_by and not copy_to.email == ass_to.email:
                    self._log(copy_to.email + ' != ' + ass_by + ' & ' + \
                             copy_to.email + ' != ' + ass_to + ': Envoi')
                    self._send_email(cr, uid, sender, copy_to, subject, body)
    
    def _construct_subject(self, cr, uid, postit,message):
        self._log('Construction du sujet')       
        end_date_string = ""
        if postit.date_end:
            self._log('Date de fin trouvee')
            end_date_string = "(" + postit.date_end + ")"
        subject = "Postit (" + postit.name + ")"  +message+ end_date_string
        return subject
    
    def _construct_body(self, cr, uid, postit):
        self._log('Construction du corps')
        
        body = "Rappel d'expiration de tache" + "\n"
        body = body + "-------------------------------\n\n"
            
        body = body + "Tache: "+ postit.name +"\n"
        description = postit.description
        ass_by = postit.assigned_by.name
        ass_to_list = postit.assigned_to
        copy_to_list = postit.copy_to
        tag_list = postit.tags
        state = postit.state
        date_start = postit.date_start
        date_end = postit.date_end
        recall_date = postit.recall_date
        partner_id = postit.partner_id
        priority = postit.priority
        duration = postit.duration

        if ass_by:
            self._log('Assigne par trouve')
            body = body + "Assigne par: " + ass_by + "\n"
        if partner_id:
            self._log('Client trouve')
            body = body + "Client: " + partner_id.name + "\n"
        if priority:
            self._log('Priority trouve')
           # body = body + "Priority: " + priority + "\n" 
        if date_start:
            self._log('Date de debut trouvee')
            body = body + "Date de debut: " + date_start + "\n"
        if date_end:
            self._log('Date de fin trouvee')
            body = body + "Date limite: " + date_end + "\n" 
        if duration:
            self._log('duration trouvee')
            body = body + "Duree: " + duration + "\n" 
        if recall_date:
            self._log('Date de rappel trouve')
            body = body + "Date echeance Prisme: " + recall_date + "\n\n" 

        if ass_to_list:
            for ass_to in ass_to_list:
                self._log('Assigne a trouve')
                body = body + "Assigne a: " + ass_to.name + "\n"
        if copy_to_list:
            for copy_to in copy_to_list:
                self._log('Copie a trouve')
                body = body + "Copie a: " + copy_to.name + "\n\n"

        if description:
            self._log('Description trouve')
            body = body + "Description: \n" + description + "\n\n"

        if tag_list:
            body = body + "Type: "
            self._log('Type trouve')
            for type_name in tag_list:
                body = body +" "+ type_name.name
            body = body + "\n"
        return body
    
    def _send_email(self, cr, uid, sender, recipient, subject, body):
        self._log('Tentative d\'envoi du mail')
        self._log('Envoi d\'un e-mail a ' + recipient + '. Sujet: ' + subject)
        tools.email_send(email_from=sender, email_to=[recipient] , \
                         subject=subject, body=body, cr=cr)
        self._debug("Sending email to " + recipient + ". " + \
            "Subject: \"" + subject + "\"")

    def _log(self, message):
        print message
        logger = prisme_file_logger.prisme_file_logger()
        logger.log(message)
        
    def _debug(self, message):
        _logger.debug(message)

prisme_postit()






