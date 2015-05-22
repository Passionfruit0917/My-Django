import simplejson
from django.shortcuts import render_to_response
from django.http import HttpResponse
from app.models import Cnhub,Euhub,Gahub
from collections import OrderedDict
from django.views.decorators.csrf import csrf_exempt
import requests
import datetime
import numpy as np
from pandas import DataFrame
import pandas as pd


def cn(request):
    li={}
    retail=[]
    line=[]
    line_amount=[]  
    line_amount_w=[]
    retail_amount=[]

    raw_sql='select ID,Vendor,count(*) as count1 from test.cnhub where date > date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and duration >240 and dayofweek(date) not in (1,7) group by vendor'
    posts = Cnhub.objects.using('other').raw(raw_sql)
    
    raw_sql_silo ='select ID,siloID,count(*) as count1 from (select ID,Date,SiloID,avg(duration) as t from test.cnhub group by SiloID,Date)a where t>240 and date > date_format(date_sub((select max(Date) from test.cnhub),interval 30 day),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by siloID order by count1 desc limit 10'
    silo_posts = Cnhub.objects.using('other').raw(raw_sql_silo)
    
    raw_sql_retail='select ID,retailer,count(*) as count1 from test.cnhub where duration >240 and date > date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by retailer order by count(*) desc limit 10'
    retail_posts = Cnhub.objects.using('other').raw(raw_sql_retail)
    
    raw_sql_line ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.cnhub where duration >240 group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and (select max(Date) from test.cnhub ) order by datefield'
    line_posts = Cnhub.objects.using('other').raw(raw_sql_line)
    
    raw_sql_line_wd ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.cnhub where duration >240 and dayofweek(date) not in (1,7) group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and (select max(Date) from test.cnhub ) order by datefield'
    line_posts_wd = Cnhub.objects.using('other').raw(raw_sql_line_wd)
    
    raw_silo_name_sql ='select ID,siloid from test.cnhub group by siloid'
    bar_silos=Cnhub.objects.using('other').raw(raw_silo_name_sql)
    
    raw_retailer_name_sql='select ID,retailer from test.cnhub group by retailer'
    bar_retailers=Cnhub.objects.using('other').raw(raw_retailer_name_sql)

    for post in posts:
        li[post.vendor.encode('ascii')]=int(post.count1)
     
    for retail_post in retail_posts:
        retail.append(retail_post.retailer)
        retail_amount.append(int(retail_post.count1))   
      
    for line_post in line_posts:
        line.append(line_post.datefield)
        line_amount.append(line_post.count1)   
    
    for line_post_wd in line_posts_wd:
        line_amount_w.append(line_post_wd.count1)
        
    lit=simplejson.dumps(li.items())
    retail=simplejson.dumps(retail)
    retail_amount=simplejson.dumps(retail_amount)
    line=simplejson.dumps(line,default=date_handler)
    line_amount=simplejson.dumps(line_amount)
    line_amount_w=simplejson.dumps(line_amount_w)
    
    return render_to_response('china.html',{"lit":lit,"silo_posts":silo_posts,"retail":retail,"retail_amount":retail_amount,"line":line,"line_amount":line_amount,"line_amount_w":line_amount_w,"bar_silos":bar_silos,"bar_retailers":bar_retailers})

@csrf_exempt
def cn_dq(request):
    url_idata = 'https://retailsolutions.zendesk.com/api/v2/views/52747557/tickets.json'
    url_mdata = 'https://retailsolutions.zendesk.com/api/v2/views/52755987/tickets.json'
    user = 'rick.xu@retailsolutions.com'
    pwd = 'Apr2015$'
    res_idata = requests.get(url_idata, auth=(user, pwd))
    res_mdata = requests.get(url_mdata, auth=(user, pwd))
    idata = simplejson.dumps(simplejson.loads(simplejson.dumps(res_idata.json())))
    mdata = simplejson.dumps(simplejson.loads(simplejson.dumps(res_mdata.json())))
    zendesk ={"idata":idata,"mdata":mdata}
    zendesk = simplejson.dumps(zendesk)
    return HttpResponse(zendesk,content_type='application/json')
  
@csrf_exempt    
def cn_dq_chart(request):
    url_tickets = 'https://retailsolutions.zendesk.com/api/v2/views/52991768/tickets.json'
    url_tickets2 = 'https://retailsolutions.zendesk.com/api/v2/views/53135327/tickets.json' 
    user = 'rick.xu@retailsolutions.com'
    pwd = 'Apr2015$'
    es_tickets = requests.get(url_tickets, auth=(user, pwd))
    es_tickets2 = requests.get(url_tickets2, auth=(user, pwd))
    tt=simplejson.loads(simplejson.dumps(es_tickets.json()))
    tt2=simplejson.loads(simplejson.dumps(es_tickets2.json()))
    arr = []
    temp=[]
    
    arr2 = []
    temp2=[]
    
    for t in tt2['tickets']:
        arr2.append(t['created_at'][0:10])
    
    for t in tt['tickets']:
        arr.append(t['created_at'][0:10])
            
    dict1={}
    dict2={}
    for a in arr:
        i=0
        temp.append(a)
        for tem in temp:
            if tem==a:
                i=i+1
                dict1[a]=i
                
    for a in arr2:
        i=0
        temp2.append(a)
        for tem in temp2:
            if tem==a:
                i=i+1
                dict2[a]=i
    
    dict1=OrderedDict(sorted(dict1.items(), key=lambda t: t[0]))
    dict2=OrderedDict(sorted(dict2.items(), key=lambda t: t[0]))
    
    cal=[]
    i=-145
    
    while (i<1):
        cal.append(str(datetime.date.today()+ datetime.timedelta(i)))
        i=i+1
    
    cal=DataFrame(cal)
    cal.columns=['Date']
    idata=pd.DataFrame(dict1.items())
    idata2=pd.DataFrame(dict2.items())
    idata.columns=['Date','Amount']
    idata2.columns=['Date','Amount']
    idata = pd.merge(cal,idata,on='Date',how='outer')
     
    idata2 = pd.merge(cal,idata2,on='Date',how='outer')
    dq_date = []
    dq_amount = []
    dq_amount2 = []
    
    dq_dates= np.array(idata.fillna(0)['Date'])
    
    for dq_dates_1 in dq_dates:
        dq_date.append(dq_dates_1)
    
    dq_amounts=np.array(idata.fillna(0)['Amount'])
    
    dq_amounts2=np.array(idata2.fillna(0)['Amount'])
    
    for dq_amounts_1 in dq_amounts:
        dq_amount.append(dq_amounts_1)
    
    for dq_amounts_1 in dq_amounts2:
        dq_amount2.append(dq_amounts_1)
    
    dq_h={'chart':{'type':'spline','width':1250},'title': {'text': '',},'xAxis': {'categories': dq_date,'tickInterval': 10 },'yAxis': {'title': {'text': 'Missing SLA Silo number'},'min':0,'tickInterval': 1,'plotLines': [{'value': 0,'width': 1,'color': '#808080',}]},'plotOptions': {'spline': {'lineWidth': 2,'states': {'hover': {'lineWidth': 3,}},'marker': {'enabled': False},}},'legend': {'layout': 'vertical','align': 'right','verticalAlign': 'middle','borderWidth': 0},'tooltip': {'shared': True,'crosshairs': True},'series': [{'name': 'Incorrect Data','data': dq_amount},{'name':'Missing Data','data':dq_amount2}]}
    #dq_h={'chart': {'type': 'column','width':'1250'},'title': {'text':'Silo Daily Performance'},'xAxis': {'categories': dq_date ,'tickInterval': 10 },'yAxis': {'min': 0,'tickInterval': 1,'title': {'text': 'Silo Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0},'series':{'groupPadding':0},},'legend':{'enabled':True,},'series': [{'name': 'Incorrect Data','data': dq_amount},{'name':'Missing Data','data':dq_amount2}]}
    dq_highchart = simplejson.dumps(dq_h)
    return HttpResponse(dq_highchart,content_type='application/json')
     
