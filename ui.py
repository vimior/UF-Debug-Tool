# !/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>


from PyQt5.Qt import QTabWidget, QWidget, QMenuBar, QAction, QToolBox, QGroupBox
from PyQt5.Qt import QHBoxLayout, QVBoxLayout, QFileDialog
from openmv.openmv_ui import OpenMV_UI
from xArm.xarm_ui import XArmUI
from uArm.uarm_ui import UArmUI
from gcode.gcode_ui import GcodeUI
from webview.webview_ui import WebViewUI


class UFDebugToolUI(object):
    def __init__(self, window=None):
        self.window = window if window is not None else QWidget
        super(UFDebugToolUI, self).__init__()
        self.lang = 'en'
        self.set_ui()

    def set_ui(self):
        self._set_window()
        self._set_menubar()
        self._set_tab()

    def _set_window(self):
        self.window.setWindowTitle(self.window.tr('UF-Debug-Tool'))
        self.window.setMinimumHeight(800)
        self.window.setMinimumWidth(1080)
        self.main_layout = QVBoxLayout(self.window)

    def _set_menubar(self):
        self.menuBar = QMenuBar()
        self.main_layout.setMenuBar(self.menuBar)

        fileMenu = self.menuBar.addMenu('File')
        self.newFileAction = QAction(self.window.tr('New'), self.window)
        self.newFileAction.setShortcut('Ctrl+N')
        self.newFileAction.setStatusTip('New File')
        fileMenu.addAction(self.newFileAction)

        self.openFileAction = QAction(self.window.tr('Open'), self.window)
        self.openFileAction.setShortcut('Ctrl+O')
        self.openFileAction.setToolTip('Open File')
        fileMenu.addAction(self.openFileAction)

        self.saveFileAction = QAction(self.window.tr('Save'), self.window)
        self.saveFileAction.setShortcut('Ctrl+S')
        self.saveFileAction.setStatusTip('Save File')
        fileMenu.addAction(self.saveFileAction)

        self.closeFileAction = QAction(self.window.tr('Close'), self.window)
        self.closeFileAction.setShortcut('Ctrl+W')
        self.closeFileAction.setStatusTip('Close File')
        fileMenu.addAction(self.closeFileAction)

        self.newFileAction.triggered.connect(self.new_dialog)
        self.openFileAction.triggered.connect(self.open_dialog)
        self.saveFileAction.triggered.connect(self.save_dialog)
        self.closeFileAction.triggered.connect(self.close_dialog)

        debugMenu = self.menuBar.addMenu('Debug')
        self.logAction = QAction(self.window.tr('Log'), self.window)
        self.logAction.setShortcut('Ctrl+D')
        self.logAction.setStatusTip('Open-Log')
        self.logAction.triggered.connect(self.control_log_window)
        debugMenu.addAction(self.logAction)

    def control_log_window(self):
        if self.window.log_window.isHidden():
            self.window.log_window.show()
            self.logAction.setText('Close-Log')
        else:
            self.window.log_window.hide()
            self.logAction.setText('Open-Log')

    def switch_tab(self, index):
        pass
        # if index == 2:
        #     self.menuBar.setHidden(False)
        # else:
        #     self.menuBar.setHidden(True)

    def _set_tab(self):
        self.tab_widget = QTabWidget()
        # self.tab_widget.currentChanged.connect(self.switch_tab)
        # tab_widget.setMaximumHeight(self.window.geometry().height() // 2)
        self.main_layout.addWidget(self.tab_widget)

        toolbox1 = QToolBox()
        toolbox2 = QToolBox()
        toolbox3 = QToolBox()
        toolbox4 = QToolBox()
        toolbox5 = QToolBox()

        groupbox1 = QGroupBox()
        groupbox2 = QGroupBox()
        groupbox3 = QGroupBox()
        groupbox4 = QGroupBox()
        groupbox5 = QGroupBox()

        toolbox1.addItem(groupbox1, "")
        toolbox2.addItem(groupbox2, "")
        toolbox3.addItem(groupbox3, "")
        toolbox4.addItem(groupbox4, "")
        toolbox5.addItem(groupbox5, "")

        self.tab_widget.addTab(toolbox1, "uArm")
        self.tab_widget.addTab(toolbox2, "xArm")
        self.tab_widget.addTab(toolbox3, "OpenMV")
        self.tab_widget.addTab(toolbox4, "Gcode")
        self.tab_widget.addTab(toolbox5, "WebView")

        uarm_layout = QVBoxLayout(groupbox1)
        xarm_layout = QVBoxLayout(groupbox2)
        openmv_layout = QHBoxLayout(groupbox3)
        gcode_layout = QVBoxLayout(groupbox4)
        webview_layout = QVBoxLayout(groupbox5)

        self.uarm_ui = UArmUI(self, uarm_layout)
        self.xarm_ui = XArmUI(self, xarm_layout)
        self.openmv_ui = OpenMV_UI(self, openmv_layout)
        self.gcode_ui = GcodeUI(self, gcode_layout)
        self.webview_ui = WebViewUI(self, webview_layout)
        self.tab_widget.setCurrentIndex(0)

    def new_dialog(self):
        self.openmv_ui.textEdit.setText('')
        self.openmv_ui.textEdit.filename = None
        self.openmv_ui.label_title.setText('untitled')
        self.tab_widget.setCurrentIndex(2)
        self.openmv_ui.textEdit.setDisabled(False)

    def open_dialog(self):
        fname = QFileDialog.getOpenFileName(self.window, 'Open file', '')
        if fname and fname[0]:
            with open(fname[0], "r") as f:
                self.openmv_ui.textEdit.setText(f.read())
                self.openmv_ui.label_title.setText(fname[0])
                self.openmv_ui.textEdit.filename = fname[0]
        self.tab_widget.setCurrentIndex(2)
        self.openmv_ui.textEdit.setDisabled(False)

    def save_dialog(self):
        widget = self.window.focusWidget()
        if widget:
            if not self.openmv_ui.textEdit.filename:
                fname = QFileDialog.getSaveFileName(self.window, 'Save File', '')
                if fname and fname[0]:
                    self.openmv_ui.textEdit.filename = fname[0]
            if self.openmv_ui.textEdit.filename:
                data = widget.toPlainText()
                with open(self.openmv_ui.textEdit.filename, "w") as f:
                    f.write(data)

    def close_dialog(self):
        self.openmv_ui.textEdit.clear()
        self.openmv_ui.textEdit.filename = None
        self.openmv_ui.label_title.setText('')
        self.openmv_ui.textEdit.setDisabled(True)

