from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QWidget, QSpacerItem, QSizePolicy, QPushButton
from PyQt5.QtCore import QTimer, Qt, QMimeData, QPoint
from PyQt5.QtGui import QColor, QPainter, QPalette, QDrag
import psutil
from pynvml import *
import os

def get_system_info():
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    gpu_load = nvmlDeviceGetUtilizationRates(handle).gpu
    gpu_temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
    nvmlShutdown()

    cpu_load = psutil.cpu_percent()
    return f"CPU负载: {cpu_load}% GPU负载: {gpu_load}% 温度: {gpu_temp}C"
def open_web():
    os.startfile("浏览器.lnk")
def open_pet():
    os.startfile("pet.lnk")
def close_pet():
    os.system("taskkill /IM pet.exe /F")
def open_social_apps():
    os.startfile("qq.lnk")
    os.startfile("微信.lnk")

class DraggableButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(DraggableButton, self).__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.moved = False

    """def mousePressEvent(self, event):
        self.moved = False
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(DraggableButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos
            self.moved = True

        super(DraggableButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if not self.moved:
            super(DraggableButton, self).mouseReleaseEvent(event)"""

app = QApplication([])
window = QWidget()
window.setStyleSheet("background-color: rgba(135,206,235,0.5);")
window.setWindowOpacity(0.8)
layout = QGridLayout()

info_label = QLabel()
info_label.setStyleSheet("""
    background-color: rgba(135,206,235,0.5);
    border-radius: 10px;
    color: white;
    font-size: 30px;
    font-weight: bold;
""")
info_label.setAlignment(Qt.AlignCenter)
info_label.setMinimumHeight(round(info_label.height() * 0.3))
layout.addWidget(info_label, 0, 0, 1, 2)
battonsize = 350

button1 = DraggableButton("打开桌宠")
button1.setStyleSheet("""
    background-color: rgba(135,206,235,0.5);
    border-radius: 10px;
    color: white;
    font-size: 30px;
    font-weight: bold;
""")
button1.setMinimumSize(battonsize, battonsize)
button1.setMaximumSize(battonsize, battonsize)
button1.clicked.connect(open_pet)
layout.addWidget(button1, 1, 0)

button3 = DraggableButton("关闭桌宠")
button3.setStyleSheet("""
    background-color: rgba(135,206,235,0.5);
    border-radius: 10px;
    color: white;
    font-size: 30px;
    font-weight: bold;
""")
button3.setMinimumSize(battonsize, battonsize)
button3.setMaximumSize(battonsize, battonsize)
button3.clicked.connect(close_pet)
layout.addWidget(button3, 1, 1)

button2 = DraggableButton("打开社交软件")
button2.setStyleSheet("""
    background-color: rgba(135,206,235,0.5);
    border-radius: 10px;
    color: white;
    font-size: 30px;
    font-weight: bold;
""")
button2.setMinimumSize(battonsize, battonsize)
button2.setMaximumSize(battonsize, battonsize)
button2.clicked.connect(open_social_apps)
layout.addWidget(button2, 1, 3)

button4 = DraggableButton("打开浏览器")
button4.setStyleSheet("""
    background-color: rgba(135,206,235,0.5);
    border-radius: 10px;
    color: white;
    font-size: 30px;
    font-weight: bold;
""")
button4.setMinimumSize(battonsize, battonsize)
button4.setMaximumSize(battonsize, battonsize)
button4.clicked.connect(open_web)
layout.addWidget(button4, 2, 1)

window.setLayout(layout)

def update_info_label():
    info_label.setText(get_system_info())
    QTimer.singleShot(5000, update_info_label)
update_info_label()
window.show()
app.exec_()
