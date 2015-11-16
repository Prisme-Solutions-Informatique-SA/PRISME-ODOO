## -*- coding: utf-8 -*-
<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>

<<<<<<< HEAD
<h1>Suivi d'opportunites</h1>
=======
<h1>Suivi d'opportunite</h1>
>>>>>>> 86b92ebcdce7aebbe83756ef2bfbab80dd824c46
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
<<<<<<< HEAD
	text = ${mess.body}
	${mess.author_id.name} - ${mess.date[:10]}:<br> {text} <hr/>
=======
	${mess.author_id.name} - ${mess.date[:10]}:<br> ${mess.body}<hr/>
>>>>>>> 86b92ebcdce7aebbe83756ef2bfbab80dd824c46
% endif

%endfor

</ul>
%endfor
</body>
</html>