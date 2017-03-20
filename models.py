# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import django.utils.timezone as timezone
from datetime import datetime
from django.db import models
import sys
reload(sys)
sys.setdefaultencoding('utf8')

###模块表
class Modules(models.Model):
    module_ID = models.CharField(max_length=3)
    module_Name = models.CharField(max_length=255)
    class Meta:
        db_table = "display_Modules"
    def __unicode__(self):
        return str(self.module_Name)
###表单汇总表
class Tables(models.Model):
    module_ID = models.ForeignKey(Modules,on_delete=models.CASCADE)
    table_ID = models.CharField(max_length=5)
    table_Name = models.CharField(max_length=255)
    notes = models.CharField(max_length=255)
    class Meta:
        db_table = "display_Tables"
    def __unicode__(self):
        return str(self.table_Name)

###表单标签表
class Labels(models.Model):
    table_ID = models.ForeignKey(Tables,on_delete=models.CASCADE)
    label_ID = models.CharField(max_length=5)
    label_Name = models.CharField(max_length=255)
    class Meta:
        db_table = "display_Lables"
    def __unicode__(self):
        return str(self.label_Name)

###全平台每日基础指标汇总表
class Platform_summary_day(models.Model):
    date = models.DateField(default=datetime.now().date())
    table_ID = models.CharField(max_length=5,default='1')
    label_ID = models.CharField(max_length=5)
    label_Value = models.DecimalField(max_digits=15,decimal_places=1)
    class Meta:
        db_table = "display_Platform_summary_day"