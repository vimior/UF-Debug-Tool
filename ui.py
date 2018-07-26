# !/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>


from PyQt5.Qt import QTabWidget, QWidget, QFrame, QMenuBar, QAction, QToolBox, QGroupBox
from PyQt5.Qt import QHBoxLayout, QVBoxLayout, QGridLayout, QFileDialog
from openmv.openmv_ui import OpenMV_UI
from xArm.xarm_ui import XArmUI
from uArm.uarm_ui import UArmUI
from gcode.gcode_ui import GcodeUI


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
        self.window.setMinimumWidth(1000)
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

        toolBox1 = QToolBox()
        toolBox2 = QToolBox()
        toolBox3 = QToolBox()
        toolBox4 = QToolBox()
        # toolBox5 = QToolBox()

        groupBox1 = QGroupBox()
        groupBox2 = QGroupBox()
        groupBox3 = QGroupBox()
        groupBox4 = QGroupBox()
        # groupBox5 = QGroupBox()

        toolBox1.addItem(groupBox1, "")
        toolBox2.addItem(groupBox2, "")
        toolBox3.addItem(groupBox3, "")
        toolBox4.addItem(groupBox4, "")
        # toolBox5.addItem(groupBox5, "")

        self.tab_widget.addTab(toolBox1, "uArm")
        self.tab_widget.addTab(toolBox2, "xArm")
        self.tab_widget.addTab(toolBox3, "OpenMV")
        self.tab_widget.addTab(toolBox4, "Gcode")
        # tab_widget.addTab(toolBox5, "Tab-5")

        uarm_layout = QVBoxLayout(groupBox1)
        xarm_layout = QVBoxLayout(groupBox2)
        openmv_layout = QHBoxLayout(groupBox3)
        gcode_layout = QVBoxLayout(groupBox4)
        # print(self.tab_widget.currentWidget())

        self.uarm_ui = UArmUI(self, uarm_layout)
        self.xarm_ui = XArmUI(self, xarm_layout)
        self.openmv_ui = OpenMV_UI(self, openmv_layout)
        self.gcode_ui = GcodeUI(self, gcode_layout)
        self.tab_widget.setCurrentIndex(3)

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

