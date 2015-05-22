from django.shortcuts import render, render_to_response
from django.core.context_processors import request
from alert.models import AlertMaster, TaskSum,TaskOwner
import json
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.db.transaction import commit_on_success
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import time,datetime
# Create your views here.

@login_required
def alert(request):
    posts   =  AlertMaster.objects.all()
    return render_to_response('external.html',{'posts':posts},context_instance=RequestContext(request))


@csrf_exempt
def ajax_response(request):
    param="Production_day"
  #  param1="silo"
    param2="sla"  
    param=request.POST.get("param")
  #  param1=request.POST.get("param1")
    param2=request.POST.get("param2")
    param3= request.POST.get("param3")
    if(param2 == "NOT_SET" ):
        param2=' like "Not%%"'
    elif(param2 == "All"):
        param2='=sla'
    elif(param2 is not None):
        param2=' not like "Not%%"'
        
    if param!="All"  and param2!="All":
        raw_sql='select * from alert.alert_master where production_day in("'+param+'","Daily")  and sla '+param2+' and SILO not in(SELECT silo  FROM alert.alert_status where date ="'+param3+'")'
          
    elif param!="All":
        raw_sql='select * from alert.alert_master where production_day in("'+param+'","Daily")' 
    
    elif param2!="All":
        raw_sql='select * from alert.alert_master where sla'+param2+''
    else:
        raw_sql='select * from alert.alert_master where SILO not in(SELECT silo  FROM alert.alert_status where date ="'+param3+'")'
    
    print raw_sql    
    tests  =  AlertMaster.objects.raw(raw_sql)
    print request.user
    return render_to_response('ajax.html',{'tests':tests},context_instance=RequestContext(request))


@csrf_exempt
def submitstatus(request):
    from django.db import connection, transaction
    e1=request.POST.get("e1")
    e2=json.loads(request.POST.get("e2"))
    e3=json.loads(request.POST.get("e3"))
    e4=json.loads(request.POST.get("e4"))
    e5=request.user
    for i in range(0,len(e2)):
        cursor = connection.cursor()
        if e3[i] is not None:
            cursor.execute("insert into alert.alert_status(date,silo,sla_status,delay_reason,personnel) values(%s,%s,%s,%s,%s)",[e1,e2[i],e3[i],e4[i],e5])
        transaction.commit_unless_managed()
    return render_to_response('alert.html')



@login_required
def taskview(request):
    sql = "select * from alert.task_owner"
    sql1 = "select * from alert.task_sum"
    tasks = TaskOwner.objects.raw(sql)
    tasks1 = TaskSum.objects.raw(sql1)
    #print request.user
    return render_to_response('task_all.html',{'tasks':tasks,'tasks1':tasks1})

@csrf_exempt
def shift_filter(request):
    task_o = request.POST.get("task_o")
    task_date = request.POST.get("task_date")
    if task_date is not None:
        if task_o == 'All':
            shift_sql = 'select * from alert.task_sum where weekday= "'+task_date+'"'
        else:
            shift_sql = 'select * from alert.task_sum where weekday= "'+task_date+'"and task_owner like "'+task_o+'%%"'
    else:
        if task_o == 'All':
            shift_sql = 'select * from alert.task_sum'
        else:
            shift_sql = 'select * from alert.task_sum where task_owner like "'+task_o+'%%"'
        
    task_filters = TaskSum.objects.raw(shift_sql)
    return render_to_response('task_ajax.html',{'task_filters':task_filters})
    
    
    


 