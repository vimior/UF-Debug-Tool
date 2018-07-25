#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'vinman'

import struct
import serial
from serial import SerialException
from serial.tools import list_ports
import numpy as np
from PIL import Image
import threading
lock = threading.Lock()

FB_HDR_SIZE = 12

# USB Debug commands
USBDBG_CMD             = 48
USBDBG_FW_VERSION      = 0x80
USBDBG_FRAME_SIZE      = 0x81
USBDBG_FRAME_DUMP      = 0x82
USBDBG_ARCH_STR        = 0x83
USBDBG_SCRIPT_EXEC     = 0x05
USBDBG_SCRIPT_STOP     = 0x06
USBDBG_SCRIPT_SAVE     = 0x07
USBDBG_SCRIPT_RUNNING  = 0x87
USBDBG_TEMPLATE_SAVE   = 0x08
USBDBG_DESCRIPTOR_SAVE = 0x09
USBDBG_ATTR_READ       = 0x8A
USBDBG_ATTR_WRITE      = 0x0B
USBDBG_SYS_RESET       = 0x0C
USBDBG_FB_ENABLE       = 0x0D
USBDBG_TX_BUF_LEN      = 0x8E
USBDBG_TX_BUF          = 0x8F

ATTR_CONTRAST    = 0
ATTR_BRIGHTNESS  = 1
ATTR_SATURATION  = 2
ATTR_GAINCEILING = 3

BOOTLDR_START         = 0xABCD0001
BOOTLDR_RESET         = 0xABCD0002
BOOTLDR_ERASE         = 0xABCD0004
BOOTLDR_WRITE         = 0xABCD0008


def get_openmv_port():
    for port in list_ports.comports():
        if 'OpenMV Cam USB' in port.description:
            return port.device
    return None


def lock_func(func):
    def decorator(*args, **kwargs):
        with lock:
            result = func(*args, **kwargs)
        return result
    return decorator


