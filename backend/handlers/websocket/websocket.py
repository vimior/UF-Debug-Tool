#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, Vinman, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.cub@gmail.com>

import json
import threading
import paramiko
import queue
import time
import datetime
from tornado import gen
from tornado import websocket


class SSHThread(threading.Thread):
    def __init__(self, client):
        super(SSHThread, self).__init__()
        self.daemon = True
        self.client = client
        self.wx_que = queue.Queue()
        self.client.info['ssh']['wx_que'] = self.wx_que

    def run(self):
        try:
            sshclient = paramiko.SSHClient()
            sshclient.load_system_host_keys()
            sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshclient.connect(self.client.info['ssh']['host'],
                              self.client.info['ssh']['port'],
                              self.client.info['ssh']['username'],
                              self.client.info['ssh']['password'])
            channel = sshclient.invoke_shell(term='xterm')
            channel.resize_pty(width=200, height=24)
            channel.settimeout(0)
            print('ssh start')
            self.client.info['ssh']['sshclient'] = sshclient
            self.client.info['ssh']['channel'] = channel
            while self.client.connected and not channel.exit_status_ready():
                time.sleep(0.01)
                try:
                    if not self.wx_que.empty():
                        channel.send(self.wx_que.get())
                except:
                    pass
                try:
                    data = channel.recv(1024)
                    if data:
                        self.client.write_message(data)
                except:
                    pass
            try:
                sshclient.close()
                self.client.close()
            except:
                pass
            print('ssh stop')
        except Exception as e:
            print(e)
            try:
                self.client.write_message('connect failed\n')
                time.sleep(0.5)
                self.client.close()
            except:
                pass


class WebSocketHandler(websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        self._info = {}
        self._connected = False

    @property
    def connected(self):
        return self._connected

    @property
    def info(self):
        return self._info

    def check_origin(self, origin):
        return True

    @gen.coroutine
    def open(self, *args, **kwargs):
        self._info['type'] = self.get_argument('type', 'cmd')
        self._info['remote_ip'] = self.request.remote_ip
        self._info['id'] = id(self)
        self._connected = True
        if self.info['type'] == 'ssh':
            self._info['ssh'] = {
                'host': None,
                'port': None,
                'username': None,
                'password': None,
                'sshclient': None,
                'channel': None,
                'wx_que': None,
            }
        print('A new ws client [type:{}] [id:{}] [addr:{}], {}'.format(
            self.info['type'],
            self.info['id'],
            self.info['remote_ip'],
            datetime.datetime.now()))

    def on_close(self):
        self._connected = False
        print('ws client [type:{}] [id:{}] [addr:{}], closed on {}'.format(
            self.info['type'],
            self.info['id'],
            self.info['remote_ip'],
            datetime.datetime.now()))

    def on_message(self, message):
        if self.info['type'] == 'ssh':
            if self.info['ssh']['sshclient'] is None:
                try:
                    jsonData = json.loads(message)
                    if jsonData['cmd'] == 'ssh_connect':
                      self.info['ssh']['host'] = jsonData['data']['host']
                      self.info['ssh']['port'] = jsonData['data']['port']
                      self.info['ssh']['username'] = jsonData['data']['username']
                      self.info['ssh']['password'] = jsonData['data']['password']
                      SSHThread(self).start()
                except:
                  pass
            elif self.info['ssh']['wx_que'] is not None:
                self.info['ssh']['wx_que'].put(message)



