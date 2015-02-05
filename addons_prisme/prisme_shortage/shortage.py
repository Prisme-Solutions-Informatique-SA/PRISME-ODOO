from osv import fields,osv
import datetime
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
	  #import pdb; pdb.set_trace()
	  if view_type == 'tree':
		#Recuperation de l'id du produits
		product_id = None
		if context != None:
			try:
				product_id = context['product_id']
			except Exception as exp:
				product_id = None
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
		if product_id != None:
			#Nettoyage
			cr.execute('delete from prisme_shortage_wizard where create_uid=%s',(str(user),))
			#Recuperation des warehouses-stock racine
			stock_main_ids = []
			cr.execute("select lot_stock_id from stock_warehouse")
			stock_main_ids = map(lambda x: x[0], cr.fetchall())
       		#Recuperation des ids des emplacements de stocks inclus       		 	
			stock_location = self.pool.get('stock.location')
			stock_ids = []
			for parent_id in stock_main_ids:					#Parcours des ids parents
				if stock_ids.count(parent_id) == 0:				#Ajout uniquement si non present
					stock_ids.append(parent_id)
				last_len = 0
				while last_len != len(stock_ids):
					last_len = len(stock_ids)
					for stockid in stock_ids:
						ids = stock_location.search(cr,user,[('location_id','=',stockid),])
						for id in ids:
							if stock_ids.count(id) == 0:
								stock_ids.append(id)
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

class shortage_all(osv.osv):
	_name = 'prisme.shortage.all'
	_columns = {
		'origin' : fields.char('Origin', size=30),
		'partner_id' : fields.many2one('res.partner','Partner'),
		'product_id' : fields.many2one('product.product','Product'),
		'product_qty' : fields.float('Qty',group_operator='first'),
		'location_id' : fields.many2one('stock.location', 'Src. Loc.'),
		'location_dest_id':fields.many2one('stock.location', 'Dest. Loc.'),
		'date' : fields.date('Date'),
		'state':  fields.selection([('actual','Actual'),('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Confirmed'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Cancelled')], 'State', readonly=True, select=True),
		'qtysum': fields.float('Forecast',group_operator='last'),
		'sign': fields.char('s',size=1),
		'qtysumshort': fields.float('Foreca. Short',group_operator='last'),
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
	  self.createSQL(cr)	
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

        #Devrait etre execute a l installation du module !!!!
	def createSQL(self, cr):
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


