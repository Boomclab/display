#coding:utf-8

import psycopg2
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



class Newmofang(object):

    """新魔方相关数据查询"""

    def __init__(self,**kwargs):
        self.search_dict = {'vv_platform_day': 'vv_cid_day', 'uv_platform_day': 'bid_uv_day','vv_platform_month': 'vv_cid_day',
                            'vv_terminal_day':'vv_cid_day','uv_terminal_day':'bid_uv_day','vv_channel_day':'vv_cid_day','uv_channel_day':'cid_uv_day'}  ###数据查询用表
        self.func_dict = {"vv_platform_month": self.vv_platform_month,"vv_platform_day": self.vv_platform_day,"uv_platform_day": self.uv_platform_day,
                          "vv_terminal_day":self.vv_terminal_day,"uv_terminal_day":self.uv_terminal_day,"vv_channel_day":self.vv_channel_day,"uv_channel_day":self.uv_channel_day}  ###查询对应模块
        self.bid_dict = {"1":"ott","102":"pcweb","104":"phonem","5":"padweb","6":"macclient",
                         "7":"win10client","8":"pcclient","9":"android","10":"apad","11":"ipad","12":"iphone","13":"mui"}###魔方数据库中bid对应的终端
        self.cid_dict = {"1":"show","2":"tv","3":"movie","7":"cartoon","87":"show","83":"tv","84":"movie","88":"cartoon"}###媒资数据库中cid对应的频道
        self.bid_not_in = 'bid not in (2,4)'###魔方数据库设计中的刷量频道，现在为bid in (2,4)
        try:###初始化数据库连接
            self.conn = psycopg2.connect(database="dm_result", user="product_readonly", password="deDr7Toi29Sj&SkDS#LL",
                                    host="10.100.5.85", port="2345")
            self.cursor = self.conn.cursor()
        except psycopg2.OperationalError:
            print datetime.datetime.now().date()
            print ("新魔方数据库无法连接")
            self.conn = None
            self.cursor = None
        if "start_date" in kwargs:
            self.start_date = kwargs['start_date']
        if "end_date" in kwargs:
            self.end_date = kwargs['end_date']
        if "searchtype" in kwargs:
            self.searchtype = kwargs['searchtype']###查询模块
            self.table = self.search_dict[self.searchtype]  ###返回查询的数据对应的表



    def func(self):###按照查询模块调取具体函数
        return self.func_dict.get(self.searchtype)

    def sql_query(self):###具体查询，返回结果
        if self.conn != None:###判断数据库连接是否正常
            sql = self.func()()
            print sql
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            self.conn.commit()
            self.conn.close()
            # print self.table
        else:
            result = None
        return result

    def vv_platform_month(self):###全平台月vv汇总模块
        sql = "select substring(date from 1 for 6) as date,sum(vv) as vv from {table} where date>='20160101' and date<='{end_date}' and {bid_not_in} " \
              "GROUP BY substring(date from 1 for 6) order by substring(date from 1 for 6)".format(table=self.table,end_date=self.end_date,bid_not_in=self.bid_not_in)
        return sql

    def vv_platform_day(self):###全平台每日vv
        sql = "select date,sum(vv) as vv from {table} where {bid_not_in} and date>='{start_time}' and date<='{end_time}' group by date order by date".format(table=self.table,start_time=self.start_date,end_time=self.end_date,bid_not_in=self.bid_not_in)
        return sql

    def uv_platform_day(self):###全平台每日uv
        sql = "select date,sum(uv) as uv from {table} where {bid_not_in} and date>='{start_time}' and date<='{end_time}' group by date order by date".format(table=self.table,start_time=self.start_date,end_time=self.end_date,bid_not_in=self.bid_not_in)
        return sql

    def vv_terminal_day(self):###按频道查询vv
        case_when_sql = self.bid_sql()
        sql = "select date,{case_when_sql} as bid_name,sum(vv) as vv from {table} " \
              "where {bid_not_in} and date>='{start_time}' and date<='{end_time}' group by date,bid order by date".format(case_when_sql=case_when_sql,table=self.table,start_time=self.start_date,end_time=self.end_date,bid_not_in=self.bid_not_in)
        return sql

    def uv_terminal_day(self):
        case_when_sql = self.bid_sql()
        sql = "select date,{case_when_sql} as bid_name,sum(uv) as uv from {table} " \
              "where {bid_not_in} and date>='{start_time}' and date<='{end_time}' group by date,bid order by date".format(case_when_sql=case_when_sql,table=self.table,start_time=self.start_date,end_time=self.end_date,bid_not_in=self.bid_not_in)
        return sql

    def vv_channel_day(self):
        case_when_sql = self.cid_sql()
        sql = "select date,{case_when_sql} as cid_name,sum(vv) as vv from {table} " \
              "where {bid_not_in} and date>='{start_time}' and date<='{end_time}' group by date,cid_name order by date".format(case_when_sql=case_when_sql,table=self.table,start_time=self.start_date,end_time=self.end_date,bid_not_in=self.bid_not_in)
        return sql

    def uv_channel_day(self):
        case_when_sql = self.cid_sql()
        sql = "select date,{case_when_sql} as cid_name,sum(uv) as uv from {table} " \
              "where {bid_not_in} and date>='{start_time}' and date<='{end_time}' group by date,cid_name order by date".format(case_when_sql=case_when_sql,table=self.table,start_time=self.start_date,end_time=self.end_date,bid_not_in=self.bid_not_in)
        return sql

    def bid_sql(self):###构造bid sql
        sql = 'case bid '
        for bid in self.bid_dict.keys():
            sql += "when {bid} then '{bid_name}' ".format(bid=bid,bid_name=self.bid_dict[bid])
        sql += "else 'else' end"
        return sql

    def cid_sql(self):###构造bid sql
        sql = 'case cid '
        for cid in self.cid_dict.keys():
            sql += "when {cid} then '{cid_name}' ".format(cid=cid,cid_name=self.cid_dict[cid])
        sql += "else 'else' end"
        return sql


    def datetime_process(self):###返回查询中开始时间与结束时间段内的日期列表
        start_date = datetime.datetime.strptime(self.start_date, '%Y%m%d').date()  ###字符串转换为日期格式
        end_date = datetime.datetime.strptime(self.end_date, '%Y%m%d').date()
        date_list = list()
        curr_date = start_date + datetime.timedelta(1)
        date_list.append("%04d%02d%02d" % (start_date.year, start_date.month, start_date.day))
        while curr_date != end_date:
            date_list.append("%04d%02d%02d" % (curr_date.year, curr_date.month, curr_date.day))
            curr_date += datetime.timedelta(1)
        date_list.append("%04d%02d%02d" % (curr_date.year, curr_date.month, curr_date.day))
        return date_list



if __name__ == '__main__':
    # print newmofang(searchtype='vv_platform_month').sql_query()
    # print newmofang(searchtype='vv_platform_day',start_date='20170301',end_date='20170307').sql_query()
    # print newmofang(searchtype='vv_terminal_day', start_date='20170301', end_date='20170307').sql_query()
    print Newmofang(searchtype='uv_channel_day',start_date='20170301', end_date='20170307').sql_query()
    # print newmofang('vv','20170102','20170302').sql_query()
    # print newmofang('uv','20170102','20170302').sql_query()