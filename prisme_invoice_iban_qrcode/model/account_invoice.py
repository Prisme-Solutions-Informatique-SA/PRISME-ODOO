# -*- coding: utf-8 -*-

from odoo import api, fields, exceptions, models, tools, _
from odoo.modules.module import get_resource_path
from PIL import Image
import os, io, base64, pyqrcode, traceback, sys

CH_KREUZ_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "src", "img", "CH-Kreuz_7mm.png")
# CH_KREUZ_IMAGE_PATH = get_resource_path("prisme_invoice_iban_qrcode", "static", "src", "img", "CH-Kreuz_7mm.png")

# Compute the BVR reference number checksum
# Using the modulo 10 
# - The parameter must be a string containing only digit
# Documentation of the algorithm from Credit Suisse:
# https://www.credit-suisse.com/media/assets/private-banking/docs/ch/unternehmen/kmugrossunternehmen/besr-technische-dokumentation-en.pdf
def bvr_checksum(bvr):
    table = [
        [0,9,4,6,8,2,7,1,3,5],
        [9,4,6,8,2,7,1,3,5,0],
        [4,6,8,2,7,1,3,5,0,9],
        [6,8,2,7,1,3,5,0,9,4],
        [8,2,7,1,3,5,0,9,4,6],
        [2,7,1,3,5,0,9,4,6,8],
        [7,1,3,5,0,9,4,6,8,2],
        [1,3,5,0,9,4,6,8,2,7],
        [3,5,0,9,4,6,8,2,7,1],
        [5,0,9,4,6,8,2,7,1,3]
    ]
    report = 0
    for serie in bvr[:-1]:
        report = table[report][int(serie)]
    return (10 - report) % 10



