import tkinter as tk
import os
from pet_organ.animation import play_animation, increase_size, decrease_size, toggle_back_mode
from pet_organ.eat import feed
from pet_organ.aichat import open_chat_window

def open_weather(root, label):
    os.startfile("weather.lnk")
    play_animation('hat', root, label)
def open_win(root, label):
    os.startfile("win.exe")
    play_animation('wave', root, label)

def open_webspeed(root, label):
    os.startfile("网速.exe")
    play_animation('wave', root, label)
def open_note(root, label):
    os.startfile("note.txt")
    play_animation('wave', root, label)
def open_video(root, label):
    os.startfile("OCT视频播放器.html")
    play_animation('hat', root, label)
def open_home(root, label):
    os.startfile("home.lnk")
    play_animation('circle', root, label)
def show_menu(root, label, event):
    menu = tk.Menu(root, tearoff=0, bg='white')  # 创建一个菜单对象
    function_menu = tk.Menu(root, tearoff=0)  # 创建一个功能菜单对象
    menu.add_command(label='招手', command=lambda: play_animation('wave', root, label))  # 向菜单中添加命令
    menu.add_command(label='转一圈儿', command=lambda: play_animation('circle', root, label))  # 向菜单中添加命令
    menu.add_command(label='脱帽', command=lambda: play_animation('hat', root, label))  # 向菜单中添加命令
    menu.add_command(label='变大', command=lambda: increase_size(root, label))
    menu.add_command(label='变小', command=lambda: decrease_size(root, label))
    menu.add_command(label='回头', command=lambda: toggle_back_mode())  # 新增回头选项
    menu.add_command(label='今天天气如何？', command=open_weather)
    menu.add_command(label='聊会天吗', command=lambda: open_chat_window(root))
    menu.add_command(label='投喂', command=lambda: feed(root))
    menu.add_command(label='去地灵殿坐坐', command=lambda: open_home(root, label))
    menu.add_command(label='看看清单', command=lambda: open_note(root, label))  # 向菜单中添加命令
    menu.add_cascade(label='其他功能', menu=function_menu)  # 向菜单中添加子菜单命令
    function_menu.add_command(label='打开OCT视频播放器', command=lambda: open_video(root, label))  # 向菜单中添加命令
    function_menu.add_command(label='打开副屏控制台', command=lambda: open_win(root, label))
    function_menu.add_command(label='打开网速监察', command=lambda: open_webspeed(root, label))
    menu.add_separator()  # 向菜单中添加分隔符
    menu.add_command(label='再见', command=root.destroy)  # 向菜单中添加命令
    menu.post(event.x_root, event.y_root)
