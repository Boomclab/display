#coding:utf-8
from django.shortcuts import render,redirect,get_object_or_404,render_to_response
from .models import *
from django.http import  HttpResponseRedirect,HttpResponse
from django.db import connection
from SQLclass import Newmofang
import datetime
import json
import psycopg2
import MySQLdb
# Create your views here.
import sys
reload(sys)
sys.setdefaultencoding('utf8')


###全平台模???
def platform(request):

    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).date().strftime('%Y%m%d')###查询开始时???
    end_date = (datetime.datetime.now()-datetime.timedelta(days=1)).date().strftime('%Y%m%d')###查询结束时间

    ###查询月vv
    vv_month_result = Newmofang(searchtype='vv_platform_month',end_date=end_date).sql_query()

    ###查询日vv
    vv_day_result = Newmofang(searchtype='vv_platform_day',start_date=start_date,end_date=end_date).sql_query()
    ###查询日uv
    uv_day_result = Newmofang(searchtype='uv_platform_day',start_date=start_date,end_date=end_date).sql_query()

    ###查询频道vv、uv
    date_list = Newmofang(start_date=start_date, end_date=end_date).datetime_process()
    terminal_list = Newmofang().bid_dict.values()
    vv_terminal_day_result = Newmofang(searchtype='vv_terminal_day',start_date=start_date,end_date=end_date).sql_query()
    # print vv_terminal_day_result
    uv_terminal_day_result = Newmofang(searchtype='uv_terminal_day',start_date=start_date,end_date=end_date).sql_query()


    ###查询频道vv、uv
    channel_list = Newmofang().cid_dict.values()
    vv_channel_day_result = Newmofang(searchtype='vv_channel_day', start_date=start_date, end_date=end_date).sql_query()
    uv_channel_day_result = Newmofang(searchtype='uv_channel_day', start_date=start_date, end_date=end_date).sql_query()
    print uv_channel_day_result


    ###数据转化为列表传入前???
    vv_month_date, vv_month_lastyear, vv_month_thisyear = vv_platform_month_process(vv_month_result=vv_month_result)###第一???全平台月度uv数据
    vv_day_date, vv_day_data, uv_day_data,vv_day_perperson = vv_platform_day_process(vv_day_result=vv_day_result,uv_day_result=uv_day_result)###第二、三张全平台日vv、uv、人均vv数据
    vv_terminal_day_dict = vv_terminal_day_process(vv_terminal_day_result=vv_terminal_day_result,date_list=date_list,terminal_list=terminal_list)  ###第四张分端vv变化
    uv_terminal_day_dict = uv_terminal_day_process(uv_terminal_day_result=uv_terminal_day_result, date_list=date_list,terminal_list=terminal_list)  ###第五张分端uv变化
    vv_channel_day_dict = vv_channel_day_process(vv_channel_day_result=vv_channel_day_result, date_list=date_list,channel_list=channel_list)  ###第六张分频道vv变化
    uv_channel_day_dict = uv_channel_day_process(uv_channel_day_result=uv_channel_day_result, date_list=date_list,channel_list=channel_list)  ###第七张分频道uv变化
    print uv_channel_day_dict

    return render(request, 'index.html', {'vv_day_date':json.dumps(vv_day_date),'vv_day_data':json.dumps(vv_day_data),
                                       'uv_day_data': json.dumps(uv_day_data),'vv_day_perperson':json.dumps(vv_day_perperson),
                                       'vv_month_date':json.dumps(vv_month_date),'vv_month_lastyear':json.dumps(vv_month_lastyear),
                                       'vv_month_thisyear':json.dumps(vv_month_thisyear),'vv_terminal_day_dict':vv_terminal_day_dict,
                                       'uv_terminal_day_dict':uv_terminal_day_dict,'vv_channel_day_dict':vv_channel_day_dict,
                                       'uv_channel_day_dict':uv_channel_day_dict})


def ltt(request):
    return render(request,'indexTwo.html')




def data_format(result):###sql返回结果处理
    if result != []:
        date_list = [each[0] for each in result]###日期列表
        data_list = [round(each[1]/10000,1) for each in result]###数据列表
        return date_list,data_list###返回x轴时间列表和y轴

def vv_platform_month_process(vv_month_result):###月vv处理
    vv_month_data = data_format(vv_month_result)[1]
    ###月份列表
    vv_month_date = [str(i) + '月' for i in range(1, 13)]
    ###第一年vv
    vv_month_lastyear = vv_month_data[:12]
    vv_month_thisyear = vv_month_data[12:]
    return vv_month_date,vv_month_lastyear,vv_month_thisyear

def vv_platform_day_process(vv_day_result,uv_day_result):###日vv、uv、人均vv处理
    vv_day_date,vv_day_data = data_format(vv_day_result)
    uv_day_date, uv_day_data = data_format(uv_day_result)
    vv_day_perperson = list(map(lambda x:round(x[0]/x[1],1),zip(vv_day_data,uv_day_data)))
    # print ("{vv_day_data} \n {uv_day_data} \n {vv_day_perperson}").format(vv_day_data=vv_day_data,uv_day_data=uv_day_data,vv_day_perperson=vv_day_perperson)
    return vv_day_date,vv_day_data,uv_day_data,vv_day_perperson

def vv_terminal_day_process(vv_terminal_day_result,date_list,terminal_list):
    vv_terminal_day_dict = dict()###返回的数据字典，数据格式为：  {终端1：[列表1],终端2：[列表2]}
    for terminal in terminal_list:
        terminal_list = list()###每个终端对应的字???
        for date in date_list:
            for result in vv_terminal_day_result:
                if date == str(result[0]) and terminal == str(result[1]):
                    terminal_list.append(round(result[2]/10000,1))
        vv_terminal_day_dict[terminal] = terminal_list
    return vv_terminal_day_dict

def uv_terminal_day_process(uv_terminal_day_result,date_list,terminal_list):
    uv_terminal_day_dict = dict()###返回的数据字典，数据格式为：  {终端1：[列表1],终端2：[列表2]}
    for terminal in terminal_list:
        terminal_list = list()###每个终端对应的字???
        for date in date_list:
            for result in uv_terminal_day_result:
                if date == str(result[0]) and terminal == str(result[1]):
                    terminal_list.append(round(result[2]/10000,1))
        uv_terminal_day_dict[terminal] = terminal_list
    return uv_terminal_day_dict

def vv_channel_day_process(vv_channel_day_result,date_list,channel_list):
    vv_channel_day_dict = dict()###返回的数据字典，数据格式为：  {终端1：[列表1],终端2：[列表2]}
    for channel in channel_list:
        channel_list = list()###每个终端对应的字???
        for date in date_list:
            for result in vv_channel_day_result:
                if date == str(result[0]) and channel == str(result[1]):
                    channel_list.append(round(result[2]/10000,1))
        vv_channel_day_dict[channel] = channel_list
    return vv_channel_day_dict

def uv_channel_day_process(uv_channel_day_result,date_list,channel_list):
    uv_channel_day_dict = dict()###返回的数据字典，数据格式为：  {终端1：[列表1],终端2：[列表2]}
    for channel in channel_list:
        channel_list = list()###每个终端对应的字???
        for date in date_list:
            for result in uv_channel_day_result:
                if date == str(result[0]) and channel == str(result[1]):
                    channel_list.append(round(result[2]/10000,1))
        uv_channel_day_dict[channel] = channel_list
    return uv_channel_day_dict
