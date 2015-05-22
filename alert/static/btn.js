$(function(){
$("#alternatecolor").on("click",'.rno',function(){
	$(this).next(".reason").css("display","block");
});

$("#alternatecolor").on("click",'.ryes',function(){
	$(this).parent().children(".reason").css("display","none");
});

$("#alternatecolor01").on("click",'.rdone',function(){
	$(this).parent().children(".treason").css("display","none");
});

$("#alternatecolor01").on("click",'.rissue',function(){
	$(this).next(".treason").css("display","block");
});


$("#alternatecolor").on("click",'.checkbtn',function(){
	if(confirm("Are you sure you want to check all of them Yes? You will be responsible for what Did!")){
		$(".ryes").attr("checked",'checked');
		}else{
		
		}		
});

$("#alternatecolor01").on("click",'.taskbtn',function(){
	if(confirm("Are you sure you want to check all of them Yes? You will be responsible for what Did!")){
		$(".rdone").attr("checked",'checked');
		}else{
		
		}		
});





});