from openerp.osv import fields, osv, expression


class prisme_warranty_type(osv.osv):
    _name = "prisme.warranty.type"
    
    _columns = {
        "name": fields.char("Name", 255, required=True, unique=True),
        "description": fields.text("Description"),
    }
    
    _sql_constraints = [("name_uniq", "unique(name)", "Type must be unique")]

prisme_warranty_type()
