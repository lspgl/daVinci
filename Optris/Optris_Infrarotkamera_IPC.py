# schlro: 2017-01-02
# Optris, IPC dll communication test
#
# based on polling version in Optris SDK
#*\Optris GmbH\PI Connect\SDK\Samples C++\Start IPC2 Win32\
# basically all necessary program parts are intergated in: mainWin32.cpp
#
# V0.1:working one time communication with dll
#     additional read and closing to continiousely reading data using IPC communication
# V0.2: connection is established and cyclicly the target temperatures is checked and printed.
#     therefore, three timers are generatoed
#     toDo: check cyclicly for new frames, get the data and display them

import sys
try:
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QApplication
except ModuleNotFoundError:
    try:
        from PyQt4.QtCore import QTimer
        from PyQt4.QtGui import QApplication
    except ModuleNotFoundError:
        print("import error")

import time

from ctypes import *


class IRCAM_IPC(object):

    def __init__(self):
        self.OptrisDLL = WinDLL('dll\ImagerIPC2.dll')

        self.IPC_EVENT_INIT_COMPLETED = 0x0001
        self.IPC_EVENT_SERVER_STOPPED = 0x0002
        self.IPC_EVENT_CONFIG_CHANGED = 0x0004
        self.IPC_EVENT_FILE_CMD_READY = 0x0008
        self.IPC_EVENT_FRAME_INIT = 0x0010
        self.IPC_EVENT_VIS_FRAME_INIT = 0x0020

        self.ipcInitialized = False
        self.frameInitialized = False
        self.Connected = False

        self.Stopped = False
        self.frameInitialized = False
        self.State = 0

        self.hr = -1

        # setup QT enviourement with timers and its events
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

    def init(self):

        timerHandleEvents = QTimer()
        timerHandleEvents.timeout.connect(self.HandleEvents)
        timerHandleEvents.start(100)
        timerInitIPC = QTimer()
        timerInitIPC.timeout.connect(self.InitIPC)
        timerInitIPC.start(200)
        timerGetTempTarget = QTimer()
        timerGetTempTarget.timeout.connect(self.GetTempMeasureArea)
        timerGetTempTarget.start(1000)

        # run event loop so python doesn't exit
        self.app.exec_()

    def InitIPC(self):
        self.hr = -1
        if not self.ipcInitialized:
            self.hr = self.OptrisDLL.InitImagerIPC(0)
            if (self.hr < 0):
                self.ipcInitialized = False
                self.frameInitialized = False
            else:
                self.hr = self.OptrisDLL.RunImagerIPC(0)
                if (self.hr == 0):
                    self.ipcInitialized = True

    def OnInitCompleted(self):
        print("init completed")
        # ToDo: get colors:
        #Colors = (TIPCMode(GetIPCMode(0)) == ipcColors);
        self.Connected = True

    def ReleaseIPC(self):
        self.Connected = False
        if self.ipcInitialized:
            self.OptrisDLL.ReleaseImagerIPC(0)
            self.ipcInitialized = False

    def OnServerStopped(self, reason):
        self.ReleaseIPC()
        return 0

    def HandleEvents(self):
        if self.ipcInitialized:
            self.State = self.OptrisDLL.GetIPCState(0, True)
            #print("State = " + str(self.State))
            if(self.State & self.IPC_EVENT_SERVER_STOPPED):
                self.OnServerStopped(0)

            if not self.Connected and (self.State & self.IPC_EVENT_INIT_COMPLETED):
                self.OnInitCompleted()

            if self.Connected and (self.State & self.IPC_EVENT_FILE_CMD_READY):
                print("File Saved")
                # OnFileCommandReady
                # Parameters:
                # - path (wchar_t*) : The complete path to the file name of the stored file (Ravi or snapshot)
                # Return value:
                # - Success (HRESULT), 0 to signal success
                # This event notifies that a file was successfully stored.

                self.snapshot_filename = c_wchar_p(" " * 1000)
                # print(len(path.value))
                self.OptrisDLL.GetPathOfStoredFile.argtypes = [c_int, c_wchar_p, c_int]
                temp = self.OptrisDLL.GetPathOfStoredFile(
                    0, self.snapshot_filename, c_int(len(self.snapshot_filename.value)))
                if temp == 0:
                    print("Filename: " + str(self.snapshot_filename.value))

            if(self.State & self.IPC_EVENT_FRAME_INIT):
                FrameWidth = c_int(0)
                FrameHeight = c_int(0)
                FrameDepth = c_int(0)
                self.OptrisDLL.GetFrameConfig.argtypes = [c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
                result = self.OptrisDLL.GetFrameConfig(0, byref(FrameWidth), byref(FrameHeight), byref(FrameDepth))
                if result == 0:
                    print("communication succeeded: " + str(FrameWidth) +
                          "x" + str(FrameHeight) + "x" + str(FrameDepth))
                    # initialise buffer for picture data

    def GetTempMeasureArea(self):
        if self.Connected:
            for i in range(self.OptrisDLL.GetMeasureAreaCount(0) - 1):
                # print(self.OptrisDLL.GetMeasureAreaCount(0)) #liefert (anzahl der areas + 1) zurueck
                t = str(self.OptrisDLL.GetTempMeasureArea(0, i))
                #print(float(self.OptrisDLL.GetTempMeasureArea(0, 2)))
                value = str(t)[1:]
                value = float(value) / 10
                print("TargetNumber: " + str(i + 1) + " TempTarget: " + str(value))
            self.FileSnapshot()

    def FileSnapshot(self):
        if self.Connected:
            self.OptrisDLL.FileSnapshot(0)


if __name__ == '__main__':
    icp = IRCAM_IPC()
    icp.init()

    while 1:
        pass
