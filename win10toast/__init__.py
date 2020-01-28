__all__ = ['ToastNotifier']

# standard library
import logging
from os import path, remove
from time import sleep
from threading import Thread
from pkg_resources import Requirement
from pkg_resources import resource_filename
from time import sleep

# 3rd party modules
from win32api import GetModuleHandle
from win32api import PostQuitMessage
from win32gui import CreateWindow
from win32gui import DestroyWindow
from win32gui import LoadIcon
from win32gui import LoadImage
from win32gui import RegisterClass
from win32gui import UnregisterClass
from win32gui import Shell_NotifyIcon
from win32gui import UpdateWindow
from win32gui import WNDCLASS
from win32gui import PumpMessages

try:
    from PIL import Image
except ImportError:
    Image = None


# Constants

CW_USEDEFAULT   = -0x80000000
IDI_APPLICATION = 0x7f00
IMAGE_ICON      = 0x1
LR_LOADFROMFILE = 0x16
LR_DEFAULTSIZE  = 0x40
NIM_ADD         = 0x0
NIM_MODIFY      = 0x1
NIM_DELETE      = 0x2
NIF_MESSAGE     = 0x1
NIF_ICON        = 0x2
NIF_TIP         = 0x4
NIF_INFO        = 0x10
WM_USER         = 0x400
WS_OVERLAPPED   = 0x0
WS_SYSMENU      = 0x80000
PARAM_DESTROY   = 0x404
PARAM_CLICKED   = 0x405



# Class

class ToastNotifier(object):
    '''Create a Windows 10 toast notification.

    from: https://github.com/nuno-andre/Windows-10-Toast-Notifications
    '''

    def __init__(self):
        self._thread = None

    @staticmethod
    def _decorator(func, callback=None):
        '''

        :param func:     callable to decorate
        :param callback: callable to run on mouse click within notification window
        :return:         callable
        '''
        def inner(*args, **kwargs):
            kwargs.update({'callback': callback})
            func(*args, **kwargs)
        return inner

    def _show_toast(
        self, title, msg, icon_path, duration, callback_on_click
    ):
        '''Notification settings.

        :param title:     notification title
        :param msg:       notification message
        :param icon_path: path to the .ico file to custom notification
        :para mduration:  delay in seconds before notification self-destruction, None for no-self-destruction
        '''

        # Register the window class.
        self.wc = WNDCLASS()
        self.hinst = self.wc.hInstance = GetModuleHandle(None)
        # must be a string
        self.wc.lpszClassName = 'PythonTaskbar'
        # could instead specify simple mapping
        self.wc.lpfnWndProc = self._decorator(self.wnd_proc, callback_on_click)
        try:
            self.classAtom = RegisterClass(self.wc)
        except Exception as e:
            logging.error('Some trouble with classAtom (%s)', e)
        style = WS_OVERLAPPED | WS_SYSMENU
        self.hwnd = CreateWindow(
            self.classAtom, 'Taskbar', style, 0, 0, CW_USEDEFAULT, CW_USEDEFAULT, 0, 0, self.hinst, None
        )
        UpdateWindow(self.hwnd)

        # icon
        if icon_path is not None:
            icon_path = path.realpath(icon_path)
            converted = False
            if Image is not None and icon_path.split('.')[-1] != '.ico':
                img = Image.open(icon_path)
                new_name = icon_path.split('.')[:-1] + '.ico'
                img.save(new_name)
                icon_path = new_name
                converted = True
        else:
            icon_path =  resource_filename(Requirement.parse('win10toast'), 'win10toast/data/python.ico')
            converted = False
        icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
        try:
            hicon = LoadImage(self.hinst, icon_path, IMAGE_ICON, 0, 0, icon_flags)
            if path.exists(new_name and converted):
                remove(new_name)
        except Exception as e:
            logging.error('Some trouble with the icon (%s): %s', icon_path, e)
            hicon = LoadIcon(0, IDI_APPLICATION)

        # Taskbar icon
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = self.hwnd, 0, flags, WM_USER + 20, hicon, 'Tooltip'
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(
            NIM_MODIFY,
            (self.hwnd, 0, NIF_INFO, WM_USER + 20, hicon, 'Balloon Tooltip', msg, 200, title)
        )
        PumpMessages()
        # take a rest then destroy
        if duration is not None:
            sleep(duration)
            DestroyWindow(self.hwnd)
            UnregisterClass(self.wc.lpszClassName, None)
        return None

    def show_toast(
            self, title='Notification', msg='Here comes the message',
            icon_path=None, duration=5, threaded=False, callback_on_click=None
        ):
        '''Notification settings.

        :param title:     notification title
        :param msg:       notification message
        :param icon_path: path to the .ico file to custom notification
        :para mduration:  delay in seconds before notification self-destruction, None for no-self-destruction
        '''
        args = title, msg, icon_path, duration, callback_on_click

        if not threaded:
            self._show_toast(*args)
        else:
            if self.notification_active():
                # We have an active notification, let is finish so we don't spam them
                return False

            self._thread = Thread(target=self._show_toast, args=args)
            self._thread.start()
        return True

    def notification_active(self):
        '''See if we have an active notification showing'''
        if self._thread is not None and self._thread.is_alive():
            # We have an active notification, let is finish we don't spam them
            return True
        return False

    def wnd_proc(self, hwnd, msg, wparam, lparam, **kwargs):
        '''Messages handler method'''
        if lparam == PARAM_CLICKED:
            # callback goes here
            if kwargs.get('callback'):
                kwargs.pop('callback')()
            self.on_destroy(hwnd, msg, wparam, lparam)
        elif lparam == PARAM_DESTROY:
            self.on_destroy(hwnd, msg, wparam, lparam)

    def on_destroy(self, hwnd, msg, wparam, lparam):
        '''Clean after notification ended.'''
        nid = self.hwnd, 0
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)

        return None
