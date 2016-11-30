from openerp.osv import fields,osv
import datetime

# class utilisee pour lie le bouton de raccourci "product shortage" du produit a sa vue
class product_template(osv.Model):
    _inherit = 'product.template'
        
    def action_view_product_shortage(self, cr, uid, ids, context=None):
        product_ids = []
        for template in self.browse(cr, uid, ids, context=context):
            product_ids += [x.id for x in template.product_variant_ids]
        result = self.pool.get('ir.model.data').xmlid_to_res_id(cr, uid, 'prisme_shortage.action_prisme_product_template_shortage',raise_if_not_found=True)        
        result = self.pool.get('ir.actions.act_window').read(cr, uid, [result], context=context)[0]
        result['domain'] = "[('product_id','in',[" + ','.join(map(str, product_ids)) + "])]"
        return result

# class utilisee pour lie le bouton de raccourci "product shortage" du produit a sa vue    
class product_product(osv.Model):
    _inherit = 'product.product'
        
    def action_view_product_shortage(self, cr, uid, ids, context=None):
        result = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'prisme_shortage.action_prisme_product_product_shortage', raise_if_not_found=True)
        result = self.pool['ir.actions.act_window'].read(cr, uid, [result], context=context)[0]
        result['domain'] = "[('product_id','in',[" + ','.join(map(str, ids)) + "])]"
        return result
    
    

