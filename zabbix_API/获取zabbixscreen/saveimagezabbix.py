#!/usr/bin/python
# -*- coding:utf-8 -*-


import time,os
import urllib
import urllib2
import cookielib
import MySQLdb
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time


global mail_user
global mail_host

mailsenduser = 'XXXX'
mailto_list = ['XXX.com']
mail_host = "smtp.126.com"
mail_user = "XXXX@126.com"
mail_pass = "XXXX"
mail_postfix = "126.com"


screens = ["1.Cpu", "2.Menmory", "9.jdbc_connetction", "PV", "nginx_4XX", "3.ecs_load", "11.tomcat_threads_main1", "12.tomcat_threads_main2", "13.tomcat_threads_main3", "10.tomcat_memory_heap"]
for screen in screens:
    save_graph_path = "./reports/%s/%s" % (time.strftime("%Y-%m-%d"), screen)
    if not os.path.exists(save_graph_path):
        os.makedirs(save_graph_path)

zabbix_host = "zabbix.com"
username = "XXXX"
password = "XXXx"
width = 600
height = 100
period = 86400

# zabbix DB

dbhost = "XXXX"
dbport = 3306
dbuser = "XXXX"
dbpasswd = "XXXX"
dbname = "XXXX"


def mysql_query(sql):
    try:
        conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, port=dbport, connect_timeout=20)
        conn.select_db(dbname)
        cur = conn.cursor()
        count = cur.execute(sql)
        if count == 0:
            result = 0
        else:
            result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print "mysql error:", e


def get_graph(zabbix_host, username, password, screen, width, height, period, save_graph_path):
    screenid_list = []
    for i in mysql_query("select screenid from screens where name='%s'" % (screen)):
                for screenid in i:
                    graphid_list = []
                    for c in mysql_query("select resourceid from screens_items where screenid='%s'" % (int(screenid))):
                        for d in c:
                            graphid_list.append(int(d))
                    for graphid in graphid_list:
                        login_opt = urllib.urlencode({
                        "name": username,
                        "password": password,
                        "autologin": 1,
                        "enter": "Sign in"})
                        get_graph_opt = urllib.urlencode({
                        "graphid": graphid,
                        "screenid": screenid,
                        "width": width,
                        "height": height,
                        "period": period})
                        cj = cookielib.CookieJar()
                        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                        login_url = r"http://%s/index.php" % zabbix_host
                        save_graph_url = r"http://%s/chart2.php" % zabbix_host
                        opener.open(login_url, login_opt).read()
                        data = opener.open(save_graph_url, get_graph_opt).read()
                        filename = "%s/%s.%s.png" % (save_graph_path, screenid, graphid)
                        f = open(filename, "wb")
                        f.write(data)
                        f.close()


def send_mail(to_list, sub, save_graph_path):
    def addimg(src, imgid):
        fp = open(src, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', imgid)
        return msgImage


    def getfilename(save_graph_path):
        filename = os.listdir(save_graph_path)
        return filename


    msg = MIMEMultipart('related')
    imagehtml = ""
    for htmlnumber in range(len(getfilename(save_graph_path))):
        p = htmlnumber +1
        if p % 2 != 0:
            imagename1 = 'name' + str(p)
            imagename2 = 'name' + str(p+1)
            imagehtml = imagehtml + '<tr bgcolor="#EFEBDE" height="100" style="font-size:13px">' + '<td>' + '<img src="cid:' + imagename1 +'"></td><td>'+ '<img src="cid:' + imagename2 + '"></td>' + '</tr>'
    imagehtmls = '<table width="600" border="0" cellspacing="0" cellpadding="4"><tr bgcolor="#CECFAD" height="20" style="font-size:14px"><td colspan=2>监控日报<a href="zabbix.dinghuo123.com">更多>></a></td></tr>' + imagehtml+'</table>'
    msgtext = MIMEText(imagehtmls, "html", "utf-8")
    msg.attach(msgtext)
    for numb in range(len(getfilename(save_graph_path))):
        imagename = 'name' + str(numb + 1)
        imagdir = save_graph_path + '/' + getfilename(save_graph_path)[numb]
        msg.attach(addimg(imagdir, imagename))
    zabbixmsglog = open('', 'a')
    zabbixmsglog.write(str(imagdir) + ': ' + str(imagename))
    zabbixmsglog.close()

    me = "XXX@126.com"
    msg['Subject'] = u"监控日报" + str(time.strftime("%Y-%m-%d")) + ":" + sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False



if __name__ == '__main__':
    for screen in screens:
        save_graph_path = "./reports/%s/%s" % (time.strftime("%Y-%m-%d"), screen)
        get_graph(zabbix_host, username, password, screen, width, height, period, save_graph_path)

        if send_mail(mailto_list, screen, save_graph_path):
            print("suss")
        else:
            print("error")
    # 发送间隔延长，否则不予发送
    time.sleep(20)


