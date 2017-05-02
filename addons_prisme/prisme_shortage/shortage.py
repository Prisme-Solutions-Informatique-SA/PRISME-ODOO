
from openerp import models, fields, tools, api, exceptions, _ 
import datetime

# class utilisee pour lie le bouton de raccourci "product shortage" du produit a sa vue
class product_template(models.Model):
    _inherit = 'product.template'
    
    def action_view_product_shortage(self):
        result = self.env['ir.actions.act_window'].for_xml_id('prisme_shortage', 'action_prisme_product_template_shortage')
        return result

# class utilisee pour lie le bouton de raccourci "product shortage" du produit a sa vue    
class product_product(models.Model):
    _inherit = 'product.product'
        
    def action_view_product_shortage(self):
        result = self.env['ir.actions.act_window'].for_xml_id('prisme_shortage', 'action_prisme_product_template_shortage')
        return result  

class shortage_wizard(models.Model):
    _name = 'prisme.shortage.wizard'

    origin = fields.Char('Origin')
    partner_id = fields.Many2one('res.partner','Partner')
    product_id = fields.Many2one('product.product','Product')
    product_qty = fields.Float('Qty')
    location_id = fields.Many2one('stock.location', 'Src. Loc.')
    location_dest_id = fields.Many2one('stock.location', 'Dest. Loc.')
    date = fields.Date('Date')
    state =  fields.Selection([('actual','Actual'),('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Confirmed'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Cancelled')], 'State', readonly=True, select=True)
    qtysum = fields.Float('Forecast')
    sign = fields.Char('s')
    qtysumshort = fields.Float('Foreca. Short')

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
      if view_type == 'tree':
        #Recuperation de l'id du produits
        product_ids = None
        template_id = None
        context = self.env.context
        if context != None:
            try:
                product_ids = [context['product_id']]
            except Exception as exp:
                try:
                    template_id = context['template_id']
                    obj_products = self.env['product.product']
                    product_ids = obj_products.search([('product_tmpl_id','=',template_id)])
                except Exception as exp:
                    product_ids = None
                    template_id = None
        try:        
            act_mod = context['active_model']
            #Pour l impression on ne supprime rien, on ne cree rien
            if act_mod == 'prisme.shortage.wizard' :
                result = super(shortage_wizard,self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
                return result
        except Exception:
            #Continue to work if no active model
            noexceptionthrowed=[]
        #Preparation des donnees du report
        if product_ids != None:
            #Nettoyage
            self.env.cr.execute('delete from prisme_shortage_wizard where create_uid=%s',(str(self.env.user.id),))
            #Recuperation des warehouses-stock racine
            stock_main_ids = []
            self.env.cr.execute("select lot_stock_id from stock_warehouse")
            stock_main_ids = map(lambda x: x[0], self.env.cr.fetchall())
            #Recuperation des ids des emplacements de stocks inclus                 
            stock_location = self.env['stock.location']
            stock_ids = []
            for parent_id in stock_main_ids:                    #Parcours des ids parents
                if stock_ids.count(parent_id) == 0:             #Ajout uniquement si non present
                    stock_ids.append(parent_id)
                last_len = 0
                while last_len != len(stock_ids):
                    last_len = len(stock_ids)
                    for stockid in stock_ids:
                        ids = stock_location.search([('location_id','=',stockid),])
                        for id in ids:
                            if stock_ids.count(id.id) == 0:
                                stock_ids.append(id.id)
                                
            
            for product_id in product_ids:
                #Recuperation des mouvements de stock du produits
                stock_move = self.env['stock.move']
                move_ids = stock_move.search([('product_id','=',product_id.id),('state','not in',['done','cancel'])],order='date')
                
                #Creation des objets pour affichage
                qtysum = 0.0
                qtysumshort = 0.0
                #On initialise de la calcul de la qty des prevision avec la qty actuelle de produit en stock et on ajoute la 1er ligne real stock
                qtysum= product_id.qty_available   
                qtysumshort = qtysum
                self.create({'origin':'Actual real stock:','product_qty':qtysum,'qtysum':qtysum,'qtysumshort':qtysum,'product_id':product_id.id,'state':'actual'})
                #Pour chaque futur mouvement    
                for moveid in move_ids:
                    move = moveid
                    src_id = move.location_id.id
                    dst_id = move.location_dest_id.id
                    #Mouvement interne donc pas affiche
                    if (stock_ids.count(src_id) != 0) and (stock_ids.count(dst_id) != 0):
                        continue
                    #Mouvement externe donc pas affiche
                    if (stock_ids.count(src_id) == 0) and (stock_ids.count(dst_id) == 0):
                        continue
                    #Mouvement externe vers interne, on additionne (entree)
                    if (stock_ids.count(src_id) == 0) and (stock_ids.count(dst_id) != 0):
                        qtysum = qtysum + move.product_qty
                        sign = '+'
                    #Mouvement interne vers externe, on soustrait (sortie)  
                    if (stock_ids.count(src_id) != 0) and (stock_ids.count(dst_id) == 0):
                        qtysum = qtysum - move.product_qty
                        qtysumshort = qtysumshort - move.product_qty
                        sign = '-'
                    if move.origin == False:
                        move.origin = ''
                    if move.partner_id == False:
                        move.partner_id = [None] 
                    if move.origin =='':
                        move.origin = move.name
                    self.create({'sign':sign,'origin': move.origin, 'partner_id': move.partner_id.id, 'product_id': product_id.id, 'product_qty': move.product_qty, 'location_id':move.location_id.id,'location_dest_id':move.location_dest_id.id, 'date':move.date,'state':move.state,'qtysum':qtysum,'qtysumshort':qtysumshort,})
        #Envoi l'affichage de la vue
      result = super(shortage_wizard,self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
      return result

##############################################################################################################################################################

class shortage_all(models.Model):
    _name = 'prisme.shortage.all'

    origin = fields.Char('Origin')
    partner_id = fields.Many2one('res.partner','Partner')
    product_id = fields.Many2one('product.product','Product')
    product_qty = fields.Float('Qty')
    location_id = fields.Many2one('stock.location', 'Src. Loc.')
    location_dest_id = fields.Many2one('stock.location', 'Dest. Loc.')
    date = fields.Date('Date')
    state = fields.Selection([('actual','Actual'),('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Confirmed'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Cancelled')], 'State', readonly=True, select=True)
    qtysum = fields.Float('Forecast')
    sign = fields.Char('s',size=1)
    qtysumshort = fields.Float('Foreca. Short')
    

    def getStockBreakProducts(self):
        product_product = self.env['product.product']
        products_ids = product_product.search([])
        result = []
        for product in products_ids:
            if product.virtual_available<0:
                result.append(product)
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
      #a vraiment ameliorer!!! mais ces fonctions n existent meme po :-(((
      #self.createSQL(cr)   
      if view_type == 'tree':
        #Si impression on ne fait rien
        if toolbar==False:
            result = super(shortage_all,self).fields_view_get(view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
            return result
        self.env.cr.execute('delete from prisme_shortage_all where create_uid=%s',(str(self.env.user.id),)) #Nettoyage
        #Recuperation des warehouses-stock racine
        stock_main_ids = []
        self.env.cr.execute("select lot_stock_id from stock_warehouse")
        stock_main_ids = map(lambda x: x[0], self.env.cr.fetchall())
        #Recuperation des ids des emplacements de stocks inclus
        stock_location = self.env['stock.location']
        stock_ids = []
        for parent_id in stock_main_ids:
            if stock_ids.count(parent_id) == 0:
                stock_ids.append(parent_id)
            last_len = 0
            while last_len != len(stock_ids):
                last_len = len(stock_ids)
                for stockid in stock_ids:
                    ids = stock_location.search([('location_id','=',stockid),])
                    for id in ids:
                        if stock_ids.count(id.id) == 0:
                            stock_ids.append(id.id)
        #Pour chaque produit en rupture
        product_ids = self.getStockBreakProducts()
        product_product=self.env['product.product']
        for product_id in product_ids:  
        #Preparation des donnees du report
            if product_id != None:
                #Recuperation des mouvements de stock du produits
                stock_move = self.env['stock.move']
                move_ids = stock_move.search([('product_id','=',product_id.id),('state','not in',['done','cancel'])],order='date')
                 
                #Creation des objets pour affichage
                qtysum = 0.0
                qtysumshort = 0.0
                #On initialise de la calcul de la qty des prevision avec la qty actuelle de produit en stock et on ajoute la 1er ligne real stock
                qtysum= product_id.qty_available
                qtysumshort = qtysum
                self.create({'origin':'Actual real stock:','product_qty':qtysum,'qtysum':qtysum,'qtysumshort':qtysum,'product_id':product_id.id,'state':'actual'})
                #Pour chaque futur mouvement    
                for moveid in move_ids:
                    move = moveid
                    src_id = move.location_id.id
                    dst_id = move.location_dest_id.id
                    #Mouvement interne donc pas affiche
                    if (stock_ids.count(src_id) != 0) and (stock_ids.count(dst_id) != 0):
                        continue
                    #Mouvement externe donc pas affiche
                    if (stock_ids.count(src_id) == 0) and (stock_ids.count(dst_id) == 0):
                        continue
                    #Mouvement externe vers interne, on additionne (entree)
                    if (stock_ids.count(src_id) == 0) and (stock_ids.count(dst_id) != 0):
                        qtysum = qtysum + move.product_qty
                        sign = '+'
                    #Mouvement interne vers externe, on soustrait (sortie)  
                    if (stock_ids.count(src_id) != 0) and (stock_ids.count(dst_id) == 0):
                        qtysum = qtysum - move.product_qty
                        qtysumshort = qtysumshort - move.product_qty
                        sign = '-'
                    if move.origin == False:
                        move.origin = ''
                    if move.origin =='':
                        move.origin = move.name
                    self.create({'sign':sign,'origin': move.origin, 'partner_id': move.partner_id.id, 'product_id': product_id.id, 'product_qty': move.product_qty, 'location_id':move.location_id.id,'location_dest_id':move.location_dest_id.id, 'date':move.date,'state':move.state,'qtysum':qtysum,'qtysumshort':qtysumshort,})
        #Envoi l'affichage de la vue
      result = super(shortage_all,self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
      return result
    
        #Devrait etre execute a l installation du module !!!!
    def init(self):
      try:  
        self.env.cr.execute('''
        CREATE OR REPLACE FUNCTION first_element_state(anyarray, anyelement)
          RETURNS anyarray AS
        $$
            SELECT CASE WHEN array_upper($1,1) IS NULL THEN array_append($1,$2) ELSE $1 END;
        $$
          LANGUAGE 'sql' IMMUTABLE;

        CREATE OR REPLACE FUNCTION first_element(anyarray)
          RETURNS anyelement AS
        $$
            SELECT ($1)[1] ;
        $$
          LANGUAGE 'sql' IMMUTABLE;

        CREATE OR REPLACE FUNCTION last_element(anyelement, anyelement)
          RETURNS anyelement AS
        $$
            SELECT $2;
        $$
          LANGUAGE 'sql' IMMUTABLE;
      
        CREATE AGGREGATE first(anyelement) (
          SFUNC=first_element_state,
          STYPE=anyarray,
          FINALFUNC=first_element
          )
        ;

        CREATE AGGREGATE last(anyelement) (
          SFUNC=last_element,
          STYPE=anyelement
        );
        ''')
      except Exception:
        self.env.cr.execute('commit;')
        
        
    # redefinit uniquement pour ce module afin de pouvoir ecrire une "query" qui fonctionne (celle de base fait des regroupements qu'on ne veut pas).     
    @api.model
    def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        self.check_access_rights('read')
        query = self._where_calc(domain)
        fields = fields or [f.name for f in self._fields.itervalues() if f.store]

        groupby = [groupby] if isinstance(groupby, basestring) else list(OrderedSet(groupby))
        groupby_list = groupby[:1] if lazy else groupby
        annotated_groupbys = [self._read_group_process_groupby(gb, query) for gb in groupby_list]
        groupby_fields = [g['field'] for g in annotated_groupbys]
        order = orderby or ','.join([g for g in groupby_list])
        groupby_dict = {gb['groupby']: gb for gb in annotated_groupbys}

        self._apply_ir_rules(query, 'read')
        for gb in groupby_fields:
            assert gb in fields, "Fields in 'groupby' must appear in the list of fields to read (perhaps it's missing in the list view?)"
            assert gb in self._fields, "Unknown field %r in 'groupby'" % gb
            gb_field = self._fields[gb].base_field
            assert gb_field.store and gb_field.column_type, "Fields in 'groupby' must be regular database-persisted fields (no function or related fields), or function fields with store=True"

        aggregated_fields = [
            f for f in fields
            if f != 'sequence'
            if f not in groupby_fields
            for field in [self._fields.get(f)]
            if field
            if field.group_operator
            if field.base_field.store and field.base_field.column_type
        ]

        field_formatter = lambda f: (
            self._fields[f].group_operator,
            self._inherits_join_calc(self._table, f, query),
            f,
        )
        select_terms = ['%s(%s) AS "%s" ' % field_formatter(f) for f in aggregated_fields]

        for gb in annotated_groupbys:
            select_terms.append('%s as "%s" ' % (gb['qualified_field'], gb['groupby']))

        groupby_terms, orderby_terms = self._read_group_prepare(order, aggregated_fields, annotated_groupbys, query)
        from_clause, where_clause, where_clause_params = query.get_sql()
        if lazy and (len(groupby_fields) >= 2 or not self._context.get('group_by_no_leaf')):
            count_field = groupby_fields[0] if len(groupby_fields) >= 1 else '_'
        else:
            count_field = '_'
        count_field += '_count'

        prefix_terms = lambda prefix, terms: (prefix + " " + ",".join(terms)) if terms else ''
        prefix_term = lambda prefix, term: ('%s %s' % (prefix, term)) if term else ''
        
        
        
        # requete modifiee et tres statique (fonctionne que pour ce module)
        query = """
            SELECT min(prisme_shortage_all.id) AS id, count(prisme_shortage_all.id) AS product_id_count , first("prisme_shortage_all"."product_qty") AS product_qty,last("prisme_shortage_all"."qtysum") AS qtysum,last("prisme_shortage_all"."qtysumshort") AS qtysumshort,"prisme_shortage_all"."product_id" as "product_id"
            FROM "prisme_shortage_all" LEFT JOIN "product_product" as "prisme_shortage_all__product_id" ON ("prisme_shortage_all"."product_id" = "prisme_shortage_all__product_id"."id")
            %(where)s
            GROUP BY "prisme_shortage_all"."product_id"
            ORDER BY id
        """ % {
            'where': prefix_term('WHERE', where_clause),
        }
        
        self._cr.execute(query, where_clause_params)
        fetched_data = self._cr.dictfetchall()

        if not groupby_fields:
            return fetched_data

        many2onefields = [gb['field'] for gb in annotated_groupbys if gb['type'] == 'many2one']
        if many2onefields:
            data_ids = [r['id'] for r in fetched_data]
            many2onefields = list(set(many2onefields))
            data_dict = {d['id']: d for d in self.browse(data_ids).read(many2onefields)}
            for d in fetched_data:
                d.update(data_dict[d['id']])

        data = map(lambda r: {k: self._read_group_prepare_data(k,v, groupby_dict) for k,v in r.iteritems()}, fetched_data)
        result = [self._read_group_format_result(d, annotated_groupbys, groupby, domain) for d in data]
        if lazy:
            # Right now, read_group only fill results in lazy mode (by default).
            # If you need to have the empty groups in 'eager' mode, then the
            # method _read_group_fill_results need to be completely reimplemented
            # in a sane way 
            result = self._read_group_fill_results(
                domain, groupby_fields[0], groupby[len(annotated_groupbys):],
                aggregated_fields, count_field, result, read_group_order=order,
            )
        return result


