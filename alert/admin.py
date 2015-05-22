from django.contrib import admin
import models

class cusAdmin(admin.ModelAdmin):
   list_display = ('date','silo','sla_status','delay_reason','personnel')
    
class masterAd(admin.ModelAdmin):
    list_display = ('silo','production_day','sla')
    
class taskAD(admin.ModelAdmin):
   
    list_display = ('retailer','task','frequency','weekday','hub','task_owner')
    

admin.site.register(models.AlertMaster,masterAd)
admin.site.register(models.AlertStatus,cusAdmin)
admin.site.register(models.TaskSum,taskAD)