class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"
    
    qrcode_qrbill = fields.Binary(string='QRCode', compute='_iban_qrcode', store=False)
    qrcode_status = fields.Text(string='QRCode Status', compute='_iban_qrcode', store=False)

    # Computes qrcode_qrbill and qrcode_status for a list of invoice
    # If the invoice is not a Customer Invoice, the entry will be skipped
    # If the invoice is in draft, only the content of the QRCode will be generated
    # Otherwise the QRCode image will be generated
    # In case of error, a message is set in qrcode_status
    @api.model
    def _iban_qrcode(self):
        for inv in self:
            # Skip if the invoice is not outgoing, the view will hide the tab
            if inv.type == 'out_invoice':
                try:
                    if inv.number:
                        # If the invoice is validated
                        # Generate the base64 encoded image
                        # This will raise an exception if the data are invalid
                        inv.qrcode_qrbill = self._generate_qrbill_base64(inv)
                    else:
                        # If the invoice is not validated
                        # Generate the content of the QRCode
                        # (use less resources than creating the whole image)
                        # This will raise an exception if the data are invalid
                        self._generate_qrbill_content(inv)
                        inv.qrcode_status = _("The QRCode will be generated once you validate the invoice")
                except exceptions.except_orm, orm_ex:
                    inv.qrcode_status = "%s\n\t%s" % (orm_ex.name, orm_ex.value)
                except Exception, ex:
                    traceback.print_exc(file=sys.stdout)
                    inv.qrcode_status = str(ex)
    
    # Generates the QRCode from the Customer Invoice
    # Call self._generate_qrbill_content(invoice) to compute the content
    # Uses an in-memory stream to generate Image
    # 1) Generate a PNG with pyqrcode
    # 2) Open and resize the Swiss logo
    # 3) Paste the logo in the middle of the QRCode
    # 4) Generate the base 64 image encoded from the PNG
    def _generate_qrbill_base64(self, invoice):
        # Get the content of the QRCode from the invoice
        qr_content = self._generate_qrbill_content(invoice)
        # Create a QRCode from the content, Error M (up to 15% damage)
        qr = pyqrcode.create(qr_content, error='M')
        
        # In memory Stream
        with io.BytesIO() as f:
            # Generate the PNG from the QR
            qr.png(f, scale=7, module_color=(0, 0, 0, 255), background=(255, 255, 255, 255), quiet_zone=0)
            
            # Reset pointer to the beginning
            f.seek(0)
            
            # Create an image from the PNG in memory
            with Image.open(f) as im:
                # Create an image from the PNG in the module static files
                with Image.open(CH_KREUZ_IMAGE_PATH) as original_logo:
                    # Resize the logo to 75x75
                    logo = original_logo.resize((75, 75))
                    # Close the original_logo when going out of the with
                
                # Use logo created in the preceding with
                with logo:
                    # Calculate the start point (top left) for the logo
                    start_x = (im.width - logo.width) / 2
                    start_y = (im.height - logo.height) / 2
                    # Create the box position
                    box = (start_x, start_y, start_x + logo.width, start_y + logo.height)
                    # Clear the zone > Useless since the logo is not transparent
                    # im.crop(box)
                    # Paste the logo in the zone
                    im.paste(logo, box)
                
                # Reset pointer to the beginning
                f.seek(0)
                # Save the modified QRCode in the memory
                im.save(f, format='PNG')
            
            # Reset pointer to the beginning
            f.seek(0)
            # Create the base64 from the memory image
            b64_qr = base64.b64encode(f.read())
        
        return b64_qr
    
    # Generates the content of the QRCode for the QR-bill
    # According to https://www.paymentstandards.ch/en/home/schemes/payment-slips.html
    def _generate_qrbill_content(self, invoice):
        # QRType MUST be "SPC"
        qr_type = 'SPC'
        # Use Version 1.0 (0100)
        version = '0100'
        # Encoding: Latin-1 (1)
        coding_type = '1'
        
        # If the bank id is not set, the IBAN doesn't exist
        if not invoice.partner_bank_id:
            raise exceptions.except_orm(_('Invalid IBAN'), _('You must specify an IBAN'))
        creditor_iban = invoice.partner_bank_id.sanitized_acc_number
        # If the IBAN is not a string or is empty, the IBAN is invalid
        if (not isinstance(creditor_iban, basestring)) or (len(creditor_iban) == 0):
            raise exceptions.except_orm(_('Invalid IBAN'), _('You must specify an IBAN'))
        # The QR-bill support only IBAN starting with "CH" and "LI"
        elif not (creditor_iban.startswith("CH") or creditor_iban.startswith("LI")):
            raise exceptions.except_orm(_('Invalid IBAN'), _('Only IBANs starting with CH or LI are permitted. IBAN: %s') % (invoice.partner_bank_id.acc_number))
        # The IBAN must be exactly 21 characters
        elif not len(creditor_iban) == 21:
            raise exceptions.except_orm(_('Invalid IBAN'), _('IBAN "%s" length (%s) must be exactly 21 characters long') % (invoice.partner_bank_id.acc_number, len(creditor_iban)))
        
        # Generate Creditor data
        creditor = self._generate_qrbill_contact_data(invoice.company_id.partner_id, "Creditor")
        
        # Generate Ultimate Creditor data (from None => 6 empty lines)
        # 5 NewLine (\n) => 6 Lines with Carriage Return (\r)
        # (name + street + number + postal + city + country)
        ultimate_creditor = '\r\n\r\n\r\n\r\n\r\n\r'
        
        # Transform Amount to string to join
        total_amount = str(invoice.amount_total)
        
        # Get currency name
        currency = invoice.currency_id.name
        # Only CHF and EUR are supported
        if not currency in ["CHF", "EUR"]:
            raise exceptions.except_orm(_('Invalid Currency'), _('Currency must be either CHF or EUR (used %s)') % (currency))
    
        # Get due date
        due_date = invoice.date_due
        # Empty line must contains at least a CR
        if not due_date or len(due_date) == 0:
            due_date = "\r"
        
        # Generate Debtor data
        ultimate_debtor = self._generate_qrbill_contact_data(invoice.partner_id, "Debtor")
        
        # By default, no reference is provided
        ref_type = 'NON'
        ref = '\r'
        if hasattr(invoice, 'bvr_reference') and isinstance(invoice.bvr_reference, basestring):
            # Sanitize the BVR reference by suppressing spaces
            tmp_ref = invoice.bvr_reference.replace(' ', '')
            if tmp_ref and len(tmp_ref) > 0:
                # If the invoice contains bvr_reference and bvr_reference is a string
                ref_type = 'QRR'
                ref = tmp_ref
                # The BVR reference must be 27 characters long
                if not len(ref) == 27:
                    raise exceptions.except_orm(_('Invalid BVR Reference Number'), _('BVR reference number length (%s) must be exactly 27 characters long') % (len(ref)))
                
                # TODO: (Maybe) Enable the validity check with the modulo 10 of the BVR reference number
                #given_chcksm = int(ref[-1:][0])
                #cmptd_chcksm = bvr_checksum(ref[:-1])
                #if given_chcksm != cmptd_chcksm:
                #    raise exceptions.except_orm(_('Invalid BVR Reference Number'), _('BVR reference number modulo 10 must match. (Computed: %s, Given: %s)') % (cmptd_chcksm, given_chcksm))

        # Join data with a NewLine as separator
        return '\n'.join([qr_type, version, coding_type, creditor_iban, creditor, ultimate_creditor, total_amount, currency, due_date, ultimate_debtor, ref_type, ref]).encode('latin-1')
    
    # Generates the address lines for an Odoo partner
    # Role should be one of the following value:
    # - Debtor
    # - Creditor
    # - Ultimate Creditor
    def _generate_qrbill_contact_data(self, contact, role):
        # If the contact is not provided, data can't be retrieved
        if not contact:
            raise exceptions.except_orm(_('Invalid ' + role), _(role + ' is mandatory'))
        
        contact_name = contact.name
        # The name must be provided and non empty
        if not contact_name or len(contact_name) == 0:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s Name'), _(role + '\'s name is mandatory'))
        # The name is maximum 70 characters long
        elif len(contact_name) > 70:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s Name'), _(role + '\'s name "%s" length (%s) must not exceeds 70 characters') % (contact_name, len(contact_name)))
        
        contact_street = contact.street
        # Empty line must contains at least a CR
        if not contact_street or len(contact_street) == 0:
            contact_street = "\r"
        # The street is maximum 70 characters long
        elif len(contact_street) > 70:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s Street'), _(role + '\'s street "%s" length (%s) must not exceeds 70 characters') % (contact_street, len(contact_street)))
        
        contact_house_number = None
        # Empty line must contains at least a CR
        if not contact_house_number or len(contact_house_number) == 0:
            contact_house_number = "\r"
        # The house number is maximum 16 characters long
        elif len(contact_house_number) > 16:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s House Number'), _(role + '\'s house number "%s" length (%s) must not exceeds 16 characters') % (contact_house_number, len(contact_house_number)))
        
        contact_postal_code = contact.zip
        # The postal code is mandatory
        if not contact_postal_code or len(contact_postal_code) == 0:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s Postal Code'), _(role + '\'s postal code is mandatory'))
        # The postal code is maximum 16 characters long
        elif len(contact_postal_code) > 16:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s Postal Code'), _(role + '\'s postal code "%s" length (%s) must not exceeds 16 characters') % (contact_postal_code, len(contact_postal_code)))
        
        contact_city = contact.city
        # The city is mandatory
        if not contact_city or len(contact_city) == 0:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s City'), _(role + '\'s city is mandatory'))
        # The city is maximum 35 characters long
        elif len(contact_city) > 35:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s City'), _(role + '\'s city "%s" length (%s) must not exceeds 35 characters') % (contact_city, len(contact_city)))
        
        contact_country = contact.country_id.code
        # The country code is mandatory
        if not contact_country or len(contact_country) == 0:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s Country Code'), _(role + '\'s country code is mandatory'))
        # The standard uses ISO 3166-1, so the country code must be 2 characters long
        if not len(contact_country) == 2:
            raise exceptions.except_orm(_('Invalid ' + role + '\'s Country Code'), _(role + '\'s country code "%s" length (%s) must be exactly 2 characters long (according to ISO 3166-1)') % (contact_country, len(contact_country)))
        
        # Each fields are separated by a line break
        return '\n'.join([contact_name, contact_street, contact_house_number, contact_postal_code, contact_city, contact_country])

AccountInvoice()