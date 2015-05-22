$(function () {
	

$("#sla_date_1").datepicker({
	maxDate: -2,
	onSelect: function(dateText, inst){ 
	$.ajax({type:"POST",url:"/daily_sla/",data:{"dateText":dateText},dataType:'json',
	beforeSend:function(data){
	$("#loading").show();
	$("#page_mask").css('visibility','visible');
	$('#idata_t').empty();
	$('#mdata_t').empty();
	$("#idata").css('display','none');
	$("#mdata").css('display','none');
	},
	success:function(data){
	
	$('#loading').hide();
	$("#page_mask").css('visibility','hidden');
	
	$('#daily_table').html(data);
	$('#daily_table').tablesorter();

	}
	})
	}
	});

$("#loading").fadeOut(); 
$('select').selectric();
$('#period_s').bind("change",display);
$('#siloid').bind("change",display);
$('#retailid').bind("change",display);
$('#tabs').tabs();


$('#dq_chart_btn').click(function(){
$.ajax({type:"GET",url:"/cn_dq_chart/",data:{},dataType:'json',
beforeSend:function(data){
$("#loading").show();
$("#page_mask").css('visibility','visible');
},
success:function(data){
$('#loading').hide();
$("#page_mask").css('visibility','hidden');
$("#dq_chart").highcharts(data);
}

})

});


$('#dq_btn').click(function(){
$.ajax({type:"GET",url:"/cn_dq/",data:{},dataType:'json',
beforeSend:function(data){
$("#loading").show();
$("#page_mask").css('visibility','visible');
$('#idata_t').empty();
$('#mdata_t').empty();
$("#idata").css('display','none');
$("#mdata").css('display','none');
},
success:function(data){
idata= JSON.parse(data.idata);
mdata= JSON.parse(data.mdata);
$('#loading').hide();
$("#page_mask").css('visibility','hidden');
$("#idata").css('display','block');
$("#mdata").css('display','block');
var idata_table="<thead><tr><th>Ticket#</th><th>Subject</th><th>Create at</th><th>Priority</th><th>Vendor</th><th>Retailer</th></tr></thead><tbody>";
var mdata_table="<thead><tr><th>Ticket#</th><th>Subject</th><th>Create at</th><th>Priority</th><th>Vendor</th><th>Retailer</th></tr></thead><tbody>";
for(var j=0;j < idata.tickets.length;j++)
{
idata_table = idata_table + "<tr><td><u><a style='color:#0000E3' href='https://retailsolutions.zendesk.com/agent/tickets/"+idata.tickets[j].id+"' target='_blank'>"+idata.tickets[j].id+"</a></u></td>"+
						   "<td>"+idata.tickets[j].subject+"</td>"+
						   "<td>"+idata.tickets[j].created_at.split('T')[0]+"</td>"+
						   "<td>"+idata.tickets[j].priority+"</td>"+
						   "<td>"+idata.tickets[j].fields[0].value.split(':')[1]+"</td>"+
						   "<td>"+idata.tickets[j].fields[1].value.split(':')[1]+"</td>"+
						   "</tr>"
}

idata_table = idata_table + "</tbody>"

for(var j=0;j < mdata.tickets.length;j++)
{
mdata_table = mdata_table + "<tr><td><u><a style='color:#0000E3' href='https://retailsolutions.zendesk.com/agent/tickets/"+mdata.tickets[j].id+"' target='_blank'>"+mdata.tickets[j].id+"</a></u></td>"+
						   "<td>"+mdata.tickets[j].subject+"</td>"+
						   "<td>"+mdata.tickets[j].created_at.split('T')[0]+"</td>"+
						   "<td>"+mdata.tickets[j].priority+"</td>"+
						   "<td>"+mdata.tickets[j].fields[0].value.split(':')[1]+"</td>"+
						   "<td>"+mdata.tickets[j].fields[1].value.split(':')[1]+"</td>"+
						   "</tr>"
}

mdata_table = mdata_table + "</tbody>"

$('#idata_t').html(idata_table);
$('#mdata_t').html(mdata_table);

$('#idata_t').tablesorter();
$('#mdata_t').tablesorter();
}

})

});

});

function display(){
var flag = 1;
var hasPlotLine = false;
var p = $('#period_s').val();
var s = $('#siloid').val();
var r = $('#retailid').val();


$.ajax({type:"POST",url:"/cn_aj_res/",data:{"p":p,"s":s,"r":r},dataType:'json',
beforeSend:function(data){
$("#loading").show();
$("#page_mask").css('visibility','visible');
},
success:function(data){
$('#loading').hide();
$("#page_mask").css('visibility','hidden');
$('#container-top').highcharts(data.cn_json_line);
$('#container-bottom-left').highcharts(data.cn_json_pie);
$('#container-bottom-right').highcharts(data.cn_json_bar);
$('#silo_table').html(data.silo_html);

if($('#siloid').val()!='Please Choose'){
	$('#silo_text').css("display","none");
	$('#silo_SLA').css("display","block");
	$('#silo_strip_wd').css("display","block");
	$('#silo_p').highcharts(data.cn_silo_bar);
}else{
$('#silo_p').empty();
$('#silo_text').css("display","block");
$('#silo_SLA').css("display","none");
$('#silo_strip_wd').css("display","none");
}

if($('#retailid').val()!='Please Choose'){
	$('#retail_text').css("display","none");
	$('#retail_SLA').css("display","block");
	$('#retailer_strip_wd').css("display","block");
	$('#retail_p').highcharts(data.cn_retail_bar);
}else{
$('#retail_p').empty()
$('#retail_text').css("display","block");
$('#retail_SLA').css("display","none");
$('#retailer_strip_wd').css("display","none");
}


$('#silo_strip_wd').click(function(){
	$('#silo_p').highcharts(data.cn_silo_bar_wd);
});

$('#retailer_strip_wd').click(function(){
	$('#retail_p').highcharts(data.cn_retail_bar_wd);
});

}
});
}