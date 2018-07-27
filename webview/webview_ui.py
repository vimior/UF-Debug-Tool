#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import os
import sys
from PyQt5.Qt import QFrame, QHBoxLayout, QLineEdit, QUrl, QAction, QToolBar, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

icon_path = os.path.join(os.path.split(sys.path[0])[0], 'icon')
if not os.path.exists(icon_path):
    icon_path = os.path.join(os.getcwd(), 'icon')

back_icon = os.path.join(icon_path, 'back.png')
forward_icon = os.path.join(icon_path, 'forward.png')
stop_icon = os.path.join(icon_path, 'stop.png')
reload_icon = os.path.join(icon_path, 'reload.png')


class WebViewUI(object):
    def __init__(self, ui, layout):
        self.main_ui = ui
        self.layout = layout
        super(WebViewUI, self).__init__()
        self.set_ui()

    def set_ui(self):
        self._set_top_ui()
        self._set_down_ui()

    def _set_top_ui(self):
        up_frame = QFrame()
        self.up_layout = QHBoxLayout(up_frame)
        self.layout.addWidget(up_frame)
        self.toolbar = QToolBar()
        self.up_layout.addWidget(self.toolbar)
        self.action_back = QAction(QIcon(back_icon), '')
        self.action_forward = QAction(QIcon(forward_icon), '')
        self.action_reload = QAction(QIcon(reload_icon), '')
        self.action_stop = QAction(QIcon(stop_icon), '')
        self.toolbar.addAction(self.action_back)
        self.toolbar.addAction(self.action_forward)
        self.toolbar.addAction(self.action_stop)
        self.toolbar.addAction(self.action_reload)
        self.action_stop.setVisible(False)
        self.action_reload.setVisible(True)
        self.toolbar.addSeparator()
        self.lnt_addr = QLineEdit('http://localhost:10086')
        self.lnt_addr.returnPressed.connect(self.load)
        self.toolbar.addWidget(self.lnt_addr)

    def _set_down_ui(self):
        down_frame = QFrame()
        self.down_layout = QHBoxLayout(down_frame)
        self.layout.addWidget(down_frame)

        self.webview = QWebEngineView()
        self.webview.urlChanged.connect(self.update_url)
        self.webview.loadFinished.connect(self.load_finish)
        self.action_back.triggered.connect(self.webview.back)
        self.action_forward.triggered.connect(self.webview.forward)
        self.action_stop.triggered.connect(self.webview.stop)
        self.action_reload.triggered.connect(self.webview.reload)
        self.down_layout.addWidget(self.webview)

    def load_finish(self):
        self.action_stop.setVisible(False)
        self.action_reload.setVisible(True)

    # def reload(self, event):
    #     try:
    #         self.webview.reload()
    #     except Exception as e:
    #         print(e)

    def load(self):
        try:
            url = str(self.lnt_addr.text())
            if '://' not in url:
                url = 'http://' + url
            url = QUrl(url)
            self.action_stop.setVisible(True)
            self.action_reload.setVisible(False)
            self.webview.load(url)
        except Exception as e:
            print(e)

    def update_url(self, q):
        self.lnt_addr.setText(q.toString())
        self.lnt_addr.setCursorPosition(0)


