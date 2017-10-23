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
<% for o in objects %>
	<h1>
		${ o.name } -  ${ o.employee_id.name } 
	</h1>
	
	<% set sortedList = getSortedList(o.timesheet_ids) %>
	
	<table class="gridtable"  width="100%">
	<tr>
	<th width="15%">Client</th>
	<th width="15%">Projet</th>
	<th width="42%">Description du travail</th>
	<th width="8%">Date</th>
	<th width="4%">D&eacute;t</th>
	<th width="4%">Fin</th>
	<th width="4%">Total</th>
	<th width="4%">Facturable</th>
	<th width="4%">Net</th>

</tr>

	<% for t in sortedList %>
		<% set curDate = updateDate(t[3]) %>
		
		<tr>
		<td>${ t[0] }</td>
		<td>${ t[1] }</td>
		<td>${ t[2] }</td>
		<td>${ curDate }</td>
		<td>${ t[4] }</td>
		<td>${ t[5] }</td>
		<td>${ t[6] }</td>
		<td>${ t[7] }</td>
		<td>${ t[6]-((t[8]*t[6])/100) }</td>
		</tr>
	<% endfor %>
	
	</table>
	
<% endfor %>

</body>
</html>

