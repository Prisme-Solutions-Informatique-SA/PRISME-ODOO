# -*- coding: utf-8 -*-

import datetime
import tools
from osv import osv, fields
import prisme_file_logger
import logging

class prisme_postit_tag(osv.osv):
    _name = "prisme.postit.tag"
    _description = "Postit Tag"
    _columns = {
        'name' : fields.char('Tag Name', required=True),
    }
prisme_postit_tag()
