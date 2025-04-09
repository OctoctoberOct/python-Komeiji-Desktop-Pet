import psutil
import time
import tkinter as tk


def update_network_speed():
    global bytes_sent, bytes_recv
    # 获取当前网络流量信息
    net_io_counters = psutil.net_io_counters()
    new_bytes_sent = net_io_counters.bytes_sent
    new_bytes_recv = net_io_counters.bytes_recv

    # 计算发送和接收的字节数
    sent_speed = new_bytes_sent - bytes_sent
    recv_speed = new_bytes_recv - bytes_recv

    # 更新初始流量信息
    bytes_sent = new_bytes_sent
    bytes_recv = new_bytes_recv

    # 转换为更易读的单位
    sent_speed_str = f"{sent_speed / 1024:.2f} KB/s"
    recv_speed_str = f"{recv_speed / 1024:.2f} KB/s"

    # 更新标签文本
    speed_label.config(text=f"发送速度: {sent_speed_str}, 接收速度: {recv_speed_str}")

    # 每秒更新一次
    root.after(1000, update_network_speed)


# 获取初始网络流量信息
net_io_counters = psutil.net_io_counters()
bytes_sent = net_io_counters.bytes_sent
bytes_recv = net_io_counters.bytes_recv

# 创建主窗口
root = tk.Tk()
root.title("实时网速监控")

# 设置窗口保持在最上方
root.attributes("-topmost", True)

# 创建标签用于显示网速
speed_label = tk.Label(root, text="加载中...", font=("Arial", 14))
speed_label.pack(padx=20, pady=20)

# 启动更新函数
update_network_speed()

# 运行主循环
root.mainloop()
    
