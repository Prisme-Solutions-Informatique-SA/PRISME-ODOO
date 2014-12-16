<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
<%!
def filter(text):
	return text
def getdate(text):
	tmp = text+''
	tmp2 = tmp[:10]
	return tmp2
def gettype(text):
	if text=='notification':
		return 0
	else:
		return 1
%>
<h1>Suivi d'opportunité</h1>
%for opp in objects :
<p><b>Opportunité</b><br>
${opp.name or ''|entity}</p>
<p><b>Société</b><br>
${opp.partner_id.name or ''|entity}</p>
<p><b>Contact</b><br>
${opp.partner_id.name or ''|entity}<br>
${opp.email_from or ''|entity}<br>
${opp.phone or ''|entity}</p>
<p><b>Description</b><br>
${opp.description or ''|entity}</p>
<p><b>Action suivante</b><br>
${opp.title_action or ''|entity}<br>
${opp.date_action or ''|entity}</p>
<p><b>Référence</b><br>
${opp.ref.name or ''|entity}<br>
${opp.ref2.name or ''|entity}</>
<p><b>Historique</b><br>
<ul>
%for mess in opp.message_ids:
% if gettype(mess.type):
	${mess.author_id.name or ''|entity} - ${getdate(mess.date)}:<br> ${filter(mess.body)}<hr/>
% endif

%endfor
</ul>
%endfor
</body>
</html>