class shortage_wizard(osv.osv):
    _name = 'prisme.shortage.wizard'
    _columns = {
        'origin' : fields.char('Origin', size=15),
        'partner_id' : fields.many2one('res.partner','Partner'),
        'product_id' : fields.many2one('product.product','Product'),
        'product_qty' : fields.float('Qty'),
        'location_id' : fields.many2one('stock.location', 'Src. Loc.'),
        'location_dest_id':fields.many2one('stock.location', 'Dest. Loc.'),
        'date' : fields.date('Date'),
        'state':  fields.selection([('actual','Actual'),('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Confirmed'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Cancelled')], 'State', readonly=True, select=True),
        'qtysum': fields.float('Forecast'),
        'sign': fields.char('s',size=1),
        'qtysumshort': fields.float('Foreca. Short'),
    }

    def fields_view_get(self, cr, user, view_id=None, view_type=None, context=None, toolbar=False, submenu=False):  
      if view_type == 'tree':
        #Recuperation de l'id du produits
        product_ids = None
        template_id = None
        if context != None:
            try:
                product_ids = [context['product_id']]
            except Exception as exp:
                try:
                    template_id = context['template_id']
                    obj_products = self.pool.get('product.product')
                    product_ids = obj_products.search(cr,user,[('product_tmpl_id','=',template_id)])
                except Exception as exp:
                    product_ids = None
                    template_id = None
        try:        
            act_mod = context['active_model']
            #Pour l impression on ne supprime rien, on ne cree rien
            if act_mod == 'prisme.shortage.wizard' :
                result = super(shortage_wizard,self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
                return result
        except Exception:
            #Continue to work if no active model
            noexceptionthrowed=[]
        #Preparation des donnees du report
        if product_ids != None:
            #Nettoyage
            cr.execute('delete from prisme_shortage_wizard where create_uid=%s',(str(user),))
            #Recuperation des warehouses-stock racine
            stock_main_ids = []
            cr.execute("select lot_stock_id from stock_warehouse")
            stock_main_ids = map(lambda x: x[0], cr.fetchall())
            #Recuperation des ids des emplacements de stocks inclus                 
            stock_location = self.pool.get('stock.location')
            stock_ids = []
            for parent_id in stock_main_ids:                    #Parcours des ids parents
                if stock_ids.count(parent_id) == 0:             #Ajout uniquement si non present
                    stock_ids.append(parent_id)
                last_len = 0
                while last_len != len(stock_ids):
                    last_len = len(stock_ids)
                    for stockid in stock_ids:
                        ids = stock_location.search(cr,user,[('location_id','=',stockid),])
                        for id in ids:
                            if stock_ids.count(id) == 0:
                                stock_ids.append(id)
                                
            
            for product_id in product_ids:
                #Recuperation des mouvements de stock du produits
                stock_move = self.pool.get('stock.move')
                move_ids = stock_move.search(cr,user,[('product_id','=',product_id),('state','not in',['done','cancel'])],order='date')
                
                #Creation des objets pour affichage
                qtysum = 0.0
                qtysumshort = 0.0
                #On initialise de la calcul de la qty des prevision avec la qty actuelle de produit en stock et on ajoute la 1er ligne real stock
                product_product = self.pool.get('product.product')
                qtysum= product_product.read(cr,user,[product_id],['qty_available'])[0]['qty_available']    
                qtysumshort = qtysum
                self.create(cr,user,{'origin':'Actual real stock:','product_qty':qtysum,'qtysum':qtysum,'qtysumshort':qtysum,'product_id':product_id,'state':'actual'})
                #Pour chaque futur mouvement    
                for moveid in move_ids:
                    move = stock_move.read(cr, user, [moveid],['location_id','location_dest_id','product_qty','origin','partner_id','date','state','name'])[0]
                    src_id = move['location_id'][0]
                    dst_id = move['location_dest_id'][0]
                    #Mouvement interne donc pas affiche
                    if (stock_ids.count(src_id) != 0) and (stock_ids.count(dst_id) != 0):
                        continue
                    #Mouvement externe donc pas affiche
                    if (stock_ids.count(src_id) == 0) and (stock_ids.count(dst_id) == 0):
                        continue
                    #Mouvement externe vers interne, on additionne (entree)
                    if (stock_ids.count(src_id) == 0) and (stock_ids.count(dst_id) != 0):
                        qtysum = qtysum + move['product_qty']
                        sign = '+'
                    #Mouvement interne vers externe, on soustrait (sortie)  
                    if (stock_ids.count(src_id) != 0) and (stock_ids.count(dst_id) == 0):
                        qtysum = qtysum - move['product_qty']
                        qtysumshort = qtysumshort - move['product_qty']
                        sign = '-'
                    if move['origin'] == False:
                        move['origin'] = ''
                    if move['partner_id'] == False:
                        move['partner_id'] = [None] 
                    if move['origin'] =='':
                        move['origin'] = move['name']
                    self.create(cr,user,{'sign':sign,'origin': move['origin'], 'partner_id': move['partner_id'][0], 'product_id': product_id, 'product_qty': move['product_qty'], 'location_id':move['location_id'][0],'location_dest_id':move['location_dest_id'][0], 'date':move['date'],'state':move['state'],'qtysum':qtysum,'qtysumshort':qtysumshort,})
        #Envoi l'affichage de la vue
      result = super(shortage_wizard,self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
      return result

shortage_wizard()

##############################################################################################################################################################

class shortage_all(osv.Model):
    _name = 'prisme.shortage.all'
    _columns = {
        'origin' : fields.char('Origin', size=30),
        'partner_id' : fields.many2one('res.partner','Partner'),
        'product_id' : fields.many2one('product.product','Product'),
        'product_qty' : fields.float('Qty'),
        'location_id' : fields.many2one('stock.location', 'Src. Loc.'),
        'location_dest_id':fields.many2one('stock.location', 'Dest. Loc.'),
        'date' : fields.date('Date'),
        'state':  fields.selection([('actual','Actual'),('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Confirmed'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Cancelled')], 'State', readonly=True, select=True),
        'qtysum': fields.float('Forecast'),
        'sign': fields.char('s',size=1),
        'qtysumshort': fields.float('Foreca. Short'),
    }

    def getStockBreakProducts(self, cr, user):
        product_product=self.pool.get('product.product')
        products_ids = product_product.search(cr, user, [])
        result = []
        for id in products_ids:
            if product_product.read(cr,user,[id],['virtual_available'])[0]['virtual_available']<0:
                result.append(id)
        return result

    def fields_view_get(self, cr, user, view_id=None, view_type=None, context=None, toolbar=False, submenu=False):
      #a vraiment ameliorer!!! mais ces fonctions n existent meme po :-(((
      #self.createSQL(cr)   
      if view_type == 'tree':
        #Si impression on ne fait rien
        if toolbar==False:
            result = super(shortage_all,self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
            return result
        cr.execute('delete from prisme_shortage_all where create_uid=%s',(str(user),)) #Nettoyage
        #Recuperation des warehouses-stock racine
        stock_main_ids = []
        cr.execute("select lot_stock_id from stock_warehouse")
        stock_main_ids = map(lambda x: x[0], cr.fetchall())
        #Recuperation des ids des emplacements de stocks inclus
        stock_location = self.pool.get('stock.location')
        stock_ids = []
        for parent_id in stock_main_ids:
            if stock_ids.count(parent_id) == 0:
                stock_ids.append(parent_id)
            last_len = 0
            while last_len != len(stock_ids):
                last_len = len(stock_ids)
                for stockid in stock_ids:
                    ids = stock_location.search(cr,user,[('location_id','=',stockid),])
                    for id in ids:
                        if stock_ids.count(id) == 0:
                            stock_ids.append(id)
        #Pour chaque produit en rupture
        product_ids = self.getStockBreakProducts(cr,user)
        product_product=self.pool.get('product.product')
        for product_id in product_ids:  
        #Preparation des donnees du report
            if product_id != None:
                #Recuperation des mouvements de stock du produits
                stock_move = self.pool.get('stock.move')
                move_ids = stock_move.search(cr,user,[('product_id','=',product_id),('state','not in',['done','cancel'])],order='date')
                 
                #Creation des objets pour affichage
                qtysum = 0.0
                qtysumshort = 0.0
                #On initialise de la calcul de la qty des prevision avec la qty actuelle de produit en stock et on ajoute la 1er ligne real stock
                qtysum= product_product.read(cr,user,[product_id],['qty_available'])[0]['qty_available']
                qtysumshort = qtysum
                self.create(cr,user,{'origin':'Actual real stock:','product_qty':qtysum,'qtysum':qtysum,'qtysumshort':qtysum,'product_id':product_id,'state':'actual'})
                #Pour chaque futur mouvement    
                for moveid in move_ids:
                    move = stock_move.read(cr, user, [moveid],['location_id','location_dest_id','product_qty','origin','partner_id','date','state','name'])[0]
                    src_id = move['location_id'][0]
                    dst_id = move['location_dest_id'][0]
                    #Mouvement interne donc pas affiche
                    if (stock_ids.count(src_id) != 0) and (stock_ids.count(dst_id) != 0):
                        continue
                    #Mouvement externe donc pas affiche
                    if (stock_ids.count(src_id) == 0) and (stock_ids.count(dst_id) == 0):
                        continue
                    #Mouvement externe vers interne, on additionne (entree)
                    if (stock_ids.count(src_id) == 0) and (stock_ids.count(dst_id) != 0):
                        qtysum = qtysum + move['product_qty']
                        sign = '+'
                    #Mouvement interne vers externe, on soustrait (sortie)  
                    if (stock_ids.count(src_id) != 0) and (stock_ids.count(dst_id) == 0):
                        qtysum = qtysum - move['product_qty']
                        qtysumshort = qtysumshort - move['product_qty']
                        sign = '-'
                    if move['origin'] == False:
                        move['origin'] = ''
                    if move['partner_id'] == False:
                        move['partner_id'] = [None]
                    if move['origin'] =='':
                        move['origin'] = move['name']
                    self.create(cr,user,{'sign':sign,'origin': move['origin'], 'partner_id': move['partner_id'][0], 'product_id': product_id, 'product_qty': move['product_qty'], 'location_id':move['location_id'][0],'location_dest_id':move['location_dest_id'][0], 'date':move['date'],'state':move['state'],'qtysum':qtysum,'qtysumshort':qtysumshort,})
        #Envoi l'affichage de la vue
      result = super(shortage_all,self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
      return result
     
    # redefinit uniquement pour ce module afin de pouvoir ecrire une "query" qui fonctionne (celle de base fait des regroupements qu'on ne veut pas).  
    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        """
        Get the list of records in list view grouped by the given ``groupby`` fields
  
        :param cr: database cursor
        :param uid: current user id
        :param domain: list specifying search criteria [['field_name', 'operator', 'value'], ...]
        :param list fields: list of fields present in the list view specified on the object
        :param list groupby: list of groupby descriptions by which the records will be grouped.  
                A groupby description is either a field (then it will be grouped by that field)
                or a string 'field:groupby_function'.  Right now, the only functions supported
                are 'day', 'week', 'month', 'quarter' or 'year', and they only make sense for 
                date/datetime fields.
        :param int offset: optional number of records to skip
        :param int limit: optional max number of records to return
        :param dict context: context arguments, like lang, time zone. 
        :param list orderby: optional ``order by`` specification, for
                             overriding the natural sort ordering of the
                             groups, see also :py:meth:`~osv.osv.osv.search`
                             (supported only for many2one fields currently)
        :param bool lazy: if true, the results are only grouped by the first groupby and the 
                remaining groupbys are put in the __context key.  If false, all the groupbys are
                done in one call.
        :return: list of dictionaries(one dictionary for each record) containing:
  
                    * the values of fields grouped by the fields in ``groupby`` argument
                    * __domain: list of tuples specifying the search criteria
                    * __context: dictionary with argument like ``groupby``
        :rtype: [{'field_name_1': value, ...]
        :raise AccessError: * if user has no read rights on the requested object
                            * if user tries to bypass access rules for read on the requested object
        """
        if context is None:
            context = {}
        self.check_access_rights(cr, uid, 'read')
        query = self._where_calc(cr, uid, domain, context=context)
        
        
        fields = fields or self._columns.keys()
  
        groupby = [groupby] if isinstance(groupby, basestring) else groupby
        groupby_list = groupby[:1] if lazy else groupby
        annotated_groupbys = [self._read_group_process_groupby(gb, query, context) 
                                    for gb in groupby_list]
        groupby_fields = [g['field'] for g in annotated_groupbys]
        order = orderby or ','.join([g for g in groupby_list])
        groupby_dict = {gb['groupby']: gb for gb in annotated_groupbys}
  
        self._apply_ir_rules(cr, uid, query, 'read', context=context)
        for gb in groupby_fields:
            assert gb in fields, "Fields in 'groupby' must appear in the list of fields to read (perhaps it's missing in the list view?)"
            groupby_def = self._columns.get(gb) or (self._inherit_fields.get(gb) and self._inherit_fields.get(gb)[2])
            assert groupby_def and groupby_def._classic_write, "Fields in 'groupby' must be regular database-persisted fields (no function or related fields), or function fields with store=True"
            if not (gb in self._fields):
                # Don't allow arbitrary values, as this would be a SQL injection vector!
                raise except_orm(_('Invalid group_by'),
                                 _('Invalid group_by specification: "%s".\nA group_by specification must be a list of valid fields.')%(gb,))
  
        aggregated_fields = [
            f for f in fields
            if f not in ('id', 'sequence')
            if f not in groupby_fields
            if f in self._fields
            if self._fields[f].type in ('integer', 'float')
            if getattr(self._fields[f].base_field.column, '_classic_write', False)
        ]
  
        field_formatter = lambda f: (self._fields[f].group_operator or 'sum', self._inherits_join_calc(self._table, f, query), f)
        select_terms = ["%s(%s) AS %s" % field_formatter(f) for f in aggregated_fields]
  
        for gb in annotated_groupbys:
            select_terms.append('%s as "%s" ' % (gb['qualified_field'], gb['groupby']))
  
        groupby_terms, orderby_terms = self._read_group_prepare(order, aggregated_fields, annotated_groupbys, query)
        from_clause, where_clause, where_clause_params = query.get_sql()
        if lazy and (len(groupby_fields) >= 2 or not context.get('group_by_no_leaf')):
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
        
        # requete de base (ne fonctionne pas avec les filtres)
        #=======================================================================
        # query = """
        #     SELECT min(prisme_shortage_all.id) AS id, count(prisme_shortage_all.id) AS product_id_count , first("prisme_shortage_all"."product_qty") AS product_qty,last("prisme_shortage_all"."qtysum") AS qtysum,last("prisme_shortage_all"."qtysumshort") AS qtysumshort,"prisme_shortage_all"."product_id" as "product_id"
        #     FROM "prisme_shortage_all" LEFT JOIN "product_product" as "prisme_shortage_all__product_id" ON ("prisme_shortage_all"."product_id" = "prisme_shortage_all__product_id"."id")
        #     WHERE ("prisme_shortage_all"."create_uid" = 1)
        #     GROUP BY "prisme_shortage_all"."product_id"
        #     ORDER BY id
        # """ 
        #=======================================================================
        
        cr.execute(query, where_clause_params)
        fetched_data = cr.dictfetchall()
  
        if not groupby_fields:
            return fetched_data
  
        many2onefields = [gb['field'] for gb in annotated_groupbys if gb['type'] == 'many2one']
        if many2onefields:
            data_ids = [r['id'] for r in fetched_data]
            many2onefields = list(set(many2onefields))
            data_dict = {d['id']: d for d in self.read(cr, uid, data_ids, many2onefields, context=context)} 
            for d in fetched_data:
                d.update(data_dict[d['id']])
  
        data = map(lambda r: {k: self._read_group_prepare_data(k,v, groupby_dict, context) for k,v in r.iteritems()}, fetched_data)
        result = [self._read_group_format_result(d, annotated_groupbys, groupby, groupby_dict, domain, context) for d in data]
        if lazy and groupby_fields[0] in self._group_by_full:
            # Right now, read_group only fill results in lazy mode (by default).
            # If you need to have the empty groups in 'eager' mode, then the
            # method _read_group_fill_results need to be completely reimplemented
            # in a sane way 
            result = self._read_group_fill_results(cr, uid, domain, groupby_fields[0], groupby[len(annotated_groupbys):],
                                                       aggregated_fields, count_field, result, read_group_order=order,
                                                       context=context)
        return result

        #Devrait etre execute a l installation du module !!!!
    def createSQL(self, cr, uid):
      try:  
        cr.execute('''
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
        cr.execute('commit;')
shortage_all()


