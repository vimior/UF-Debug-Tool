# !/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2018, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

import sys
from PyQt5.Qt import QApplication, QWidget
from ui import UFDebugToolUI
from log import logger, LogWindow


class UFDebugTool(QWidget):
    def __init__(self):
        super(UFDebugTool, self).__init__()
        self.ui = UFDebugToolUI(self)
        self.log_window = LogWindow(self)
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
    # icon = QIcon()
    # icon.addPixmap(QPixmap(os.path.join(icon_path, 'main.png')), QIcon.Normal, QIcon.Off)
    # controller.setWindowIcon(icon)
    controller.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
