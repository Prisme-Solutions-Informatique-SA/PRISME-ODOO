<html>
<head>
    <style type="text/css">
table {
 border-width:1px; 
 border-style:solid; 
 border-color:gray;
 width:100%;
 }
tr {
 border-width:1px;
 border-style:solid; 
 border-color:black;  
}
td { 
 font:Verdana;
 font-size:10;
 }
thead tr{
 border-width:1px;
 border-style:solid; 
 border-color:black;
}

table .over{
    border-width: 0px;
}

.basic_table{
text-align:center;
border:1px solid lightGrey;
border-collapse: collapse;
}
.basic_table td {
border:1px solid lightGrey;
font-size:12;
}


.list_table {
border-color:black;
text-align:center;
border-collapse: collapse;

}
.list_table td {
border-color:gray;
border-top:1px solid gray;
text-align:left;
font-size:12;
padding-right:3px;
padding-left:3px;
padding-top:3px;
padding-bottom:3px;
}

.list_table th {
border-bottom:2px solid black;
text-align:left;
font-size:12;
font-weight:bold;
padding-right:3px;
padding-left:3px;
border-top: 0px solid black;
border-left: 0px;
border-right: 0px;
}

.list_tabe thead {
    display:table-header-group;
}

    </style>
</head>
<body>
        <table style="border-top: 0px solid black; border-left: 0px; border-right: 0px">
        <thead>
            <tr>
                <th style="text-align:left;" width="20%">${objects[1].date |entity}</th>
                <th style="text-align:center;"><b>${company.name |entity}</b></th>
                <th style="text-align:right" width="20%"> </th>
            </tr>
            </thead>
       </table>
<div id="1" style="padding-left:0;padding-top:0;padding-bottom:10;border-width:0px;border-style:solid">
       <br/>
       <p align="center">
       ${_("MO Operations unfinished with tools") |entity}
       </p>
       <br/>
       <table class="basic_table" >
           <tr>
               <td width="20%"><b>${_("Order by") |entity}</b></td>
               <td align="left">${_("Tool") |entity}</tr>
           </tr>
           <tr>
               <td> </td>
               <td align="left">${_("starter date") |entity}</td>
           </tr>
       </table>
       <br/>
       <table class="list_table">
        <thead>
            <tr>
                <th>${_("Tool") |entity}</th>
                <th>${_("Date") |entity}</th>
                <th>${_("Number Operation") |entity}</th>
                <th>${_("Number MO") |entity}</th>
                <th>${_("Operation Description") |entity}</th>
                <th>${_("Workcenter") |entity}</th>
                <th width="10%">${_("Reserved") |entity}</th>
            </tr>
       </thead>
       %for line in objects:
           <tr>
               <td>${line.tool_product_id.name or ''|entity}</td>
                <td>${line.date_planned or ''|entity}</td>
                <td>${line.production_id.id or ''|entity}</td>
                <td>${line.production_id.name or ''|entity}</td>
                <td>${line.name or ''|entity}</td>
                <td>${line.workcenter_id.name or ''|entity}</td>
                %if line.reserved :
                <td>${_("Yes") |entity}</td>
                %else :
                <td> </td>
                %endif
           </tr>
       %endfor
      </table>
</div>
</body>
</html>