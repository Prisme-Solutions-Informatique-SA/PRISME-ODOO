## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>

<h1>Suivi d'opportunite</h1>
%for opp in objects :
<p><b>Opportunity</b><br>
${opp.name}</p>
<p><b>Societe</b><br>
${opp.partner_id.name}</p>
<p><b>Contact</b><br>
${opp.partner_id.name}<br>
${opp.email_from}<br>
${opp.phone}</p>
<p><b>Description</b><br>
${opp.description}</p>
<p><b>Action suivante</b><br>
${opp.title_action}<br>
${opp.date_action}</p>
<p><b>Reference</b><br>
${opp.ref.name}<br>
${opp.ref2.name}</>
<p><b>Historique</b><br>
<ul>

%for mess in opp.message_ids:
% if mess.type!='notification':
	${mess.author_id.name} - ${mess.date[:10]}:<br> ${mess.body}<hr/>
% endif

%endfor
</ul>
%endfor
</body>
</html>