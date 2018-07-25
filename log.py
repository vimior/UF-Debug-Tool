# !/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import queue
from PyQt5.Qt import QWidget, QTextEdit, QVBoxLayout, QTextCursor, QGridLayout, QFrame, QPushButton
from PyQt5.QtCore import QObject, pyqtSignal, QThread

log_que = queue.Queue()


class Logger(object):
    def __init__(self):
        super(Logger, self).__init__()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'logger'):
            cls.logger = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls.logger

    @staticmethod
    def __generate_log_text(*args):
        msg = ''
        for i in args:
            msg += ' {}'.format(i)
        # if not msg.strip():
        #     return
        return msg

    def _log(self, *args, color='black', level=''):
        text = self.__generate_log_text(*args)
        if text:
            if level:
                text = '[{}] {}'.format(level, text)
            log_que.put({
                'color': color,
                'text': text
            })

    def log(self, *args):
        self._log(*args, color='black')

    def debug(self, *args):
        self._log(*args, color='#999999', level='DEBUG')

    def info(self, *args):
        self._log(*args, color='#0000FF', level='INFO')

    def warn(self, *args):
        self._log(*args, color='#FF9900', level='WARN')

    def warning(self, *args):
        self._log(*args, color='#FF9900', level='WARNING')

    def error(self, *args):
        self._log(*args, color='#FF0000', level='ERROR')

    def critical(self, *args):
        self._log(*args, color='#CC0000', level='CRITICAL')

    def stdout(self, text):
        self._log(text, color='black', level='STDOUT')

    def stderr(self, text):
        self._log(text, color='#FF0000', level='STDERR')

logger = Logger()


class OutputStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(text)


class LogThread(QThread):
    signal = pyqtSignal(dict)

    def __init__(self):
        super(LogThread, self).__init__()

    def run(self):
        while True:
            try:
                item = log_que.get()
                self.signal.emit(item)
            except Exception as e:
                print(e)


class LogWindow(QWidget):
    def __init__(self, window):
        super(LogWindow, self).__init__()
        self.main_window = window
        self.set_ui()
        # sys.stdout = OutputStream(textWritten=logger.stdout)
        # sys.stderr = OutputStream(textWritten=logger.stderr)
        self.log_thread = LogThread()
        self.log_thread.signal.connect(self.append_log)
        self.log_thread.start()

    def set_ui(self):
        self._set_window()
        self._set_log_ui()
        # self.move((self.main_window.geometry().x() + self.main_window.geometry().width()) * 1.05,
        #           self.main_window.geometry().y())

    def _set_window(self):
        self.setWindowTitle(self.tr('DebugLog'))
        self.setMinimumHeight(self.main_window.geometry().height())
        self.setMinimumWidth(self.main_window.geometry().width() / 3 * 2)
        self.main_layout = QVBoxLayout(self)

    def _set_log_ui(self):
        log_frame = QFrame()
        log_layout = QGridLayout(log_frame)
        self.main_layout.addWidget(log_frame)

        self.textedit_log = QTextEdit()
        self.textedit_log.setAcceptDrops(False)
        # self.textedit_log.setEnabled(False)
        log_layout.addWidget(self.textedit_log)
        btn_clear_log = QPushButton('ClearLog')
        btn_clear_log.clicked.connect(self.clear_log)
        log_layout.addWidget(btn_clear_log)

    def append_log(self, item):
        try:
            msg = '<p style="color:{};">{}</p>'.format(item.get('color', 'black'), item['text'])
            self.textedit_log.insertHtml(msg)
            self.textedit_log.insertPlainText('\r\n')
            self.textedit_log.moveCursor(QTextCursor.End)
        except Exception as e:
            pass
            # print(e)

    def clear_log(self):
        try:
            self.textedit_log.setText('')
        except Exception as e:
            pass
            # print(e)

    def closeEvent(self, event):
        self.main_window.ui.logAction.setText('Open-Log')
        super(LogWindow, self).closeEvent(event)
