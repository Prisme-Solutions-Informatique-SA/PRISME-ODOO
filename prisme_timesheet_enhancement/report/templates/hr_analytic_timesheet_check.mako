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
<h1> Checklist heures</h1>

<font face="verdana"size="1" >
<table class="gridtable" width="100%">
<tr>
<th>Client</th>
<th>Projet</th>
<th>Collaborateur</th> 
<th>Description du travail</th> 
<th width="4%">Date</th> 
<th>D&eacute;t</th>
<th>Fin</th>
<th>Total</th>
<th>Facturable</th>
<th>Net</th>
</tr>

<% set sortedList = getSortedList(objects) %>

<% for t in sortedList %>

	<% set nothing = updateClAPr(t) %>

	<tr>
	<td>${ getClient() }</td>
	<td>${ getProject() }</td>
	<td>${ t[9] }</td>
	<td>${ t[2] }</td>
	<td>${ getFormattedDate(t[3]) }</td>
	<td>${ t[4] }</td>
	<td>${ t[5] }</td>
	<td>${ t[6] }</td>
	<td>${ t[7] }</td>
	<td>${ t[6]-((t[8]*t[6])/100.0) }</td>

	</tr>
<% endfor %>
</table>
</font>

</body>
</html>
