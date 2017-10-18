# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, tools

class MailAddAttachment(models.Model):
    _name = "mail.add.attachment"
    _description = 'Email Templates Additional Report Attachments'
    
    report_template = fields.Many2one('ir.actions.report.xml', 'Optional report to print and attach')
    report_name = fields.Char('Report Filename', translate=True,
                              help="Name to use for the generated report file (may contain placeholders)\n"
                                   "The extension can be omitted and will then come from the report type.")
    template_id = fields.Many2one('mail.template', string='Template', ondelete='cascade')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: