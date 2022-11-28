#! -*- coding: utf-8 -*-
"""
Author: arvin
Create type_time: 2022-11-01
Info: 定期向企业微信推送消息

修订内容: 从原代码每分钟发布一次提醒改成在设定时间点发送提醒，可以实现多时间点发布不同内容提醒信息并@所有人
"""
import datetime
import http
import json
import sys
import time

import requests

# 测试机器人1号,将此网址替换成你的群聊机器人Webhook地址
wx_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="
wx_info_path = "./conf/wx_user"
wx_robot_token = "./conf/token"


def append_last_line(file, line):
    with open(file, 'a', encoding="utf-8") as f:
        # 加\n换行显示
        f.write("\n" + line)


def get_url(file):
    with open(file, 'r', encoding="utf-8") as f:
        token = f.readline().strip('\n')
    return wx_url + token


def get_first_line(file):
    with open(file, 'r', encoding="utf-8") as f:
        first = f.readline().strip('\n')
    return first


def pop_line_from(file, del_line=1):  # del_line 行号从1开始
    with open(file, 'r', encoding="utf-8") as old_file:
        with open(file, 'r+', encoding="utf-8") as new_file:
            current_line = 0
            # 定位到需要删除的行
            while current_line < (del_line - 1):
                old_file.readline()
                current_line += 1
            # 当前光标在被删除行的行首，记录该位置
            seek_point = old_file.tell()
            # 设置光标位置
            new_file.seek(seek_point, 0)
            # 读需要删除的行，光标移到下一行行首
            del_line_content = old_file.readline()
            # 被删除行的下一行读给 next_line
            next_line = old_file.readline()
            # 连续覆盖剩余行，后面所有行上移一行
            while next_line:
                new_file.write(next_line)
                next_line = old_file.readline()
            # 写完最后一行后截断文件，因为删除操作，文件整体少了一行，原文件最后一行需要去掉
            new_file.truncate()
    # 剪切的行的内容, 去掉换行符
    return del_line_content.strip("\n")


def get_current_time():
    """获取当前时间，当前时分秒"""
    now = datetime.datetime.now()
    now_time = now.strftime('%Y-%m-%d %H:%M:%S')
    week = now.isoweekday()
    hour = now.strftime("%H")
    mm = now.strftime("%M")
    ss = now.strftime("%S")
    return now_time, week, hour, mm, ss


def sleep_time(hour, m, sec):
    """返回总共秒数"""
    return hour * 3600 + m * 60 + sec


def send_msg(content):
    """@全部，并发送指定信息"""
    data = json.dumps({
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list":
                ["@all"]
        }
    })
    r = requests.post(get_url(wx_robot_token), data, auth=('Content-Type', 'application/json'))
    return r.status_code


def every_time_send_msg(week_list=None, special_h1="09", special_m="00"):
    """每天指定时间发送指定消息"""
    if week_list is None:
        week_list = [1, 2, 3, 4, 5, 6, 7]
    print("配置信息：每周" + str(week_list) + ", " + special_h1 + "时" + special_m + "分" + "发送提醒消息...")
    print("任务启动...")
    w_list = week_list
    # 设置自动执行间隔时间
    while True:
        c_now, c_w, c_h, c_m, c_s = get_current_time()
        # 每天定时
        if w_list.count(c_w):
            if c_h > special_h1:
                rest = int(special_h1) - int(c_h) + 24
                sleep_t = (rest - 1) * 3600 + (60 - int(c_m)) * 60
                time.sleep(sleep_t)
            elif c_h < special_h1:
                rest = int(special_h1) - int(c_h)
                sleep_t = (rest - 1) * 3600 + (60 - int(c_m)) * 60
                time.sleep(sleep_t)
            elif c_h == special_h1:
                if c_w == "1":
                    print(c_now, "更新值班表信息...")
                    head = pop_line_from(wx_info_path)
                    append_last_line(wx_info_path, head)

                print(c_now, "获取本次值班人信息...")
                first = get_first_line(wx_info_path)
                print(c_now, '正在发送企业微信提醒...')
                code = send_msg("数据平台本周值班人: \n    " + first)
                if code == http.HTTPStatus.OK:
                    print(c_now, '发送成功...')
                time.sleep(86400 - int(c_m) * 60)
        else:
            rest = 24 - int(c_h)
            sleep_t = (rest - 1) * 3600 + (60 - int(c_m)) * 60
            time.sleep(sleep_t)


if __name__ == '__main__':
    week_l = sys.argv[1].split(",")
    special_hour = sys.argv[2]
    every_time_send_msg(week_l, special_hour)
