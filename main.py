# !/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
import sys
from PyQt5.Qt import QApplication, QWidget, QIcon, QPixmap
from PyQt5.QtCore import QThread
from ui import UFDebugToolUI
from log import logger, LogWindow
from tornado import ioloop
from tornado import web
from backend.handlers.websocket import WebSocketHandler
from backend.handlers.http import VueHandler

icon_path = os.path.join(os.path.split(sys.path[0])[0], 'icon')
if not os.path.exists(icon_path):
    icon_path = os.path.join(os.getcwd(), 'icon')

static_path = os.path.join(os.path.split(sys.path[0])[0], 'backend', 'static')
if not os.path.exists(static_path):
    static_path = os.path.join(os.getcwd(), 'backend', 'static')
template_path = os.path.join(os.path.split(sys.path[0])[0], 'backend', 'templates')
if not os.path.exists(template_path):
    template_path = os.path.join(os.getcwd(), 'backend', 'templates')


class TornadoThread(QThread):
    def __init__(self):
        super(TornadoThread, self).__init__()

    def run(self):
        try:
            self.run_backend()
        except Exception as e:
            print(e)

    @staticmethod
    def run_backend():
        settings = {
            'template_path': template_path,
            'static_path': static_path
        }
        handlers = [
            (r'/ws', WebSocketHandler),
            (r'/', VueHandler),
        ]

        address = '0.0.0.0'
        port = 10086
        app = web.Application(handlers, **settings)
        app.listen(port, address=address)
        print('server listen on {}:{}'.format(address, port))
        pid = os.getpid()
        ppid = os.getppid()
        print('server process pid: {}, ppid: {}'.format(pid, ppid))

        main_ioloop = ioloop.IOLoop.instance()
        main_ioloop.start()


class UFDebugTool(QWidget):
    def __init__(self):
        super(UFDebugTool, self).__init__()
        self.ui = UFDebugToolUI(self)
        self.log_window = LogWindow(self)
        icon = QIcon()
        icon.addPixmap(QPixmap(os.path.join(icon_path, 'main.png')), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.log_window.setWindowIcon(icon)

        self.tornado_thread = TornadoThread()
        self.tornado_thread.start()

        # self.log_window.show()
        # logger.debug('*****debug log style******')
        # logger.info('*****info log style******')
        # logger.warn('*****warn log style******')
        # logger.error('*****error log style******')
        # logger.critical('*****critical log style******')
        # sys.stdout.write('*****stdout style******')
        # sys.stderr.write('*****stderr style******')
        # print('*****print style******')

    def closeEvent(self, event):
        self.log_window.close()
        super(UFDebugTool, self).closeEvent(event)

    def show(self):
        super(UFDebugTool, self).show()
        if self.log_window.isHidden():
            self.ui.logAction.setText('Open-Log')
        else:
            self.ui.logAction.setText('Close-Log')


def main():
    app = QApplication(sys.argv)
    controller = UFDebugTool()
    icon = QIcon()
    icon.addPixmap(QPixmap(os.path.join(icon_path, 'main.png')), QIcon.Normal, QIcon.Off)
    controller.setWindowIcon(icon)
    controller.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
