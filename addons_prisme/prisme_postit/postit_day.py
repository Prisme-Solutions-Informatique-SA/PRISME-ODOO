# -*- coding: utf-8 -*-

import datetime
import tools
from osv import osv, fields
import prisme_file_logger
import logging

class prisme_postit_day(osv.osv):
    _name = "prisme.postit.day"
    _description = "Postit Day"
    _columns = {
        'name' : fields.char('Day Name', required=True, translate=True),
        'nbr' : fields.integer('Day number', required=True),
    }
prisme_postit_day()