@csrf_exempt
def cn_aj_res(request):
    p=request.POST.get("p")
    s=request.POST.get("s")
    r=request.POST.get("r")
    cav_period="30 day"
    line=[]
    line_amount=[]  
    line_amount_w=[]
    retail_amount=[]
    silo_date=[]
    silo_date_wd=[]
    silo_amount=[]
    silo_amount_wd=[]
    retail_date_wd=[]
    retail_amount_wd=[]
    retail=[]
    v_pie={}
    silo_pie=OrderedDict()
    retail_p_date=[]
    retail_p_amount=[]
    if(p == "Last 7 days"): cav_period ="7 day"
    elif(p == "Last 30 days"):cav_period ="30 day"
    elif(p == "Last 3 months"):cav_period ="3 month"  
    elif(p == "Last 6 months"):cav_period ="6 month"
        
    raw_sql_line ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.cnhub where duration >240 group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.cnhub ) order by datefield'        
    raw_sql_line_wd ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.cnhub where duration >240 and dayofweek(date) not in (1,7) group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.cnhub ) order by datefield'       
    raw_sql_vendor='select ID,Vendor,count(*) as count1 from test.cnhub where date > date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and duration >240 and dayofweek(date) not in (1,7) group by vendor'
    raw_sql_retail='select ID,retailer,count(*) as count1 from test.cnhub where duration >240 and date > date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by retailer order by count(*) desc limit 10'
    raw_sql_silo ='select ID,siloID,count(*) as count1 from (select ID,Date,SiloID,avg(duration) as t from test.cnhub group by SiloID,Date)a where t>240 and date > date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by siloID order by count1 desc limit 10'
    raw_silos_p_sql ='SELECT ID,b.datefield,IFNULL(a.t,0) as duration from (select Date,siloID,round(avg(duration),0) AS t from test.cnhub where siloid="'+s+'" group by Date,siloID order by date desc) a right JOIN test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.cnhub) order by datefield'
    raw_silos_p_sql_wd ='SELECT ID,b.datefield,IFNULL(a.t,0) as duration from (select Date,siloID,round(avg(duration),0) AS t from test.cnhub where siloid="'+s+'" group by Date,siloID order by date desc) a right JOIN test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.cnhub) and dayofweek(datefield) not in (1,7) order by datefield'
    raw_retail_sql='select ID,b.datefield,IFNULL(d,0) as duration from(select Date,retailer,round(avg(duration),0) as d from test.cnhub where retailer="'+r+'" group by Date,retailer) a right join test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.cnhub)'
    raw_retail_sql_wd='select ID,b.datefield,IFNULL(d,0) as duration from(select Date,retailer,round(avg(duration),0) as d from test.cnhub where retailer="'+r+'" group by Date,retailer) a right join test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.cnhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.cnhub) and dayofweek(datefield) not in (1,7)'
    silo_posts = Cnhub.objects.using('other').raw(raw_sql_silo)
    retail_posts = Cnhub.objects.using('other').raw(raw_sql_retail)
    line_posts = Cnhub.objects.using('other').raw(raw_sql_line) 
    line_posts_wd = Cnhub.objects.using('other').raw(raw_sql_line_wd)
    vendor_posts = Cnhub.objects.using('other').raw(raw_sql_vendor)   
    raw_silos_p=Cnhub.objects.using('other').raw(raw_silos_p_sql)
    raw_retails = Cnhub.objects.using('other').raw(raw_retail_sql)
    raw_silos_p_wd = Cnhub.objects.using('other').raw(raw_silos_p_sql_wd)
    raw_retails_wd = Cnhub.objects.using('other').raw(raw_retail_sql_wd)
    
    for line_post_wd in line_posts_wd:
        line_amount_w.append(line_post_wd.count1)
            
    for line_post in line_posts:
        line.append(line_post.datefield)
        line_amount.append(line_post.count1)  
            
    for vendor_post in vendor_posts:
        v_pie[vendor_post.vendor.encode('ascii')]=int(vendor_post.count1)  
    
    for retail_post in retail_posts:
        retail.append(retail_post.retailer)
        retail_amount.append(int(retail_post.count1))   
    
    for silo_post in silo_posts:
        silo_pie[silo_post.siloid.encode('ascii')]=int(silo_post.count1)
    
    for raw_silo_p in raw_silos_p:
        silo_date.append(raw_silo_p.datefield)
        silo_amount.append(raw_silo_p.duration)
    
    for raw_retail in raw_retails:
        retail_p_date.append(raw_retail.datefield)
        retail_p_amount.append(int(raw_retail.duration))
    
    for raw_silo_p_wd in raw_silos_p_wd:
        silo_date_wd.append(raw_silo_p_wd.datefield)
        silo_amount_wd.append(raw_silo_p_wd.duration)
        
    for raw_retail_wd in raw_retails_wd:
        retail_date_wd.append(raw_retail_wd.datefield)
        retail_amount_wd.append(raw_retail_wd.duration)
    
    line=simplejson.loads(simplejson.dumps(line,default=date_handler))
    silo_date=simplejson.loads(simplejson.dumps(silo_date,default=date_handler))    
    retail_p_date=simplejson.loads(simplejson.dumps(retail_p_date,default=date_handler)) 
    silo_date_wd=simplejson.loads(simplejson.dumps(silo_date_wd,default=date_handler))
    retail_date_wd=simplejson.loads(simplejson.dumps(retail_date_wd,default=date_handler))
    
    cn_json_line={'chart':{'width':1250},'title': {'text': '',},'xAxis': {'categories': line,'tickInterval': 1 },'yAxis': {'title': {'text': 'Missing SLA Silo number'},'min':0,'plotLines': [{'value': 0,'width': 1,'color': '#808080',}]},'legend': {'layout': 'vertical','align': 'right','verticalAlign': 'middle','borderWidth': 0},'plotOptions': {'spline': {'lineWidth': 2,'states': {'hover': {'lineWidth': 3,}},'marker': {'enabled': False},}}, 'tooltip': {'shared': True,'crosshairs': True},'series': [{'name': 'Include Weekend','data': line_amount},{'name': 'Exclude Weekend','data': line_amount_w}]}
        
    v_pie=simplejson.dumps(v_pie.items())
    v_pie = simplejson.loads(v_pie)
    
    cn_json_pie={'chart': {'plotShadow': False,'width':390},'title': {'text': ''},'tooltip': {'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'},'plotOptions': {'pie': {'allowPointSelect': True,'cursor': 'pointer','dataLabels': {'enabled': False,},'showInLegend':True}},'series': [{'type': 'pie','name': 'Silo Missing Percentage','data':v_pie }]}
    cn_json_bar={'chart': {'type': 'bar','width':380},'title': {'text': ''},'xAxis': {'categories':retail ,'title': {'text': ''}},'yAxis': {'min': 0,'max':170,'title': {'text': '','align': 'high'},'labels': {'overflow': 'justify'}},'plotOptions': { 'bar': {'dataLabels': {'enabled': True},'color': '#058DC7'}},'legend': {'enabled':False},'credits': {'enabled': False},'series': [{'name': 'Missing number','data':retail_amount}]                                                                 }
    cn_silo_bar={'chart': {'type': 'column','width':'1250'},'title': {'text':'Silo Daily Performance'},'xAxis': {'categories': silo_date },'yAxis': {'min': 0,'max':850,'title': {'text': 'Silo Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':silo_amount}]}
    cn_silo_bar_wd={'chart': {'type': 'column','width':'1250'},'title': {'text':'Silo Daily Performance'},'xAxis': {'categories': silo_date_wd },'yAxis': {'min': 0,'max':850,'title': {'text': 'Silo Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0,'color': '#007979'},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':silo_amount_wd}]}
    cn_retail_bar={'chart': {'type': 'column','width':'1250'},'title': {'text':'Retailer Daily Performance'},'xAxis': {'categories': retail_p_date },'yAxis': {'min': 0,'max':850,'title': {'text': ' Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':retail_p_amount}]}
    cn_retail_bar_wd={'chart': {'type': 'column','width':'1250'},'title': {'text':'Retailer Daily Performance'},'xAxis': {'categories': retail_date_wd },'yAxis': {'min': 0,'max':850,'title': {'text': ' Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0,'color': '#007979'},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':retail_amount_wd}]}
    if(p == "Last 7 days"):
        cn_json_line['xAxis']['tickInterval']=1
        cn_silo_bar['xAxis']['tickInterval']=1
        cn_retail_bar['xAxis']['tickInterval']=1
        cn_silo_bar_wd['xAxis']['tickInterval']=1
        cn_retail_bar_wd['xAxis']['tickInterval']=1
    elif(p == "Last 30 days"):
        cn_json_line['xAxis']['tickInterval']=2
        cn_silo_bar['xAxis']['tickInterval']=2
        cn_retail_bar['xAxis']['tickInterval']=2
        cn_silo_bar_wd['xAxis']['tickInterval']=2
        cn_retail_bar_wd['xAxis']['tickInterval']=2
    elif(p == "Last 3 months"):
        cn_json_line['xAxis']['tickInterval']=5
        cn_silo_bar['xAxis']['tickInterval']=5
        cn_retail_bar['xAxis']['tickInterval']=5
        cn_silo_bar_wd['xAxis']['tickInterval']=5
        cn_retail_bar_wd['xAxis']['tickInterval']=5
    elif(p == "Last 6 months"):
        cn_json_line['xAxis']['tickInterval']=10
        cn_silo_bar['xAxis']['tickInterval']=10
        cn_retail_bar['xAxis']['tickInterval']=10
        cn_silo_bar_wd['xAxis']['tickInterval']=10
        cn_retail_bar_wd['xAxis']['tickInterval']=10
    
    test1=""
    test2="<tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr>"
    for i in silo_pie.items():
        test1 = test1+"<tr><td>"+str(i[0])+"</td><td>"+str(i[1])+"</td></tr>"
        
    silo_html="<tr><td style='font-weight:bold;'>Siloname</td><td style='font-weight:bold;'>Missing numbers</td></tr>"+test2+test1

    json_data ={'cn_json_line':cn_json_line,'cn_json_pie':cn_json_pie,'cn_json_bar':cn_json_bar,'siloname':silo_pie,'silo_html':silo_html,'cn_silo_bar':cn_silo_bar,'cn_retail_bar':cn_retail_bar,'cn_silo_bar_wd':cn_silo_bar_wd,'cn_retail_bar_wd':cn_retail_bar_wd}
    json_data = simplejson.dumps(json_data)
    return HttpResponse(json_data,content_type='application/json')

@csrf_exempt
def daily_sla(request):
    dateText = request.POST.get("dateText")
    dateText= datetime.datetime.strptime(dateText,"%m/%d/%Y")
    dateText = dateText.strftime("%Y-%m-%d")
    d_sla_sql = 'SELECT ID,date,siloid,retailer,vendor,duration FROM test.cnhub where date="'+dateText+'" and duration >240 order by duration desc'
    sla_datas= Cnhub.objects.using('other').raw(d_sla_sql)
    table_html="<tbody>"
    table_head="<thead><tr><th>Date</th><th>SILOID</th><th>Retailer</th><th>Vendor</th><th>Process_Time(Minutes)</th></tr></thead>"
    for sla_data in sla_datas:
        table_html=table_html+"<tr><td>"+str(sla_data.date)+"</td>"+"<td>"+str(sla_data.siloid)+"</td><td>"+str(sla_data.retailer)+"</td><td>"+str(sla_data.vendor)+"</td><td>"+str(sla_data.duration)+"</td></tr>"
    table_html = table_html + "</tbody>"
    if table_html=="<tbody></tbody>":
        sla_daily= "No Missing today :)"
    else:
        sla_daily = table_head + table_html
    
    sla_daily=simplejson.dumps(sla_daily)
    return HttpResponse(sla_daily,content_type='application/json')

@csrf_exempt
def eu_daily_sla(request):
    dateText = request.POST.get("dateText")
    dateText= datetime.datetime.strptime(dateText,"%m/%d/%Y")
    dateText = dateText.strftime("%Y-%m-%d")
    d_sla_sql = 'SELECT ID,date,siloid,retailer,vendor,duration FROM test.euhub where date="'+dateText+'" and duration >240 order by duration desc'
    sla_datas= Cnhub.objects.using('other').raw(d_sla_sql)
    table_html="<tbody>"
    table_head="<thead><tr><th>Date</th><th>SILOID</th><th>Retailer</th><th>Vendor</th><th>Process_Time(Minutes)</th></tr></thead>"
    for sla_data in sla_datas:
        table_html=table_html+"<tr><td>"+str(sla_data.date)+"</td>"+"<td>"+str(sla_data.siloid)+"</td><td>"+str(sla_data.retailer)+"</td><td>"+str(sla_data.vendor)+"</td><td>"+str(sla_data.duration)+"</td></tr>"
    table_html = table_html + "</tbody>"
    if table_html=="<tbody></tbody>":
        sla_daily= "No Missing today :)"
    else:
        sla_daily = table_head + table_html
    
    sla_daily=simplejson.dumps(sla_daily)
    return HttpResponse(sla_daily,content_type='application/json')

@csrf_exempt
def ga_daily_sla(request):
    dateText = request.POST.get("dateText")
    dateText= datetime.datetime.strptime(dateText,"%m/%d/%Y")
    dateText = dateText.strftime("%Y-%m-%d")
    d_sla_sql = 'SELECT ID,date,siloid,retailer,vendor,duration FROM test.gahub where date="'+dateText+'" and duration >240 order by duration desc'
    sla_datas= Cnhub.objects.using('other').raw(d_sla_sql)
    table_html="<tbody>"
    table_head="<thead><tr><th>Date</th><th>SILOID</th><th>Retailer</th><th>Vendor</th><th>Process_Time(Minutes)</th></tr></thead>"
    for sla_data in sla_datas:
        table_html=table_html+"<tr><td>"+str(sla_data.date)+"</td>"+"<td>"+str(sla_data.siloid)+"</td><td>"+str(sla_data.retailer)+"</td><td>"+str(sla_data.vendor)+"</td><td>"+str(sla_data.duration)+"</td></tr>"
    table_html = table_html + "</tbody>"
    if table_html=="<tbody></tbody>":
        sla_daily= "No Missing today :)"
    else:
        sla_daily = table_head + table_html
    
    sla_daily=simplejson.dumps(sla_daily)
    return HttpResponse(sla_daily,content_type='application/json')


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def welcome(request):
    return render_to_response('welcome.html')

def eu(request):
    li={}
    retail=[]
    line=[]
    line_amount=[]  
    line_amount_w=[]
    retail_amount=[]
    raw_sql='select ID,Vendor,count(*) as count1 from test.Euhub where date > date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and duration >240 and dayofweek(date) not in (1,7) group by vendor limit 10'
    posts = Euhub.objects.using('other').raw(raw_sql)
    
    raw_sql_silo ='select ID,siloID,count(*) as count1 from (select ID,Date,SiloID,avg(duration) as t from test.Euhub group by SiloID,Date)a where t>240 and date > date_format(date_sub((select max(Date) from test.Euhub),interval 30 day),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by siloID order by count1 desc limit 10'
    silo_posts = Euhub.objects.using('other').raw(raw_sql_silo)
    
    raw_sql_retail='select ID,retailer,count(*) as count1 from test.Euhub where duration >240 and date > date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by retailer order by count(*) desc limit 10'
    retail_posts = Euhub.objects.using('other').raw(raw_sql_retail)
    
    raw_sql_line ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.Euhub where duration >240 group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and (select max(Date) from test.Euhub ) order by datefield'
    line_posts = Euhub.objects.using('other').raw(raw_sql_line)
    
    raw_sql_line_wd ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.Euhub where duration >240 and dayofweek(date) not in (1,7) group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and (select max(Date) from test.Euhub ) order by datefield'
    line_posts_wd = Euhub.objects.using('other').raw(raw_sql_line_wd)
    
    raw_silo_name_sql ='select ID,siloid from test.Euhub group by siloid'
    bar_silos=Euhub.objects.using('other').raw(raw_silo_name_sql)
    
    raw_retailer_name_sql='select ID,retailer from test.Euhub group by retailer'
    bar_retailers=Euhub.objects.using('other').raw(raw_retailer_name_sql)

    for post in posts:
        li[post.vendor.encode('ascii')]=int(post.count1)
     
    for retail_post in retail_posts:
        retail.append(retail_post.retailer)
        retail_amount.append(int(retail_post.count1))   
      
    for line_post in line_posts:
        line.append(line_post.datefield)
        line_amount.append(line_post.count1)   
    
    for line_post_wd in line_posts_wd:
        line_amount_w.append(line_post_wd.count1)
        
    lit=simplejson.dumps(li.items())
    retail=simplejson.dumps(retail)
    retail_amount=simplejson.dumps(retail_amount)
    line=simplejson.dumps(line,default=date_handler)
    line_amount=simplejson.dumps(line_amount)
    line_amount_w=simplejson.dumps(line_amount_w)
    return render_to_response('eu.html',{"lit":lit,"silo_posts":silo_posts,"retail":retail,"retail_amount":retail_amount,"line":line,"line_amount":line_amount,"line_amount_w":line_amount_w,"bar_silos":bar_silos,"bar_retailers":bar_retailers})

@csrf_exempt
def eu_aj_res(request):
    p=request.POST.get("p")
    s=request.POST.get("s")
    r=request.POST.get("r")
    cav_period="30 day"
    line=[]
    line_amount=[]  
    line_amount_w=[]
    retail_amount=[]
    silo_date=[]
    silo_date_wd=[]
    silo_amount=[]
    silo_amount_wd=[]
    retail_date_wd=[]
    retail_amount_wd=[]
    retail=[]
    v_pie={}
    silo_pie=OrderedDict()
    retail_p_date=[]
    retail_p_amount=[]
    if(p == "Last 7 days"): cav_period ="7 day"
    elif(p == "Last 30 days"):cav_period ="30 day"
    elif(p == "Last 3 months"):cav_period ="3 month"  
    elif(p == "Last 6 months"):cav_period ="6 month"
        
    raw_sql_line ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.Euhub where duration >240 group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Euhub ) order by datefield'        
    raw_sql_line_wd ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.Euhub where duration >240 and dayofweek(date) not in (1,7) group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Euhub ) order by datefield'       
    raw_sql_vendor='select ID,Vendor,count(*) as count1 from test.Euhub where date > date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and duration >240 and dayofweek(date) not in (1,7) group by vendor limit 10'
    raw_sql_retail='select ID,retailer,count(*) as count1 from test.Euhub where duration >240 and date > date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by retailer order by count(*) desc limit 10'
    raw_sql_silo ='select ID,siloID,count(*) as count1 from (select ID,Date,SiloID,avg(duration) as t from test.Euhub group by SiloID,Date)a where t>240 and date > date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by siloID order by count1 desc limit 10'
    raw_silos_p_sql ='SELECT ID,b.datefield,IFNULL(a.t,0) as duration from (select Date,siloID,round(avg(duration),0) AS t from test.Euhub where siloid="'+s+'" group by Date,siloID order by date desc) a right JOIN test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Euhub) order by datefield'
    raw_silos_p_sql_wd ='SELECT ID,b.datefield,IFNULL(a.t,0) as duration from (select Date,siloID,round(avg(duration),0) AS t from test.Euhub where siloid="'+s+'" group by Date,siloID order by date desc) a right JOIN test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Euhub) and dayofweek(datefield) not in (1,7) order by datefield'
    raw_retail_sql='select ID,b.datefield,IFNULL(d,0) as duration from(select Date,retailer,round(avg(duration),0) as d from test.Euhub where retailer="'+r+'" group by Date,retailer) a right join test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Euhub)'
    raw_retail_sql_wd='select ID,b.datefield,IFNULL(d,0) as duration from(select Date,retailer,round(avg(duration),0) as d from test.Euhub where retailer="'+r+'" group by Date,retailer) a right join test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.Euhub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Euhub) and dayofweek(datefield) not in (1,7)'
    silo_posts = Euhub.objects.using('other').raw(raw_sql_silo)
    retail_posts = Euhub.objects.using('other').raw(raw_sql_retail)
    line_posts = Euhub.objects.using('other').raw(raw_sql_line) 
    line_posts_wd = Euhub.objects.using('other').raw(raw_sql_line_wd)
    vendor_posts = Euhub.objects.using('other').raw(raw_sql_vendor)   
    raw_silos_p=Euhub.objects.using('other').raw(raw_silos_p_sql)
    raw_retails = Euhub.objects.using('other').raw(raw_retail_sql)
    raw_silos_p_wd = Euhub.objects.using('other').raw(raw_silos_p_sql_wd)
    raw_retails_wd = Euhub.objects.using('other').raw(raw_retail_sql_wd)
    
    for line_post_wd in line_posts_wd:
        line_amount_w.append(line_post_wd.count1)
            
    for line_post in line_posts:
        line.append(line_post.datefield)
        line_amount.append(line_post.count1)  
            
    for vendor_post in vendor_posts:
        v_pie[vendor_post.vendor.encode('ascii')]=int(vendor_post.count1)  
    
    for retail_post in retail_posts:
        retail.append(retail_post.retailer)
        retail_amount.append(int(retail_post.count1))   
    
    for silo_post in silo_posts:
        silo_pie[silo_post.siloid.encode('ascii')]=int(silo_post.count1)
    
    for raw_silo_p in raw_silos_p:
        silo_date.append(raw_silo_p.datefield)
        silo_amount.append(raw_silo_p.duration)
    
    for raw_retail in raw_retails:
        retail_p_date.append(raw_retail.datefield)
        retail_p_amount.append(int(raw_retail.duration))
    
    for raw_silo_p_wd in raw_silos_p_wd:
        silo_date_wd.append(raw_silo_p_wd.datefield)
        silo_amount_wd.append(raw_silo_p_wd.duration)
        
    for raw_retail_wd in raw_retails_wd:
        retail_date_wd.append(raw_retail_wd.datefield)
        retail_amount_wd.append(raw_retail_wd.duration)
    
    line=simplejson.loads(simplejson.dumps(line,default=date_handler))
    silo_date=simplejson.loads(simplejson.dumps(silo_date,default=date_handler))    
    retail_p_date=simplejson.loads(simplejson.dumps(retail_p_date,default=date_handler)) 
    silo_date_wd=simplejson.loads(simplejson.dumps(silo_date_wd,default=date_handler))
    retail_date_wd=simplejson.loads(simplejson.dumps(retail_date_wd,default=date_handler))
    
    cn_json_line={'chart':{'width':1250},'title': {'text': '',},'xAxis': {'categories': line,'tickInterval': 1 },'yAxis': {'title': {'text': 'Missing SLA Silo number'},'min':0,'plotLines': [{'value': 0,'width': 1,'color': '#808080',}]},'legend': {'layout': 'vertical','align': 'right','verticalAlign': 'middle','borderWidth': 0},'tooltip': {'shared': True,'crosshairs': True},'series': [{'name': 'Include Weekend','data': line_amount},{'name': 'Exclude Weekend','data': line_amount_w}]}

        
    v_pie=simplejson.dumps(v_pie.items())
    v_pie = simplejson.loads(v_pie)
    
    cn_json_pie={'chart': {'plotShadow': False,'width':390},'title': {'text': ''},'tooltip': {'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'},'plotOptions': {'pie': {'allowPointSelect': True,'cursor': 'pointer','dataLabels': {'enabled': False,},'showInLegend':True}},'series': [{'type': 'pie','name': 'Silo Missing Percentage','data':v_pie }]}
    cn_json_bar={'chart': {'type': 'bar','width':380},'title': {'text': ''},'xAxis': {'categories':retail ,'title': {'text': ''}},'yAxis': {'min': 0,'title': {'text': '','align': 'high'},'labels': {'overflow': 'justify'}},'plotOptions': { 'bar': {'dataLabels': {'enabled': True},'color': '#058DC7'}},'legend': {'enabled':False},'credits': {'enabled': False},'series': [{'name': 'Missing number','data':retail_amount}]                                                                 }
    cn_silo_bar={'chart': {'type': 'column','width':'1250'},'title': {'text':'Silo Daily Performance'},'xAxis': {'categories': silo_date },'yAxis': {'min': 0,'max':850,'title': {'text': 'Silo Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':silo_amount}]}
    cn_silo_bar_wd={'chart': {'type': 'column','width':'1250'},'title': {'text':'Silo Daily Performance'},'xAxis': {'categories': silo_date_wd },'yAxis': {'min': 0,'max':850,'title': {'text': 'Silo Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0,'color': '#007979'},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':silo_amount_wd}]}
    cn_retail_bar={'chart': {'type': 'column','width':'1250'},'title': {'text':'Retailer Daily Performance'},'xAxis': {'categories': retail_p_date },'yAxis': {'min': 0,'max':850,'title': {'text': ' Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':retail_p_amount}]}
    cn_retail_bar_wd={'chart': {'type': 'column','width':'1250'},'title': {'text':'Retailer Daily Performance'},'xAxis': {'categories': retail_date_wd },'yAxis': {'min': 0,'max':850,'title': {'text': ' Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0,'color': '#007979'},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':retail_amount_wd}]}
    if(p == "Last 7 days"):
        cn_json_line['xAxis']['tickInterval']=1
        cn_silo_bar['xAxis']['tickInterval']=1
        cn_retail_bar['xAxis']['tickInterval']=1
        cn_silo_bar_wd['xAxis']['tickInterval']=1
        cn_retail_bar_wd['xAxis']['tickInterval']=1
    elif(p == "Last 30 days"):
        cn_json_line['xAxis']['tickInterval']=2
        cn_silo_bar['xAxis']['tickInterval']=2
        cn_retail_bar['xAxis']['tickInterval']=2
        cn_silo_bar_wd['xAxis']['tickInterval']=2
        cn_retail_bar_wd['xAxis']['tickInterval']=2
    elif(p == "Last 3 months"):
        cn_json_line['xAxis']['tickInterval']=5
        cn_silo_bar['xAxis']['tickInterval']=5
        cn_retail_bar['xAxis']['tickInterval']=5
        cn_silo_bar_wd['xAxis']['tickInterval']=5
        cn_retail_bar_wd['xAxis']['tickInterval']=5
    elif(p == "Last 6 months"):
        cn_json_line['xAxis']['tickInterval']=10
        cn_silo_bar['xAxis']['tickInterval']=10
        cn_retail_bar['xAxis']['tickInterval']=10
        cn_silo_bar_wd['xAxis']['tickInterval']=10
        cn_retail_bar_wd['xAxis']['tickInterval']=10
    
    test1=""
    test2="<tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr>"
    for i in silo_pie.items():
        test1 = test1+"<tr><td>"+str(i[0])+"</td><td>"+str(i[1])+"</td></tr>"
        
    silo_html="<tr><td style='font-weight:bold;'>Siloname</td><td style='font-weight:bold;'>Missing numbers</td></tr>"+test2+test1

    json_data ={'cn_json_line':cn_json_line,'cn_json_pie':cn_json_pie,'cn_json_bar':cn_json_bar,'siloname':silo_pie,'silo_html':silo_html,'cn_silo_bar':cn_silo_bar,'cn_retail_bar':cn_retail_bar,'cn_silo_bar_wd':cn_silo_bar_wd,'cn_retail_bar_wd':cn_retail_bar_wd}
    json_data = simplejson.dumps(json_data)
    return HttpResponse(json_data,content_type='application/json')

def ga(request):
    li={}
    retail=[]
    line=[]
    line_amount=[]  
    line_amount_w=[]
    retail_amount=[]
    raw_sql='select ID,Vendor,count(*) as count1 from test.Gahub where date > date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and duration >240 and dayofweek(date) not in (1,7) group by vendor limit 10'
    posts = Gahub.objects.using('other').raw(raw_sql)
    
    raw_sql_silo ='select ID,siloID,count(*) as count1 from (select ID,Date,SiloID,avg(duration) as t from test.Gahub group by SiloID,Date)a where t>240 and date > date_format(date_sub((select max(Date) from test.Gahub),interval 30 day),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by siloID order by count1 desc limit 10'
    silo_posts = Gahub.objects.using('other').raw(raw_sql_silo)
    
    raw_sql_retail='select ID,retailer,count(*) as count1 from test.Gahub where duration >240 and date > date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by retailer order by count(*) desc limit 10'
    retail_posts = Gahub.objects.using('other').raw(raw_sql_retail)
    
    raw_sql_line ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.Gahub where duration >240 group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and (select max(Date) from test.Gahub ) order by datefield'
    line_posts = Gahub.objects.using('other').raw(raw_sql_line)
    
    raw_sql_line_wd ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.Gahub where duration >240 and dayofweek(date) not in (1,7) group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub(now(),interval 30 day),"%%Y-%%m-%%d") and (select max(Date) from test.Gahub ) order by datefield'
    line_posts_wd = Gahub.objects.using('other').raw(raw_sql_line_wd)
    
    raw_silo_name_sql ='select ID,siloid from test.Gahub group by siloid'
    bar_silos=Gahub.objects.using('other').raw(raw_silo_name_sql)
    
    raw_retailer_name_sql='select ID,retailer from test.Gahub group by retailer'
    bar_retailers=Gahub.objects.using('other').raw(raw_retailer_name_sql)

    for post in posts:
        li[post.vendor.encode('ascii')]=int(post.count1)
     
    for retail_post in retail_posts:
        retail.append(retail_post.retailer)
        retail_amount.append(int(retail_post.count1))   
      
    for line_post in line_posts:
        line.append(line_post.datefield)
        line_amount.append(line_post.count1)   
    
    for line_post_wd in line_posts_wd:
        line_amount_w.append(line_post_wd.count1)
        
    lit=simplejson.dumps(li.items())
    retail=simplejson.dumps(retail)
    retail_amount=simplejson.dumps(retail_amount)
    line=simplejson.dumps(line,default=date_handler)
    line_amount=simplejson.dumps(line_amount)
    line_amount_w=simplejson.dumps(line_amount_w)
    return render_to_response('ga.html',{"lit":lit,"silo_posts":silo_posts,"retail":retail,"retail_amount":retail_amount,"line":line,"line_amount":line_amount,"line_amount_w":line_amount_w,"bar_silos":bar_silos,"bar_retailers":bar_retailers})

@csrf_exempt
def ga_aj_res(request):
    p=request.POST.get("p")
    s=request.POST.get("s")
    r=request.POST.get("r")
    cav_period="30 day"
    line=[]
    line_amount=[]  
    line_amount_w=[]
    retail_amount=[]
    silo_date=[]
    silo_date_wd=[]
    silo_amount=[]
    silo_amount_wd=[]
    retail_date_wd=[]
    retail_amount_wd=[]
    retail=[]
    v_pie={}
    silo_pie=OrderedDict()
    retail_p_date=[]
    retail_p_amount=[]
    if(p == "Last 7 days"): cav_period ="7 day"
    elif(p == "Last 30 days"):cav_period ="30 day"
    elif(p == "Last 3 months"):cav_period ="3 month"  
    elif(p == "Last 6 months"):cav_period ="6 month"
        
    raw_sql_line ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.Gahub where duration >240 group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Gahub ) order by datefield'        
    raw_sql_line_wd ='select b.ID,b.datefield,IFNULL(a.count1,0) as count1 from (select ID,Date,count(*) as count1 from test.Gahub where duration >240 and dayofweek(date) not in (1,7) group by Date)a  right JOIN test.calendar b on a.date = b.datefield where b.datefield between date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Gahub ) order by datefield'       
    raw_sql_vendor='select ID,Vendor,count(*) as count1 from test.Gahub where date > date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and duration >240 and dayofweek(date) not in (1,7) group by vendor limit 10'
    raw_sql_retail='select ID,retailer,count(*) as count1 from test.Gahub where duration >240 and date > date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by retailer order by count(*) desc limit 10'
    raw_sql_silo ='select ID,siloID,count(*) as count1 from (select ID,Date,SiloID,avg(duration) as t from test.Gahub group by SiloID,Date)a where t>240 and date > date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and dayofweek(date) not in (1,7) group by siloID order by count1 desc limit 10'
    raw_silos_p_sql ='SELECT ID,b.datefield,IFNULL(a.t,0) as duration from (select Date,siloID,round(avg(duration),0) AS t from test.Gahub where siloid="'+s+'" group by Date,siloID order by date desc) a right JOIN test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Gahub) order by datefield'
    raw_silos_p_sql_wd ='SELECT ID,b.datefield,IFNULL(a.t,0) as duration from (select Date,siloID,round(avg(duration),0) AS t from test.Gahub where siloid="'+s+'" group by Date,siloID order by date desc) a right JOIN test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Gahub) and dayofweek(datefield) not in (1,7) order by datefield'
    raw_retail_sql='select ID,b.datefield,IFNULL(d,0) as duration from(select Date,retailer,round(avg(duration),0) as d from test.Gahub where retailer="'+r+'" group by Date,retailer) a right join test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Gahub)'
    raw_retail_sql_wd='select ID,b.datefield,IFNULL(d,0) as duration from(select Date,retailer,round(avg(duration),0) as d from test.Gahub where retailer="'+r+'" group by Date,retailer) a right join test.calendar b on a.date = b.datefield where datefield between date_format(date_sub((select max(Date) from test.Gahub),interval '+cav_period+'),"%%Y-%%m-%%d") and (select max(Date) from test.Gahub) and dayofweek(datefield) not in (1,7)'
    silo_posts = Gahub.objects.using('other').raw(raw_sql_silo)
    retail_posts = Gahub.objects.using('other').raw(raw_sql_retail)
    line_posts = Gahub.objects.using('other').raw(raw_sql_line) 
    line_posts_wd = Gahub.objects.using('other').raw(raw_sql_line_wd)
    vendor_posts = Gahub.objects.using('other').raw(raw_sql_vendor)   
    raw_silos_p=Gahub.objects.using('other').raw(raw_silos_p_sql)
    raw_retails = Gahub.objects.using('other').raw(raw_retail_sql)
    raw_silos_p_wd = Gahub.objects.using('other').raw(raw_silos_p_sql_wd)
    raw_retails_wd = Gahub.objects.using('other').raw(raw_retail_sql_wd)
    
    for line_post_wd in line_posts_wd:
        line_amount_w.append(line_post_wd.count1)
            
    for line_post in line_posts:
        line.append(line_post.datefield)
        line_amount.append(line_post.count1)  
            
    for vendor_post in vendor_posts:
        v_pie[vendor_post.vendor.encode('ascii')]=int(vendor_post.count1)  
    
    for retail_post in retail_posts:
        retail.append(retail_post.retailer)
        retail_amount.append(int(retail_post.count1))   
    
    for silo_post in silo_posts:
        silo_pie[silo_post.siloid.encode('ascii')]=int(silo_post.count1)
    
    for raw_silo_p in raw_silos_p:
        silo_date.append(raw_silo_p.datefield)
        silo_amount.append(raw_silo_p.duration)
    
    for raw_retail in raw_retails:
        retail_p_date.append(raw_retail.datefield)
        retail_p_amount.append(int(raw_retail.duration))
    
    for raw_silo_p_wd in raw_silos_p_wd:
        silo_date_wd.append(raw_silo_p_wd.datefield)
        silo_amount_wd.append(raw_silo_p_wd.duration)
        
    for raw_retail_wd in raw_retails_wd:
        retail_date_wd.append(raw_retail_wd.datefield)
        retail_amount_wd.append(raw_retail_wd.duration)
    
    line=simplejson.loads(simplejson.dumps(line,default=date_handler))
    silo_date=simplejson.loads(simplejson.dumps(silo_date,default=date_handler))    
    retail_p_date=simplejson.loads(simplejson.dumps(retail_p_date,default=date_handler)) 
    silo_date_wd=simplejson.loads(simplejson.dumps(silo_date_wd,default=date_handler))
    retail_date_wd=simplejson.loads(simplejson.dumps(retail_date_wd,default=date_handler))
    
    cn_json_line={'chart':{'width':1250},'title': {'text': '',},'xAxis': {'categories': line,'tickInterval': 1 },'yAxis': {'title': {'text': 'Missing SLA Silo number'},'min':0,'plotLines': [{'value': 0,'width': 1,'color': '#808080',}]},'legend': {'layout': 'vertical','align': 'right','verticalAlign': 'middle','borderWidth': 0},'tooltip': {'shared': True,'crosshairs': True},'series': [{'name': 'Include Weekend','data': line_amount},{'name': 'Exclude Weekend','data': line_amount_w}]}

        
    v_pie=simplejson.dumps(v_pie.items())
    v_pie = simplejson.loads(v_pie)
    
    cn_json_pie={'chart': {'plotShadow': False,'width':390},'title': {'text': ''},'tooltip': {'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'},'plotOptions': {'pie': {'allowPointSelect': True,'cursor': 'pointer','dataLabels': {'enabled': False,},'showInLegend':True}},'series': [{'type': 'pie','name': 'Silo Missing Percentage','data':v_pie }]}
    cn_json_bar={'chart': {'type': 'bar','width':380},'title': {'text': ''},'xAxis': {'categories':retail ,'title': {'text': ''}},'yAxis': {'min': 0,'title': {'text': '','align': 'high'},'labels': {'overflow': 'justify'}},'plotOptions': { 'bar': {'dataLabels': {'enabled': True},'color': '#058DC7'}},'legend': {'enabled':False},'credits': {'enabled': False},'series': [{'name': 'Missing number','data':retail_amount}]                                                                 }
    cn_silo_bar={'chart': {'type': 'column','width':'1250'},'title': {'text':'Silo Daily Performance'},'xAxis': {'categories': silo_date },'yAxis': {'min': 0,'max':850,'title': {'text': 'Silo Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':silo_amount}]}
    cn_silo_bar_wd={'chart': {'type': 'column','width':'1250'},'title': {'text':'Silo Daily Performance'},'xAxis': {'categories': silo_date_wd },'yAxis': {'min': 0,'max':850,'title': {'text': 'Silo Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0,'color': '#007979'},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':silo_amount_wd}]}
    cn_retail_bar={'chart': {'type': 'column','width':'1250'},'title': {'text':'Retailer Daily Performance'},'xAxis': {'categories': retail_p_date },'yAxis': {'min': 0,'max':850,'title': {'text': ' Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':retail_p_amount}]}
    cn_retail_bar_wd={'chart': {'type': 'column','width':'1250'},'title': {'text':'Retailer Daily Performance'},'xAxis': {'categories': retail_date_wd },'yAxis': {'min': 0,'max':850,'title': {'text': ' Process Duration    (Minutes)'}},'plotOptions': {'column': {'pointPadding': 0.2,'borderWidth': 0,'color': '#007979'},'series':{'groupPadding':0},},'legend':{'enabled':False,},'series': [{'name': 'Duration','data':retail_amount_wd}]}
    if(p == "Last 7 days"):
        cn_json_line['xAxis']['tickInterval']=1
        cn_silo_bar['xAxis']['tickInterval']=1
        cn_retail_bar['xAxis']['tickInterval']=1
        cn_silo_bar_wd['xAxis']['tickInterval']=1
        cn_retail_bar_wd['xAxis']['tickInterval']=1
    elif(p == "Last 30 days"):
        cn_json_line['xAxis']['tickInterval']=2
        cn_silo_bar['xAxis']['tickInterval']=2
        cn_retail_bar['xAxis']['tickInterval']=2
        cn_silo_bar_wd['xAxis']['tickInterval']=2
        cn_retail_bar_wd['xAxis']['tickInterval']=2
    elif(p == "Last 3 months"):
        cn_json_line['xAxis']['tickInterval']=5
        cn_silo_bar['xAxis']['tickInterval']=5
        cn_retail_bar['xAxis']['tickInterval']=5
        cn_silo_bar_wd['xAxis']['tickInterval']=5
        cn_retail_bar_wd['xAxis']['tickInterval']=5
    elif(p == "Last 6 months"):
        cn_json_line['xAxis']['tickInterval']=10
        cn_silo_bar['xAxis']['tickInterval']=10
        cn_retail_bar['xAxis']['tickInterval']=10
        cn_silo_bar_wd['xAxis']['tickInterval']=10
        cn_retail_bar_wd['xAxis']['tickInterval']=10
    
    test1=""
    test2="<tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr><tr><td></td></tr>"
    for i in silo_pie.items():
        test1 = test1+"<tr><td>"+str(i[0])+"</td><td>"+str(i[1])+"</td></tr>"
        
    silo_html="<tr><td style='font-weight:bold;'>Siloname</td><td style='font-weight:bold;'>Missing numbers</td></tr>"+test2+test1

    json_data ={'cn_json_line':cn_json_line,'cn_json_pie':cn_json_pie,'cn_json_bar':cn_json_bar,'siloname':silo_pie,'silo_html':silo_html,'cn_silo_bar':cn_silo_bar,'cn_retail_bar':cn_retail_bar,'cn_silo_bar_wd':cn_silo_bar_wd,'cn_retail_bar_wd':cn_retail_bar_wd}
    json_data = simplejson.dumps(json_data)
    return HttpResponse(json_data,content_type='application/json')



def wm(request):
    return render_to_response('walmart.html')



