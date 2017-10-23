import datetime
from openerp import tools
from openerp.osv import fields, osv, expression
import prisme_file_logger
import logging

_logger = logging.getLogger('prisme_lots_enhancement')

class prisme_warranty_warranty(osv.osv):
    _name = 'prisme.warranty.warranty'
    
    _columns = {
        'description': fields.text('Description'),
    
        'assigned_by': fields.many2one('res.partner',
                                        string='Assigned By'),
        'assigned_to': fields.many2one('res.partner',
                                        string='Assigned To'),
        'copy_to': fields.many2one('res.partner',
                                    string='Copy To'),
        'warranty_type_id': fields.many2one(
                    'prisme.warranty.type',
                    string='Type'
                    ),
        'state': fields.selection([('active', 'Active'),
                                   ('cur_ren_suppl',
                                    'Current Renewal (Suppl.)'),
                                   ('cur_ren_cust',
                                    'Current Renewal (Cust.)'),
                                   ('closed', 'Closed')],
                                    'State', required=True),
                                    
        #TODO The context would complete the partner search field to
        # match the supplier name
        'last_suppl_invoice': fields.many2one('account.invoice',
                                string='Last Supplier Invoice',
                                domain="[('type','=','in_invoice')]"),
                                
        #TODO The context would complete the partner search field to
        # match the customer name
        'last_cust_invoice': fields.many2one('account.invoice',
                                string='Last Customer Invoice',
                                domain="[('type','=','out_invoice')]"),
                                
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'recall_date': fields.date('Recall Date'),
        
        'internal_notes': fields.text('Internal Notes'),
        'contact_notes': fields.text('Notes for Contact'),
        
        'lot_id': fields.many2one('stock.production.lot', ondelete='cascade',
                                  string="Production Lot", required=True),
                                  # required=True:
                                  # Attention a la creation depuis un lot qui
                                  # ne remplira ce champ que lors de la 
                                  # sauvegarde du lot (ce qui empeche
                                  # l'enregistrement de la garantie)
        'partner' : fields.many2one('res.partner', string='Partner',readonly=True),
    }
    
    # Launched each minute, this scheduled action write the date and hour
    # into a file to allow to view if the vm is on
    def log_vm_on(self, cr, uid, automatic=False, use_new_cursor=False, \
                  context=None):
        import time
        current_date = time.strftime('%d.%m.%Y', time.localtime())
        current_time = time.strftime('%H:%M:%S', time.localtime())
        
        self._debug('Writing date in vm_on')
        
        logger = prisme_file_logger.prisme_file_logger(
                    '/var/log/prisme/vm_on-warranty/', 7)
        logger.log(current_date + ', ' + current_time + ' : ON')
    
    def scheduled_action(self, cr, uid, automatic=False, use_new_cursor=False, \
                       context=None):
        import time
        self._log('Lancement du planificateur (' + \
                  time.strftime('%d.%m.%Y %H:%M:%S', time.localtime()) + ')')
        self._debug("Warranties scanning called by a trigger")
        self._check_warranty_dates(cr, uid, context)
        self._log('Fin')
        self._log('\n')
        
    def _check_warranty_dates(self, cr, uid, context=None):
        self._log('')
        self._log('Scan des garanties de la base ' + cr.dbname)
        warranties_ids = self.search(cr, uid, [("state", "!=", "closed")])
        warranties = self.browse(cr, uid, warranties_ids)
        for warranty in warranties:
            self._log('-------------------------------------------------------')
            self._log('Scan d\'une garantie du lot ' + warranty.lot_id.name)
            if warranty.recall_date:
                recall_date = \
                    datetime.datetime.strptime(warranty.recall_date, \
                    "%Y-%m-%d").date()
        
                # Si la date de rappelle est passee
                if  recall_date <= datetime.date.today():
                    self._log('Date de rappel de la garantie du lot ' + \
                              warranty.lot_id.name + ' depassee')
                    # Si la garantie est en cours de renouvellement
                    if warranty.state == "cur_ren_suppl" or\
                        warranty.state == "cur_ren_cust": 
                        self._log('Garantie en cours de renouvellement')
                        # On envoie un rappel uniquement si on est jeudi
                        if datetime.date.today().weekday() == 3:
                            self._log('Jeudi: rappel')
                            self._notify_lot_recall(cr, uid, warranty)
                        else:
                            self._log('Pas jeudi: aucun rappel')
                    # Sinon, on envoie un rappel quel que soit le jour
                    else:
                        self._log('Garantie expiree')
                        self._notify_lot_recall(cr, uid, warranty)
                    
                
    def _notify_lot_recall(self, cr, uid, warranty):
        self._log('Construction de l\'e-mail')
        subject = self._construct_subject(cr, uid, warranty)
        body = self._construct_body(cr, uid, warranty)
               
        self._log('Recuperation des personnes a notifier')
        ass_by = None
        ass_to = None
        copy_to = None
        if warranty.assigned_by:
            ass_by = warranty.assigned_by.email
        if warranty.assigned_to:
            ass_to = warranty.assigned_to.email
        if warranty.copy_to:
            copy_to = warranty.copy_to.email
            
        self._log('Recuperation du nom de la base de donnees')
        sender = 'Prisme - OpenERP (' + cr.dbname + \
                 ') <system.openerp@prisme.ch>'
            
        self._log('Calcul pour eviter les envois a double')
        # If the field assigned by has been filled
        if ass_by:
            self._log('Calcul pour ' + ass_by)
            
            # Sending e-mail to the user
            self._send_email(cr, uid, sender, ass_by, subject, body)
        if ass_to:
            self._log('Calcul pour ' + ass_to)
            if not ass_to == ass_by:
                self._log(ass_by + ' != ' + ass_by + ': Envoi')
                self._send_email(cr, uid, sender, ass_to, subject, body)
        if copy_to:
            self._log('Calcul pour ' + copy_to)
            if not copy_to == ass_by and not copy_to == ass_to:
                self._log(copy_to + ' != ' + ass_by + ' & ' + \
                          copy_to + ' != ' + ass_to + ': Envoi')
                self._send_email(cr, uid, sender, copy_to, subject, body)
    
    def _construct_subject(self, cr, uid, warranty):
        self._log('Construction du sujet')
        lot = warranty.lot_id
        
        end_date_string = ""
        if warranty.end_date:
            self._log('Date de fin trouvee')
            end_date_string = " (Date de fin: " + warranty.end_date + ")"
           
        if lot:
            self._log('Lot trouve')
            customer_string = ""
            if lot.customer:
                self._log('Client trouve')
                customer_string = ", client: " + lot.customer.name
                
                
            subject = "Rappel OpenERP: Une garantie du " + \
                lot.product_id.name + \
                " (s/n: " + lot.name + customer_string + \
                ") a expire ou expirera bientot" + end_date_string
        else:
            self._log('Lot non trouve')
            subject = "Rappel OpenERP: Une garantie non liee a un lot a" + \
                " expire ou expirera bientot" + end_date_string
        return subject
    
    def _construct_body(self, cr, uid, warranty):
        self._log('Construction du corps')
        
        body = "Rappel d'expiration de garantie\n"
        body = body + "-------------------------------\n\n"
            
        body = body + "Informations sur la garantie:\n"
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
            self._log('Description trouve')
            body = body + "Description: \n" + description + "\n\n"
            
        if type:
            self._log('Type trouve')
            body = body + "Type: " + type + "\n"
        if state:
            self._log('Etat trouve')
            body = body + "Statut: " + state + "\n\n"
            
        if ass_by:
            self._log('Assigne par trouve')
            body = body + "Assigne par: " + ass_by + "\n"
        if ass_to:
            self._log('Assigne a trouve')
            body = body + "Assigne a: " + ass_to + "\n"
        if copy_to:
            self._log('Copie a trouve')
            body = body + "Copie a: " + copy_to + "\n\n"
            
        if start_date:
            self._log('Date de debut trouvee')
            body = body + "Date de debut: " + start_date + "\n"
        if end_date:
            self._log('Date de fin trouvee')
            body = body + "Date de fin: " + end_date + "\n" 
        if recall_date:
            self._log('Date de rappel trouve')
            body = body + "Date de rappel: " + recall_date + "\n\n" 
            
        if notes:
            self._log('Notes trouvees')
            body = body + "Notes: \n" + notes 
        
        lot = warranty.lot_id
        if lot:
            self._log('Lot trouve')
            body = body + "\n\n\nInformations sur le lot: \n"
            s_n = lot.name
            product = lot.product_id.name
            description = lot.description
            customer = lot.customer
            end_user = lot.user
            end_user_dept = lot.user_department
            manufacturer = lot.manufacturer
            supplier = lot.supplier.name
            remarks = lot.remarks
            
            body = body + "s/n: " + s_n + "\n"
            body = body + "produit: " + product + "\n\n"
             
            if description:
                self._log('Description du lot trouve')
                body = body + "Description: \n" + description + "\n\n"
                  
            if customer:
                self._log('Client trouve')
                body = body + "Client: " + customer.name + "\n" 
            if end_user_dept:
                self._log('Dept de l\'utilisateur final trouve')
                body = body + "Departement de l'utilisateur final: " + \
                    end_user_dept + "\n" 
            if end_user:
                self._log('Utilisateur final trouve')
                body = body + "Utilisateur final: " + end_user + "\n\n"
            
            if manufacturer:
                self._log('Contstructeur trouve')
                body = body + "Constructeur: " + manufacturer + "\n" 
            if supplier:
                self._log('Fournisseur trouve')
                body = body + "Fournisseur: " + supplier + "\n\n" 
            if remarks:
                self._log('Remarques trouve')
                body = body + "Remarques: \n" + remarks
        return body
    
    def _send_email(self, cr, uid, sender, recipient, subject, body):
        self._log('Tentative d\'envoi du mail')
        self._log('Envoi d\'un e-mail a ' + recipient + '. Sujet: ' + subject)
        tools.email_send(email_from=sender, email_to=[recipient] , \
                         subject=subject, body=body, cr=cr)
        self._debug("Sending email to " + recipient + ". " + \
            "Subject: \"" + subject + "\"")
        
    def _log(self, message):
        logger = prisme_file_logger.prisme_file_logger()
        logger.log(message)
        
    def _debug(self, message):
        _logger.debug(message)
        
prisme_warranty_warranty()
