from osv import osv, fields 
import netsvc

class analytic_account_nexan(osv.osv):
    _name = 'account.analytic.account' 
    _inherit = 'account.analytic.account'
   
    #current is used to stop to the CRT account / where the merging start...
    _columns = {
        'current': fields.boolean('Current'),
    }
    
    #Merge product account with projet account	
    def merge_account(self, cr, uid,ids, product_acc_id, project_acc_id): 
       #Pool declaration
       pool_anal = self.pool.get('account.analytic.account')
       property_obj = self.pool.get('ir.property')
       #Get Clim property
       climid = property_obj.search(cr, uid, [('name','ilike','property_nexan_analytic_model')])
       if not climid:
         raise osv.except_osv(_('Error!'), _('property_nexan_analytic_model not exist'))
       resul = property_obj.read(cr,uid,climid,['value_text'])
       clim = resul[0]['value_text']
       if str(clim)=="":
         raise osv.except_osv(_('Error!'), _('property_nexan_analytic_model is blank'))
       #Initialize browsing analytic account
       product_acc = pool_anal.browse(cr, uid, product_acc_id)
       project_acc = pool_anal.browse(cr, uid, project_acc_id.id)
       #Get inital loop variable
       if product_acc.parent_id:
	  isParent=True
       else: 
          isParent=False
       if product_acc.current:
          isCurrent=True
       else: 
          isCurrent=False
       accs = []
       accs.append(product_acc.name)
       #Loop until current account is found
       while (isParent and not(isCurrent)):
          product_acc = product_acc.parent_id
          if product_acc.parent_id:
             isParent=True
          else:
             isParent=False
          if product_acc.current:
             isCurrent=True
          else:
             accs.append(product_acc.name)
             isCurrent=False
       #Merging account
       currentParent = project_acc_id.id
       #Get customer name
       ressplit = project_acc_id.name.split('-')
       customerName=ressplit[0] 
       for acc in accs[::-1]:
          accnew = acc.replace(clim,customerName)
          #Search if account already exist
          child = self.getChildNamedForParent(cr, uid, accnew, currentParent)
          if not(child):
            #Create if not
            currentParent=self.createAccount(cr, uid, accnew, currentParent)
          else:
            currentParent=child
       #Return last create or found account
       return currentParent

    #Return a child with parameter name for one parent in parameter if it exists
    def getChildNamedForParent(self, cr, uid, childName, parentId, context=None):
       pool_anal = self.pool.get('account.analytic.account')
       childs = pool_anal.search(cr,uid,[('name','ilike',childName)],context=None,limit=100)
       for child in childs:
           childobj = pool_anal.browse(cr,uid, child)
           if childobj.parent_id.id == parentId:
             return child
       return False

    #Create analytic account
    def createAccount(self, cr, uid, cname, parent, context=None):
       pool_anal = self.pool.get('account.analytic.account')
       anal_id = pool_anal.create(cr,uid,{'name': cname, 'state':'open', 'type':'normal', 'parent_id':parent})
       return anal_id


analytic_account_nexan() 
