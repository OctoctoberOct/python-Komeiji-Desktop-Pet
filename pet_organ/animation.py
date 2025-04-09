import tkinter as tk
from itertools import cycle
from PIL import Image, ImageTk
import random

# 图片文件列表
idle_photos = ['animation/idle1.gif', 'animation/idle2.gif', 'animation/idle3.gif']  # 待机动画图片列表
idle_photo_cycle = cycle(idle_photos)  # 创建一个循环迭代器

animation_photos = {
    'wave': ['animation/wave1.gif', 'animation/wave2.gif', 'animation/wave3.gif', 'animation/wave1.gif',
             'animation/wave2.gif', 'animation/wave3.gif'],  # 右键单击动画图片列表
    'push': ['animation/push.gif'],  # 拖动窗口动画图片列表
    'hat': ['animation/hat1.gif', 'animation/hat2.gif', 'animation/hat3.gif'],  # “hat”动画图片列表
    'circle': ['animation/circle (1).gif', 'animation/circle (2).gif', 'animation/circle (3).gif',
               'animation/circle (4).gif', 'animation/circle (5).gif', 'animation/circle (6).gif',
               'animation/circle (7).gif', 'animation/circle (8).gif', 'animation/circle (9).gif']
}
animation_photo_cycles = {name: cycle(photos) for name, photos in animation_photos.items()}
animation = ['wave', 'hat', 'circle']

# 添加一个字典来存储每个动画的切换速度（以毫秒为单位）
animation_speeds = {
    'wave': 300,
    'push': 200,
    'hat': 200,
    'circle': 200,
}
play_idle = True  # 添加一个布尔变量来控制是否播放待机动画
current_animation = None  # 用于追踪当前播放的动画名称
# 图像的初始大小
image_size = 300
# 新增：控制是否回头（图像翻转）的变量
is_back = False


def increase_size(root, label):
    global image_size
    image_size += 50  # 增大尺寸
    change_image(label)  # 调用更新动画函数，重置待机动画


def decrease_size(root, label):
    global image_size
    image_size = max(50, image_size - 50)  # 防止尺寸过小
    change_image(label)  # 调用更新动画函数，重置待机动画


def change_image(label):
    global photo, play_idle, current_animation
    if play_idle and current_animation is None:  # 确保当前没有其他动画在播放
        img = Image.open(next(idle_photo_cycle))  # 获取下一帧图片
        img = process_image(img)  # 处理图像（可能翻转）
        photo = ImageTk.PhotoImage(img)  # 转换为 Tkinter 格式
        label.config(image=photo)  # 更新显示

    # 动态调整播放速度
    base_speed = 300  # 基础速度（毫秒）
    speed_factor = max(1, image_size / 300)  # 根据图像大小动态调整因子
    adjusted_speed = int(base_speed * speed_factor)  # 计算调整后的速度
    if play_idle and current_animation is None:  # 双重检查状态
        label.after(adjusted_speed, change_image, label)  # 调用下一帧


def play_loot_animation(root, label):
    d = random.choice(animation)
    play_animation(d, root, label)
    root.after(20000, play_loot_animation, root, label)


def play_animation(name, root, label, count=0):
    global photo, play_idle, current_animation
    if current_animation is not None and current_animation != name:
        return  # 如果有其他动画正在播放，就直接返回
    if count == 0:
        play_idle = False  # 暂停待机动画
        current_animation = name  # 更新当前动画名称

    if count < len(animation_photos[name]):  # 如果还有动画帧剩余
        img = Image.open(next(animation_photo_cycles[name]))  # 获取下一帧图片
        img = process_image(img)  # 处理图像（可能翻转）
        photo = ImageTk.PhotoImage(img)  # 转换为 Tkinter 格式
        label.config(image=photo)  # 更新显示
        root.after(animation_speeds[name], play_animation, name, root, label, count + 1)  # 定时调用下一帧
    else:
        # 添加一个短时间的延迟，确保动画状态切换平滑
        root.after(100, lambda: resume_idle_animation(root, label))


def resume_idle_animation(root, label):
    global play_idle, current_animation
    play_idle = True  # 播放完动画后恢复待机动画
    current_animation = None  # 清除动画状态
    change_image(label)  # 强制重新开始待机动画


def move_window(root, label, event):
    x = root.winfo_pointerx() - root.winfo_width() // 2
    y = root.winfo_pointery() - root.winfo_height() // 2
    root.geometry(f'+{x}+{y}')
    play_animation('push', root, label)  # 播放“push”动画


# 新增：处理图像的函数，根据 is_back 决定是否翻转
def process_image(img):
    global is_back
    img = img.resize((image_size, image_size), Image.LANCZOS)  # 调整图片大小
    if is_back:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)  # 水平翻转图像
    return img


# 新增：切换回头模式的函数
def toggle_back_mode():
    global is_back
    is_back = not is_back
