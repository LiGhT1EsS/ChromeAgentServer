#!/usr/bin/env python2
# coding: utf-8

from __future__ import print_function

import threading
import base64

from flask import Flask
from flask import request
from flask import jsonify
import MySQLdb

from Settings import settings

__author__ = 'lightless'
__email__ = 'root@lightless.me'

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/receive')
def receive_url():

    url = request.args.get("u", "")
    if url == "":
        return jsonify(code=4001, message=u"参数为空")
    url = base64.b64decode(url)
    work_thread = threading.Thread(target=work_func, args=(url, ), name="work_func")
    work_thread.start()
    return jsonify(code=1001, message=u"任务已添加")


@app.route("/show")
def show_result():

    token = request.args.get("token", "")
    if token != settings.token:
        return jsonify(code=666, message=u'fuck you hacker!')
    conn = MySQLdb.connect(
        host=settings.db_host, user=settings.db_user, passwd=settings.db_password, db=settings.db_name
    )
    cursor = conn.cursor()
    sql = "SELECT url FROM chrome_agent_server.urls WHERE is_deleted != 1"
    cursor.execute(sql)
    qs = cursor.fetchall()

    return_value = list()
    for q in qs:
        return_value.append(q[0])

    return jsonify(code=1001, message=u"success", data=return_value)


def work_func(url):
    url = url.replace("\\", "\\\\")
    url = url.replace("'", "\\'")
    # print(url)
    conn = MySQLdb.connect(
        host=settings.db_host, user=settings.db_user, passwd=settings.db_password, db=settings.db_name
    )
    cursor = conn.cursor()
    sql = "SELECT COUNT(1) FROM chrome_agent_server.urls WHERE url = '{0}'".format(url)
    cursor.execute(sql)
    qs = cursor.fetchall()
    if int(qs[0][0]) == 0:
        # insert
        sql = "INSERT INTO chrome_agent_server.urls(url) VALUE ('{0}')".format(url)
        cursor.execute(sql)
        conn.commit()

    cursor.close()
    conn.close()


if __name__ == '__main__':
    app.run(debug=settings.debug, threaded=True, host=settings.listen_host, port=settings.listen_port)
