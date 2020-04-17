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
#    Project ID:    OERP-002-08
#    Phabricator:   T499
#
##########################################################################

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
        # Use Version 2 (0200)
        version = '0200'
        # Encoding: Latin-1 (1)
        coding_type = '1'
        
        # If the bank id is not set, the IBAN doesn't exist
        if not invoice.partner_bank_id:
            raise exceptions.except_orm('Invalid IBAN', 'You must specify an IBAN')
        creditor_iban = invoice.partner_bank_id.sanitized_acc_number
        # If the IBAN is not a string or is empty, the IBAN is invalid
        if (not isinstance(creditor_iban, basestring)) or (len(creditor_iban) == 0):
            raise exceptions.except_orm('Invalid IBAN', 'You must specify an IBAN')
        # The QR-bill support only IBAN starting with "CH" and "LI"
        elif not (creditor_iban.startswith("CH") or creditor_iban.startswith("LI")):
            raise exceptions.except_orm('Invalid IBAN', 'Only IBANs starting with CH or LI are permitted.')
        # The IBAN must be exactly 21 characters
        elif not len(creditor_iban) == 21:
            raise exceptions.except_orm('Invalid IBAN', 'IBAN length must be exactly 21 characters long')
        
        # Generate Creditor data
        creditor = self._generate_qrbill_contact_data(invoice.company_id.partner_id, "Creditor")
        
        # Generate Ultimate Creditor data. v2 specifications state that we mustn't fill in those fields, but send an empty line.
        # 6 NewLine (\n) because the 7th is generated in the join function located at the end of this def.
        # Adding 7 carriage returns, 1 for each new line.
        # (adress type + name + street + number + postal + city + country)
        ultimate_creditor = '\r\n\r\n\r\n\r\n\r\n\r\n\r'
        
        # Transform Amount to string to join
        total_amount = str(invoice.amount_total)
        
        # Get currency name
        currency = invoice.currency_id.name
        # Only CHF and EUR are supported
        if not currency in ["CHF", "EUR"]:
            raise exceptions.except_orm('Invalid Currency', 'Currency must be either CHF or EUR')
    
        ### Due date was originally added in v1, but removed in v2 ###
        # Get due date
        #due_date = invoice.date_due
        # Empty line must contains at least a CR
        #if not due_date or len(due_date) == 0:
        #    due_date = "\r"
        
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
                    raise exceptions.except_orm('Invalid BVR Reference Number', 'BVR reference number length must be exactly 27 characters long')
                
        # Used for payment purpose or additionnal textual informations. Not implemented yet.
        unstructured_message = '\r' 
        
        # EPD stands for End Payment Data.
        trailer = 'EPD'
        
        # Bill information contains coded data for automated booking of the payment. This isn't forwarded with the payment. Not implemented yet.
        bill_information = '\r'
        
        # Alternative schemes. We keep it empty for now.
        alternative_scheme_1 = '\r'
        alternative_scheme_2 = '\r'
        
        # Join data with a NewLine as separator
        # Below line was used for the v1 of qr-bill
        # '\n'.join([qr_type, version, coding_type, creditor_iban, creditor, ultimate_creditor, total_amount, currency, due_date, ultimate_debtor, ref_type, ref]).encode('latin-1')
        
        # Creating qr-bill informations given to the SIX v2.1 specifications
        return '\n'.join([
            qr_type, 
            version, 
            coding_type, 
            creditor_iban, 
            creditor, 
            ultimate_creditor, 
            total_amount, 
            currency,
            ultimate_debtor, 
            ref_type, 
            ref,
            unstructured_message,
            trailer,
            bill_information,
            alternative_scheme_1,
            alternative_scheme_2
            ]).encode('latin-1')
        
    
    # Generates the address lines for an Odoo partner
    # Role should be one of the following value:
    # - Debtor
    # - Creditor
    # - Ultimate Creditor
    def _generate_qrbill_contact_data(self, contact, role):
        # If the contact is not provided, data can't be retrieved
        if not contact:
            raise exceptions.except_orm('Invalid ' + role, role + ' is mandatory')
        
        if (not contact.is_company) and contact.parent_id.name:
            contact_name = contact.parent_id.name
        else:
            contact_name = contact.name
        # The name must be provided and non empty
        if not contact_name or len(contact_name) == 0:
            raise exceptions.except_orm("Invalid " + role + "'s Name", role + "'s name is mandatory")
        # The name is maximum 70 characters long
        elif len(contact_name) > 70:
            raise exceptions.except_orm("Invalid " + role + "'s Name", role + "'s name length must not exceed 70 characters")
        
        contact_street_and_nb = contact.street
        # Empty line must contains at least a CR
        if not contact_street_and_nb or len(contact_street_and_nb) == 0:
            contact_street_and_nb = "\r"
        # The street is maximum 70 characters long
        elif len(contact_street_and_nb) > 70:
            raise exceptions.except_orm("Invalid " + role + "'s Street", role + "'s street length must not exceed 70 characters")
        
        contact_postal_code = contact.zip
        # The postal code is mandatory
        if not contact_postal_code or len(contact_postal_code) == 0:
            raise exceptions.except_orm('Invalid ' + role + '\'s Postal Code', role + '\'s postal code is mandatory')
        
        contact_city = contact.city
        # The city is mandatory
        if not contact_city or len(contact_city) == 0:
            raise exceptions.except_orm('Invalid ' + role + '\'s City', role + '\'s city is mandatory')
        
        # The city and zip is maximum 70 characters long
        contact_zip_and_city = contact_postal_code + ' ' + contact_city
        if len(contact_zip_and_city) > 70 :
            raise exceptions.except_orm('Invalid ' + role + '\'s City', role + '\'s city length must not exceeds 70 characters')
        
        contact_country = contact.country_id.code
        # The country code is mandatory
        if not contact_country or len(contact_country) == 0:
            raise exceptions.except_orm('Invalid ' + role + '\'s Country Code', role + '\'s country code is mandatory')
        # The standard uses ISO 3166-1, so the country code must be 2 characters long
        if not len(contact_country) == 2:
            raise exceptions.except_orm('Invalid ' + role + '\'s Country Code', role + '\'s country code length must be exactly 2 characters long.')
        
        # Each fields are separated by a line break.
        return '\n'.join([
            'K', #address type : combined address
            contact_name,
            contact_street_and_nb, 
            contact_zip_and_city, 
            # below 2 lines must be empty with a K address type
            '\r',
            '\r',
            contact_country
            ])

AccountInvoice()