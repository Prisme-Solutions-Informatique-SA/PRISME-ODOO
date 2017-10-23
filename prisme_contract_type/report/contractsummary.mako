<html>
<head>
<style type="text/css">
table.gridtable {
	font-family: verdana,arial,sans-serif;
	font-size: 9px;
	color:#333333;
	border-width: 1px;
	border-color: #666666;
	border-collapse: collapse;
        page-break-inside: avoid;
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
</style>
</head>
<body>
<%
i=0
%>
    %for o in objects :
      %if i!=0:
<p style="page-break-before: always;"></p>
      %endif
    <%
        oid=o.id
	timesheets=getTimesheets(oid)
        invoices=getInvoices(oid)
        purchases=getPurchases(oid)
        i=i+1
    	if hasattr(o, 'partner_id'):
    		setLang(o.partner_id.lang)
        
    %>
<p>
Projet: ${o.name or ''}<br/>
</p>
<h4>Main d'oeuvre</h4>
<table class="gridtable" width="100%">
<tr>
<th align="left" width="10%">Description</th>
<th align="left" width="70%">Date</th>
<th align="right" width="10%">Montant</th>
<th align="right" width="10%">Temps</th>
</tr>
<%
colTotal=0
colAmount=0
%>
%for t in timesheets: 
<tr>
<td valign="top" width="10%">${  t['name'] }</td> 
<td width="70%">${ formatLang(t['date'],date=True) }</td> 
<td valign="top" align="right" width="10%">${  formatLang(t['amount']) }</td> 
<td valign="top" align="right" width="10%">${  formatLang(t['unit_amount']) }</td>
</tr>
<%
colTotal=colTotal+t['amount']
colAmount=colAmount+t['unit_amount']
%>
%endfor
<tr>
<td style="border: 0px;"></td>
<td style="border: 0px;"></td>
<td align="right"><b>${formatLang(colTotal)}</b></td>
<td align="right"><b>${formatLang(colAmount)}</b></td>
</tr>

</table>
<h4>Facturé</h4>
<table class="gridtable" width="100%">
<tr>
<th align="left" width="10%">Date</th>
<th align="left" width="70%">No</th>
<th align="right" width="10%">Montant</th>
</tr>
<%
colAmount=0
%>
%for t in invoices:
<tr>
<td valign="top" width="10%">${  formatLang(t['date'],date=True) }</td>
<td width="70%">${ t['number'] }</td>
<td valign="top" align="right" width="10%">${  formatLang(t['amount_total']) }</td>
</tr>
<%
colAmount=colAmount+t['amount_total']
%>
%endfor
<tr>
<td style="border: 0px;"></td>
<td style="border: 0px;"></td>
<td align="right"><b>${formatLang(colAmount)}</b></td>
</tr>

</table>
<h4>Achats</h4>
<table class="gridtable" width="100%">
<tr>
<th align="left" width="10%">Date</th>
<th align="left" width="60%">Fournisseur</th>
<th align="right" width="10%">No</th>
<th align="right" width="10%">No Fournisseur</th>
<th align="right" width="10%">Montant</th>
</tr>
<%
colAmount=0
%>
%for t in purchases:
<tr>
<td valign="top" width="10%">${  formatLang(t['date'],date=True) }</td>
<td width="60%">${ t['supplier'] }</td>
<td valign="top" width="10%">${  t['number'] }</td>
<td valign="top" width="10%">${  t['supplier_number'] }</td>
<td valign="top" align="right" width="10%">${  formatLang(t['amount_total']) }</td>
</tr>
<%
colAmount=colAmount+t['amount_total']
%>
%endfor
<tr>
<td style="border: 0px;"></td>
<td style="border: 0px;"></td>
<td style="border: 0px;"></td>
<td style="border: 0px;"></td>
<td align="right"><b>${formatLang(colAmount)}</b></td>
</tr>

</table>

%endfor
</html>

