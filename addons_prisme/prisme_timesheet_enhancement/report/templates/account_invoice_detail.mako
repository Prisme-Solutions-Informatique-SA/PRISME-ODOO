<html>
<head>
<style type="text/css">
table.gridtable {
	font-family: verdana,arial,sans-serif;
	font-size: 12px;
	color:#333333;
	border-width: 1px;
	border-color: #666666;
	border-collapse: collapse;
}
table.gridtable th {
	border-width: 1px;
	padding: 1px;
	border-style: solid;
	border-color: #666666;
	background-color: #dedede;
}
table.gridtable td {
	border-width: 1px;
	padding: 1px;
	border-style: solid;
	border-color: #666666;
	background-color: #ffffff;
  
}

.dontsplit {
  page-break-inside: avoid; 
}
.lw { font-size: 15px; }
h1 {page-break-before: always;}
</style>
</head>
<body>
  <div align="center">${helper.embed_logo_by_name('prisme_logo')|n}</div>
</br>
<%
i=0
%>
%for o in objects :
      %if i!=0:
         <p style="page-break-before: always;"></p>
      %endif
    <%
        i=i+1
    	if hasattr(o, 'partner_id'):
    		setLang(o.partner_id.lang)
    %>
<table width="100%">
<tr>
<td  width="60%" valign="bottom"></td>
<td width="40%">
<p class="lw" >

                %if o.partner_id.parent_id.id:
                ${o.partner_id.parent_id.name or ''| entity }<br/>
                ${o.partner_id.title and o.partner_id.title.name or ''| entity } ${o.partner_id.name | entity }<br/>
                %else:
                ${o.partner_id.title and o.partner_id.title.name or ''| entity } ${o.partner_id.name | entity }<br/>
                %endif
		${ "".join([s for s in display_address(o.partner_id).splitlines(True) if s.strip("\r\n")]).replace('\n', '<br />') }
</p>

</td>
</tr>
</table>
<p>&nbsp;<br/>&nbsp;</p>
<h3>Prestations facture ${o.number}</h3>
<%
    o._cr.execute("select acc.name, ptr.name, line.date, line.name, line.unit_amount, prd.default_code, tmpl.list_price,fact.factor,fact.name,prd.id,acc.pricelist_id,acc.partner_id from hr_analytic_timesheet t,account_analytic_line line, account_analytic_account acc, res_users usr, res_partner ptr, product_product prd, product_template tmpl,hr_timesheet_invoice_factor fact where t.line_id = line.id and fact.id=line.to_invoice and prd.product_tmpl_id=tmpl.id and line.product_id=prd.id and usr.partner_id=ptr.id and line.user_id=usr.id and acc.id=line.account_id and line.move_id is null and line.invoice_id="+str(o.id)+" order by date, t.time_beginning")

    res = o._cr.fetchall()
%>
<%
   from operator import itemgetter, attrgetter
   sortedList=sorted(res,key=itemgetter(0,1,5,8,2))
%>
<% 
colTotal=0
colAmount=0
oldProject = ""
oldProduct = ""
oldCollab = "" 
oldFactor = ""
chgCollab=False
%> 

%for t in sortedList: 
<%
chgCollab=False
%>
%if t[0] != oldProject:
<p>
<table class="gridtable" width="100%">
<tr>
<th align="left">Projet</th>
<th align="left">Date</th>
</tr>
<tr>
<td>${t[0]}</td>
<td>${o.date_invoice}</td>
</tr>
</table>
</p>

%endif
%if t[1] != oldCollab: 
%if oldCollab!="":
<%
chgCollab=True
%>
<tr>
<td style="border: 0px;"></td>
<td style="border: 0px;"></td>
<td align="right"><b>${formatLang(colTotal)}</b></td>
<td align="right"><b>${formatLang(colAmount)}</b></td>
</tr>
</table>
%endif
<br/><h4 > Collaborateur: ${t[1]| entity}</h4>
%endif
%if (t[5]!=oldProduct) or (t[8]!=oldFactor) or chgCollab:
%if (oldProduct!="") or (oldFactor!=""):
%if chgCollab==False:
<tr>
<td style="border: 0px;"></td>
<td style="border: 0px;"></td>
<td align="right"><b>${formatLang(colTotal)}</b></td>
<td align="right"><b>${formatLang(colAmount)}</b></td>
</tr>
</table>
%endif
%endif
<h5>${t[5]| entity} - ${t[8]| entity}</h5>
<table class="gridtable" width="100%">
<tr>
<th align="left" width="12%">Date</th>
<th align="left" width="68%">Description</th>
<th align="right" width="10%">Total</th>
<th align="right" width="10%">CHF</th>
</tr>
<%
colTotal=0
colAmount=0
%>
%endif
<%
plid=0
plid=t[10]
paid=0
paid=t[11]
pid=0
pid=t[9]
qty=0
qty=t[4]
price=0
price=getprice(plid,pid,paid,qty)
amt=0
amt=(price*qty)-((price*qty)*t[7]/100)
if t[7]==100:
   amt=price*qty
%>
<div class="dontsplit">
<tr>
  
<td valign="top" width="10%">${  formatLang(t[2],date=True) }</td> 
<td width="70%">${ t[3] | entity}</td> 
<td valign="top" align="right" width="10%">${  formatLang(t[4]) }</td> 
<td valign="top" align="right" width="10%">${  formatLang(amt) }</td>
  
</tr>
</div>
<%
colTotal=colTotal+t[4]
colAmount=colAmount+amt
oldProject=t[0]
oldCollab=t[1]
oldProduct=t[5]
oldFactor=t[8]
%>
 %endfor
<tr>
<td style="border: 0px;"></td> 
<td style="border: 0px;"></td>
<td align="right"><b>${formatLang(colTotal)}</b></td>
<td align="right"><b>${formatLang(colAmount)}</b></td>
</tr>
</table>
 %endfor
</body>
</html>
