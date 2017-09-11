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
	<div align="center">${helper.embed_logo_by_name('prisme_logo')|safe}</div>
	
	
<% set i=0 %>


<% for o in objects %>
      <% if i!=0 %>
         <p style="page-break-before: always;"></p>
      <% endif %>
    
      <% set i=i+1 %>
	  
    


  <table width="100%">
  <tr>
  <td  width="60%" valign="bottom"></td>
  <td width="40%">
  <p class="lw" >

            <% if o.partner_id.is_company %>
				${o.partner_id.title and o.partner_id.title.name or ''} ${o.partner_id.name}<br/>
			<% elif o.partner_id.parent_id.id %>
				${o.partner_id.parent_id.name or ''}<br/>
				${o.partner_id.title and o.partner_id.title.name or ''} ${o.partner_id.name}<br/>
            <% else %>
				${o.partner_id.title and o.partner_id.title.name or ''} ${o.partner_id.name}<br/>
            <% endif %>

			<% for s in display_address(o.partner_id).splitlines(True) %>
				<% if s.strip("\r\n") %>
					${s}
					<br/>
				<% endif %>
			<% endfor %>
  </p>

  </td>
  </tr>
  </table>
  <p>&nbsp;<br/>&nbsp;</p>
  <h3>Prestations facture ${o.number}</h3>
  
  <% set colTotal=0 %>
  <% set colAmount=0 %>
  <% set oldProject = "" %>
  <% set oldProduct = "" %>
  <% set oldCollab = "" %>
  <% set oldFactor = "" %>
  <% set chgCollab=False %>
  
  <% for t in getSortedList(cr, o.id) %>
	<% set chgCollab=False %>
	<%if t[0] != oldProject %>
		<p>
		<table class="gridtable" width="100%">
		<tr>
		<th align="left">Projet</th>
		<th align="left">Date</th>
		</tr>
		<tr>
		<td>${t[0]}</td>
		<td>${formatDate(o.date_invoice)}</td>
		</tr>
		</table>
		</p>
	<% endif %>
	
		<% if t[1] != oldCollab %>
			<% if oldCollab!="" %>
				<% set chgCollab=True %>
				<tr>
				<td style="border: 0px;"></td>
				<td style="border: 0px;"></td>
				<td align="right"><b>${formatLang(getAndResetTotal())}</b></td>
				<td align="right"><b>${formatLang(getAndResetAmount())}</b></td>
				</tr>
				</table>
			<% endif %>
			<br/><h4 > Collaborateur: ${t[1]}</h4>
		<% endif %>
		
	<% if (t[5]!=oldProduct) or (t[8]!=oldFactor) or chgCollab %>
		<% if (oldProduct!="") or (oldFactor!="") %>
			<% if chgCollab==False %>
				<tr>
				<td style="border: 0px;"></td>
				<td style="border: 0px;"></td>
				<td align="right"><b>${formatLang(getAndResetTotal())}</b></td>
				<td align="right"><b>${formatLang(getAndResetAmount())}</b></td>
				</tr>
				</table>
			<% endif %>
		<% endif %>
		<h5>${t[5]} - ${t[8]}</h5>
		<table class="gridtable" width="100%">
		<tr>
		<th align="left" width="12%">Date</th>
		<th align="left" width="68%">Description</th>
		<th align="right" width="10%">Total</th>
		<th align="right" width="10%">CHF</th>
		</tr>
		<% set colTotal=0 %>
		<% set colAmount=0 %>
	<% endif %>
	
	<% set plid=0 %>
	<% set plid=t[10] %>
	<% set paid=0 %>
	<% set paid=t[11] %>
	<% set pid=0 %>
	<% set pid=t[9] %>
	<% set qty=0 %>
	<% set qty=t[4] %>
	<% set price=0 %>
	<% set price=getprice(pool,cr,uid,plid,pid,paid,qty) %>
	<% set amt=0 %>
	<% set amt=(price*qty)-((price*qty)*t[7]/100) %>
	<% if t[7]==100 %>
		<% set amt=price*qty %>
	<% endif %>
	
	<div class="dontsplit">
	<tr>
	  
	<td valign="top" width="10%">${  formatLang(t[2],date=True) }</td> 
	<td width="70%">${ t[3] }</td> 
	<td valign="top" align="right" width="10%">${  formatLang(t[4]) }</td> 
	<td valign="top" align="right" width="10%">${  formatLang(amt) }</td>
	  
	</tr>
	</div>
	
	<% set at = addToTotal(t[4]) %>
	<% set aa = addToAmount(amt) %>
	<% set oldProject=t[0] %>
	<% set oldCollab=t[1] %>
	<% set oldProduct=t[5] %>
	<% set oldFactor=t[8] %>
	
  <% endfor %>

  <tr>
  <td style="border: 0px;"></td> 
  <td style="border: 0px;"></td>
  <td align="right"><b>${formatLang(getAndResetTotal())}</b></td>
  <td align="right"><b>${formatLang(getAndResetAmount())}</b></td>
  </tr>
  </table>
  
<% endfor %>

</body>
</html>
