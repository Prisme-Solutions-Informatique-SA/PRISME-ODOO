# -*- coding: utf-8 -*-
from osv import osv, fields

class document_page(osv.Model):
    _name = 'document.page'
    _inherit = ["pad.common", "document.page"]

    _order = 'numbering asc'



    def _get_selection(self, cursor, user_id, context=None):
        return (
                ('todo', 'A faire'),
                ('inprogress', 'En cours'),
                ('tovalidate', 'A valider'),
                ('done', u'Terminé'))

    _columns = {
        'numbering': fields.char("Sequence", 255,required=False,translate=False),
        'state' : fields.selection(_get_selection, 'Status'),
        'content_pad': fields.char('Content PAD', pad_content_field='content')
    }

    def _get_page_index(self, cr, uid, page, link=True):
        level = 0
        return self._get_page_index_sublevels(cr, uid, page, level, link=False)

    def _get_page_index_sublevels(self, cr, uid, page, level, link=True):
        index = []
        for subpage in page.child_ids:
            index += [''+ self._get_page_index_sublevels(cr, uid, subpage, level+1)]
        r = ''
        if link:
            indent = 20*level
            fontsize = 24-2*level
            docstate = ""
            if fontsize < 16:
                fontsize = 16
            if page.state != False and page.state != 'done':
                possible_states = self._get_selection(self, cr, uid)
                if page.state == 'todo':
                        docstate = possible_states[0][1]
                elif page.state == 'inprogress':
                        docstate = possible_states[1][1]
                elif page.state == 'tovalidate':
                        docstate = possible_states[2][1]
                docstate = '['+docstate+']'
            style = "font-size:%ipx;padding-left:%ipx;"%(fontsize,indent)
            numbering = ''
            if page.numbering:
                numbering = page.numbering
            if page.type == "category":
                style = style + "color: #0000dd;"
            else:
                style = style + "color: #000000;"
            r = '<a href="#id=%s" class="level%s category" style="%s">%s %s %s</a><br>'%(page.id,level,style,numbering,page.name, docstate)
        if index:
            r += "" + "".join(index) + ""
        return r

    def _get_display_content(self, cr, uid, ids, name, args, context=None):
        res = {}
        for page in self.browse(cr, uid, ids, context=context):
            if page.type == "category":
               content = self._get_page_index(cr, uid, page, link=False)
            else:
               content = page.content
            res[page.id] =  content
        return res

document_page()

