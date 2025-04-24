import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import sys
import time
import subprocess

class ImagenService(win32serviceutil.ServiceFramework):
    _svc_name_ = "OpenAIImageToCSV"
    _svc_display_name_ = "Image to CSV Converter with GPT-4o"
    _svc_description_ = "Processes images into CSV using OpenAI GPT-4o automatically."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        socket.setdefaulttimeout(60)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("OpenAIImageToCSV service started.")
        self.main()

    def main(self):
        while self.running:
            try:
                # Ejecuta tu script principal como subprocess (puedes cambiar a import si prefieres)
                subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "main.py")])
                time.sleep(10)
            except Exception as e:
                servicemanager.LogErrorMsg(f"Error: {str(e)}")
                time.sleep(10)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ImagenService)
