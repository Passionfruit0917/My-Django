$(function () {
$('select').selectric();
$(".select02").bind("change",display);
$(".select03").bind("change",display);
$(".select04").bind("change",display1);
$("#date_1").datepicker({
	minDate: -2,
	maxDate: 0,
	onSelect: function(dateText, inst) { 
	display();
	}
	});
	
$("#date_2").datepicker({
	minDate: -2,
	maxDate: 0,
	onSelect: function(dateText, inst) { 
	display1();
	}
	});	
});

function display(event) {
var date = new Date(Date.parse($("#date_1").val()));
var today = new Array('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
var a = today[date.getDay()]; 
var b = $(".select02").val();
var c = $(".select03").val();
$.post("/ajax_response/", {"param": a,"param1":b,"param2":c,"param3":$("#date_1").val()}, function (data) {
							//alert($("#date_1").val());

							//alert($('input:radio[name=1]:checked').val());

							$("#alternatecolor").html(data);	
												
																	});
						};
				
				
function display1(event) {
var task_o = $(".select04").val();
var date1 = new Date(Date.parse($("#date_2").val()));
var today1 = new Array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');
var task_date = today1[date1.getDay()]; 
$.post("/shift_filter/", {"task_o": task_o,"task_date":task_date}, function (data) {

		$("#alternatecolor01").html(data);	
});

};