class OpenMV(object):
    def __init__(self):
        super(OpenMV, self).__init__()
        self.init()

    def init(self):
        self._connected = False
        self._port = None
        self._serial = None
        self._running = False
        self._fb_size = (320, 240)
        self._fb_data = None
        self._fw_version = None
        self._enable_fb = True
        self._error = None
        self.timeout = 0.3

    @property
    def port(self):
        return self._port

    @property
    def connected(self):
        return self._connected

    @connected.setter
    def connected(self, state):
        self._connected = state

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, state):
        self._running = state

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        self._error = error

    @property
    def fw_version(self):
        if not self._fw_version:
            self.get_fw_version()
        return self._fw_version

    @property
    def enable_fb(self):
        return self._enable_fb

    @enable_fb.setter
    def enable_fb(self, enable):
        self.set_enable_fb(enable)

    @property
    def fb_size(self):
        return self._fb_size

    @property
    def fb_data(self):
        return self._fb_data

    @fb_data.setter
    def fb_data(self, data):
        self._fb_data = data

    @property
    def in_waiting(self):
        if self._serial:
            try:
                return self._serial.in_waiting
            except serial.SerialException:
                return False
        else:
            return False

    def connect(self):
        self._port = get_openmv_port()
        if self._port is not None:
            try:
                self._serial = serial.Serial(self._port, baudrate=921600, timeout=self.timeout)
                self._connected = True
                self._error = None
                self.get_fw_version()
                self.script_running()
                self.set_enable_fb(True)
            except Exception as e:
                self.init()
                self._error = str(e)
        else:
            self.init()
            self._error = 'No available OpenMV port'

    def disconnect(self):
        try:
            if self.connected:
                self._serial.close()
        except:
            pass
        finally:
            self.init()

    def set_timeout(self, timeout):
        try:
            if self.connected:
                self._serial.timeout = timeout
        except:
            pass

    def check_connection_status(self):
        if self.connected:
            try:
                self._serial.write(b'b')
                return True
            except SerialException as e:
                self._error = str(e)
                self.disconnect()
                return False
            except:
                return None

    def get_fb_size(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_FRAME_SIZE, FB_HDR_SIZE))
                return struct.unpack("III", self._serial.read(12))
            else:
                return None
        except:
            return None

    @lock_func
    def get_fb_data(self):
        try:
            size = self.get_fb_size()
            if size is None or len(size) < 3 or not size[0]:
                return None
            if size[2] > 2:
                num_bytes = size[2]
            else:
                num_bytes = size[0] * size[1] * size[2]

            self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_FRAME_DUMP, num_bytes))
            buff = self._serial.read(num_bytes)
            if size[2] == 1:  # Grayscale
                y = np.fromstring(buff, dtype=np.uint8)
                buff = np.column_stack((y, y, y))
            elif size[2] == 2:  # RGB565
                arr = np.fromstring(buff, dtype=np.uint16).newbyteorder('S')
                r = (((arr & 0xF800) >> 11) * 255.0 / 31.0).astype(np.uint8)
                g = (((arr & 0x07E0) >> 5) * 255.0 / 63.0).astype(np.uint8)
                b = (((arr & 0x001F) >> 0) * 255.0 / 31.0).astype(np.uint8)
                buff = np.column_stack((r, g, b))
            else:  # JPEG
                try:
                    buff = np.asarray(Image.frombuffer("RGB", size[0:2], buff, "jpeg", "RGB", ""))
                except Exception as e:
                    print("JPEG decode error (%s)"%(e))
                    return None

            if (buff.size != (size[0] * size[1] * 3)):
                return None

            self._fb_size = (size[0], size[1])
            return (size[0], size[1], buff.reshape((size[1], size[0], 3)))
        except Exception as e:
            print('>>>', e)
            return None

    @lock_func
    def exec_script(self, buf):
        try:
            if self.connected:
                self.set_enable_fb(True)
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_SCRIPT_EXEC, len(buf)))
                self._serial.write(buf)
                self._running = True
                return True
            else:
                return False
        except:
            return False

    def save_script(self, buf):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_SCRIPT_SAVE, len(buf)))
                self._serial.write(buf)
                return True
            else:
                return False
        except:
            return False

    @lock_func
    def stop_script(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_SCRIPT_STOP, 0))
                return True
            else:
                return False
        except:
            return False

    @lock_func
    def script_running(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_SCRIPT_RUNNING, 4))
                state = struct.unpack("I", self._serial.read(4))[0]
                if state == 1:
                    self._running = True
                else:
                    self._running = False
                return self.running
            else:
                return None
        except SerialException:
            return None
        except:
            return False

    def save_template(self, x, y, w, h, path):
        try:
            if self.connected:
                buf = struct.pack("IIII", x, y, w, h) + path
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_TEMPLATE_SAVE, len(buf)))
                self._serial.write(buf)
                return True
            else:
                return False
        except:
            return False

    def save_descriptor(self, x, y, w, h, path):
        try:
            if self.connected:
                buf = struct.pack("HHHH", x, y, w, h) + path
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_DESCRIPTOR_SAVE, len(buf)))
                self._serial.write(buf)
                return True
            else:
                return False
        except:
            return False

    def get_attr(self, attr):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBIh", USBDBG_CMD, USBDBG_ATTR_READ, 1, attr))
                return self._serial.read(1)
            else:
                return None
        except:
            return None

    def set_attr(self, attr, value):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBIhh", USBDBG_CMD, USBDBG_ATTR_WRITE, 0, attr, value))
                return True
            else:
                return False
        except:
            return False

    @lock_func
    def reset(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_SYS_RESET, 0))
                self.init()
                return True
            else:
                return False
        except:
            return False

    def bootloader_start(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<I", BOOTLDR_START))
                return struct.unpack("I", self._serial.read(4))[0] == BOOTLDR_START
            else:
                return False
        except:
            return False

    def bootloader_reset(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<I", BOOTLDR_RESET))
                return True
            else:
                return False
        except:
            return False

    def flash_erase(self, sector):
        try:
            if self.connected:
                self._serial.write(struct.pack("<II", BOOTLDR_ERASE, sector))
                return True
            else:
                return False
        except:
            return False

    def flash_write(self, buf):
        try:
            if self.connected:
                self._serial.write(struct.pack("<I", BOOTLDR_WRITE) + buf)
                return True
            else:
                return False
        except:
            return False

    @lock_func
    def get_output_data(self):
        buf_len = self.tx_buf_len()
        if buf_len:
            buf = self.tx_buf(buf_len)
            if buf and b'Type "help()" for more information.' in buf:
                self._running = False
            return buf
        else:
            return None

    def tx_buf_len(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_TX_BUF_LEN, 4))
                return struct.unpack("I", self._serial.read(4))[0]
            else:
                return None
        except:
            return None

    def tx_buf(self, bytes):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_TX_BUF, bytes))
                return self._serial.read(bytes)
            else:
                return None
        except:
            return None

    def get_fw_version(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_FW_VERSION, 12))
                self._fw_version = struct.unpack("III", self._serial.read(12))
                return self._fw_version
            else:
                return None
        except:
            return None

    def set_enable_fb(self, enable):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBIH", USBDBG_CMD, USBDBG_FB_ENABLE, 0, enable))
                self._enable_fb = enable
                return True
            else:
                return False
        except Exception as e:
            return False

    def arch_str(self):
        try:
            if self.connected:
                self._serial.write(struct.pack("<BBI", USBDBG_CMD, USBDBG_ARCH_STR, 64))
                return self._serial.read(64).split('\0', 1)[0]
            else:
                return None
        except:
            return None


