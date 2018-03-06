# -*- coding: utf-8 -*-
import paramiko
import time
import paramiko
import select
import sys

def text_save(content, filename):
    file = open(filename, 'a')
    for i in content:
        # file.write(u' '.join((i)).encode('utf-8').strip() + '\n')
        file.write(i.encode('utf-8', 'ignore'))
    file.close()


def readlog(serverip, port, user, pwd, file_dir):
    #log_now_time = time.strftime('%Y-%m-%d%H:%M:%S', time.localtime(time.time()))
    paramiko.util.log_to_file("paramiko.log")
    log_now_day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=serverip, port=port, username=user, password=pwd, timeout=4)
    # 开启channel 管道
    transport = client.get_transport()
    channel = transport.open_session()
    channel.get_pty()
    # 执行命令nohup.log
    tail = 'tail -20f %s' % file_dir
    # 将命令传入管道中
    channel.exec_command(tail)
    while True:
        # 判断退出的准备状态
        if channel.exit_status_ready():
            break
        try:
            # 通过socket进行读取日志
            rl, wl, el = select.select([channel], [], [])
            if len(rl) > 0:
                recv = channel.recv(1024)
                # 此处将获取的数据解码成gbk的存入本地日志
                print(recv.decode('utf-8', 'ignore'))
                text_save(recv.decode('utf-8', 'ignore'), 'tail(' + serverip + '-' + log_now_day + ').txt')
        # 键盘终端异常
        except KeyboardInterrupt:
            print("Caught control-C")
            channel.send("\x03")  # 发送 ctrl+c
            channel.close()
    client.close()


def main():
    serverip = sys.argv[1]
    user = 'test'
    file_dir = sys.argv[2]
    pwd = sys.argv[3]
    port = 22
    readlog(serverip, port, user, pwd, file_dir)


if __name__ == '__main__':
    main()