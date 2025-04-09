import tkinter as tk
import os
import configparser
from tkinter import ttk
import threading
import sys

hunger_lock = threading.Lock()  # 添加全局锁
pause_decrease = False
decrease_job_id = None

# 全局变量
max_hunger = None
hunger = None

def load_hunger():
    global hunger, max_hunger  # 声明为全局变量
    config = configparser.ConfigParser()
    file_path = 'food_config.ini'
    print(f"尝试读取配置文件: {os.path.abspath(file_path)}")
    config.read(file_path)
    if config.has_section('Game'):
        try:
            with hunger_lock:
                hunger = int(config.get('Game', 'hunger'))
                max_hunger = int(config.get('Game', 'max_hunger'))
                print(f"成功加载饥饿值: {hunger}，最大饥饿值: {max_hunger}")
        except ValueError:
            print("配置错误: 'hunger' 或 'max_hunger' 值无效")
    else:
        print("配置缺少 'Game' 部分")
    return hunger, max_hunger

# 加载饥饿值和最大饥饿值
hunger, max_hunger = load_hunger()

def get_hunger():
    global hunger
    return hunger

def get_max_hunger():
    global max_hunger
    return max_hunger

def set_hunger(value):
    global hunger
    with hunger_lock:
        hunger = min(get_max_hunger(), max(0, value))  # 保证在合法范围内
        save_hunger()

# 投喂功能，添加进度条和标签
from eat import decrease_job_id  # 在 pet.py 中引用时也要确保能访问这个变量

progress = None
feed_lable = None
feed_window = None

def feed(root):
    global feed_window, progress, feed_lable
    print(f"进入 feed 函数，当前饥饿值: {get_hunger()}")

    # 暂停减少逻辑
    try:
        if decrease_job_id is not None:
            root.after_cancel(decrease_job_id)
            print("定时器已取消")
    except Exception as e:
        print(f"取消定时器出错: {e}")

    # 5 秒后恢复定时器
    def resume_decrease():
        decrease_hunger(root)

    root.after(5000, resume_decrease)
    if hunger is None:
        print("未从配置文件中获取到饥饿值，请检查配置文件。")
        return
    feed_window = tk.Toplevel(root)
    feed_window.overrideredirect(True)  # 去掉窗口的标题栏和边框
    feed_window.title('投喂')
    feed_window.geometry('900x600')

    # 定义拖动窗口的函数
    def start_drag(event):
        feed_window._drag_start_x = event.x
        feed_window._drag_start_y = event.y

    def drag(event):
        x = feed_window.winfo_x() - feed_window._drag_start_x + event.x
        y = feed_window.winfo_y() - feed_window._drag_start_y + event.y
        feed_window.geometry(f"+{x}+{y}")

    # 绑定拖动事件
    feed_window.bind("<ButtonPress-1>", start_drag)
    feed_window.bind("<B1-Motion>", drag)

    # 添加标签
    feed_lable = tk.Label(feed_window, text=f'{hunger}/{get_max_hunger()}')
    feed_lable.pack()
    # 添加进度条
    progress = ttk.Progressbar(feed_window, length=get_max_hunger(), mode='determinate', maximum=get_max_hunger())
    progress.pack(pady=10)
    # 添加食物图片和点击事件
    foods = {
        '汉堡': {'image': 'food/1.png', 'value': 1},
        '炸鸡': {'image': 'food/2.png', 'value': 2},
        '面条': {'image': 'food/3.png', 'value': 30},
        '鱼饼': {'image': 'food/1.png', 'value': 30},
        '三明治': {'image': 'food/2.png', 'value': 30},
        '烤八目鳗': {'image': 'food/3.png', 'value': 30},
    }
    # 创建两个Frame，一个用于放置上排的按钮，一个用于放置下排的按钮
    frame1 = tk.Frame(feed_window)
    frame1.pack()
    frame2 = tk.Frame(feed_window)
    frame2.pack()
    for i, (name, food) in enumerate(foods.items()):
        photo = tk.PhotoImage(file=food['image'])
        button = tk.Button(frame1 if i < 3 else frame2,
                           image=photo, command=lambda
                           value=food['value']: add_hunger(value, progress, feed_lable))
        button.image = photo
        button.pack(side='left', padx=50 if i > 0 else 0)
    # 添加隐藏窗口的按钮
    hide_button = tk.Button(feed_window, text='隐藏窗口', command=feed_window.withdraw)
    hide_button.pack()
    # 在窗口被销毁时保存hunger值
    feed_window.protocol("WM_DELETE_WINDOW", lambda: [save_hunger(), feed_window.destroy()])
    # 在投喂窗口中调用update_hunger函数
    update_hunger()

# 修改增加饥饿值的函数，更新进度条和标签，并保存饥饿值
def add_hunger(value, progress, feed_lable):
    old_hunger = get_hunger()
    new_hunger = min(get_max_hunger(), old_hunger + value)
    set_hunger(new_hunger)
    # 更新UI
    if progress:
        progress['value'] = new_hunger
    if feed_lable:
        feed_lable['text'] = f'{new_hunger}/{get_max_hunger()}'
    print(f"投喂生效: {old_hunger} -> {new_hunger}")

# 添加每分钟减少饥饿值的函数，并保存饥饿值
def decrease_hunger(root):
    global decrease_job_id
    if decrease_job_id is not None:
        try:
            root.after_cancel(decrease_job_id)
        except:
            pass

    old_hunger = get_hunger()
    if old_hunger is not None and old_hunger > 0:
        set_hunger(old_hunger - 1)
        if progress and progress.winfo_exists():
            progress['value'] = get_hunger()
        if feed_lable:
            feed_lable['text'] = f'{get_hunger()}/{get_max_hunger()}'

    decrease_job_id = root.after(1000, decrease_hunger, root)

def update_hunger():
    global hunger, feed_window, progress, feed_lable
    # 检查投喂窗口是否存在
    if feed_window is not None and feed_window.winfo_exists():
        # 更新进度条和标签
        if progress is not None and progress.winfo_exists() and hunger is not None:
            progress['value'] = hunger
        if feed_lable is not None and hunger is not None:
            feed_lable['text'] = f'{hunger}/{get_max_hunger()}'
    if 'root' in globals():
        root.after(5000, update_hunger)  # 每5秒更新一次

# 保存饥饿值到配置文件
def save_hunger():
    global hunger, max_hunger
    if hunger is not None and max_hunger is not None:
        # 创建一个配置文件对象
        config = configparser.ConfigParser()
        # 在配置文件中添加一个section
        config.add_section('Game')
        # 在这个section中添加键值对
        config.set('Game', 'hunger', str(hunger))
        config.set('Game', 'max_hunger', str(max_hunger))
        # 将配置文件写入到磁盘
        file_path = 'food_config.ini'
        try:
            with open(file_path, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"保存饥饿值时出现错误: {e}")
    else:
        print("饥饿值或最大饥饿值为 None，无法保存。")
