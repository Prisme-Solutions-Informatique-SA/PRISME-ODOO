####################################################################################
#                                                                                  #
# PROJECT NAME   : MISE EN OEUVRE D'OPENERP                                        #
# APPLIANCE      : ---                                                             #
# ESTABLISHED BY : DAMIEN RAEMY                                                    #
# COMPANY        : PRISME INFORMATIQUE                                             #
# DATE           : NOVEMBRE 2010                                                   #
#                                                                                  #
####################################################################################
#                                                                                  #
# FUNCTIUN       : DESCRIBE THE MODULE'S PRINCIPAL CARACTERISTICS                  #
#                                                                                  #
####################################################################################

{
    'name': 'Prisme Timesheet Enhancement',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
    Prisme - specific developments
    --------------------------------------------------------------------------------

    Add features to manage human resources:
    * More information for the working hours (beginning, end, 
      internal description)
    * Customer display for the working hours
    * Period hours in timesheet management

    For more informations:
    damien.raemy@prisme.ch
    """,
    'author': 'Damien Raemy | Prisme Solutions Informatique SA',
    'website': 'http://www.prisme.ch',
    'depends': [
        'hr_timesheet',
        'hr_timesheet_sheet',
        'hr_timesheet_invoice',        
        ],
    'init_xml': [],
    'update_xml': [
        'view_hr_timesheet_line.xml',
        'view_hr_timesheet_sheet.xml',
        'view_account_analytic_line.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}