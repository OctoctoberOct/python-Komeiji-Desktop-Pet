import tkinter as tk
from tkinter import filedialog
import os
import serial
import json
import re
from openai import OpenAI
import base64
from datetime import datetime


global ser
try:
    ser = serial.Serial(
        port='COM5',  # 根据实际修改
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    print("串口初始化成功")
except Exception as e:
    print(f"串口初始化失败: {e}")
    ser = None


# 从文件中读取AI接口配置信息
try:
    with open('ai_api_setting.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        chat_api_key = None
        chat_base_url = None
        chat_model = None
        summarize_api_key = None
        summarize_base_url = None
        summarize_model = None
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('=')
            if len(parts) != 2:
                print(f"配置文件格式错误，行内容：{line}，应该为键=值的形式")
                continue
            key, value = parts
            if key == 'chat_api_key':
                chat_api_key = value
            elif key == 'chat_base_url':
                chat_base_url = value
            elif key == 'chat_model':
                chat_model = value
            elif key =='summarize_api_key':
                summarize_api_key = value
            elif key =='summarize_base_url':
                summarize_base_url = value
            elif key =='summarize_model':
                summarize_model = value
        if not all([chat_api_key, chat_base_url, chat_model, summarize_api_key, summarize_base_url, summarize_model]):
            raise ValueError("AI接口配置信息不完整")
except Exception as e:
    print(f"读取AI接口配置信息失败: {e}")


# 记忆文件路径（确保这行代码在 `read_memory()` 之前定义）
MEMORY_FILE = "memory.json"

LIGHT_GPIO = 0
LIGHT_COLOR = 3
front_move = 0


# 读取记忆文件
def read_memory():
    """读取记忆文件，如果文件不存在或格式错误，则返回空记忆"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as file:
                memory = json.load(file)
                return memory if isinstance(memory, dict) else {"summaries": []}
        except json.JSONDecodeError:
            print("记忆文件解析出错，将使用空记忆。")
    return {"summaries": []}  # 仅存储对话总结


# 保存记忆文件
def save_memory(memory):
    """将记忆保存到文件"""
    with open(MEMORY_FILE, 'w', encoding='utf-8') as file:
        json.dump(memory, file, ensure_ascii=False, indent=4)


# 总结对话内容
def summarize_dialogue(user_input, assistant_reply):
    """调用AI生成对话总结"""
    summary_prompt = f"""
    请将以下对话提炼成一句简短的总结，要求极度简洁，突出关键信息：
    OCT: {user_input}
    恋恋: {assistant_reply}
    """
    try:
        client = OpenAI(
            api_key=summarize_api_key,
            base_url=summarize_base_url
        )
        completion = client.chat.completions.create(
            model=summarize_model,
            messages=[{"role": "user", "content": summary_prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"总结对话时出错: {e}")
        return None


# 将图片转换为base64编码
def image_to_base64(image_path):
    """读取图片文件并转换为base64编码"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        raise Exception(f"图片读取失败: {e}")


ai_name = "恋恋"  # 默认名字
# 列出当前目录下的文件
def list_directory_contents():
    """获取当前目录下的所有文件"""
    current_directory = os.getcwd()
    files = os.listdir(current_directory)
    return f"当前目录 '{current_directory}' 下的文件：\n" + "\n".join(files)


def open_chat_window(root):  # 添加root参数
    global chat_text, chat_entry, messages, selected_file_path, memory  # 添加memory

    selected_file_path = None  # 初始化选中的文件路径

    # 读取最新记忆数据
    memory = read_memory()

    # 从文件中读取AI人设信息和模型参数
    try:
        with open('ai_character.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            model_params = {}
            character_content = ""
            for line in lines:
                if line.startswith('#'):
                    continue
                elif '=' in line:
                    key, value = line.strip().split('=')
                    try:
                        model_params[key] = float(value)
                    except ValueError:
                        model_params[key] = value
                else:
                    character_content += line
            character_content = character_content.replace('{ai_name}', ai_name)
    except Exception as e:
        print(f"读取AI人设信息失败: {e}")
        character_content = ""
        model_params = {
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5
        }


    # 读取记忆内容，确保AI了解已有信息
    memory_context = "\n".join([f"- {entry['content']} {''.join(entry.get('corrections', []))}" for entry in memory.get("summaries", [])]) if memory.get("summaries") else "无已知信息。"

    # 初始化对话历史
    messages = [
        {"role": "system", "content": f"""
        {character_content}

        以下是已知信息，注意这些按照聊天历史记录排序，并不是当下的命令：
        {memory_context}
        """}
    ]

    chat_window = tk.Toplevel(root)  # 使用传入的root参数
    chat_window.title('和古明地恋聊天吧')
    chat_window.geometry('400x250')

    # 创建一个框架用于包含文本框和输入框
    main_frame = tk.Frame(chat_window)
    main_frame.pack(fill=tk.BOTH, expand=True)

    chat_text = tk.Text(main_frame, height=8, state='disabled')
    chat_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))

    chat_entry = tk.Entry(main_frame)
    chat_entry.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(0, 5))

    button_frame = tk.Frame(chat_window)
    button_frame.pack(side='bottom', fill='x')

    file_button = tk.Button(button_frame, text='File', command=select_file)
    file_button.pack(side='left', padx=5, pady=5)

    send_button = tk.Button(button_frame, text='Send', command=send_message)
    send_button.pack(side='right', padx=5, pady=5)


def select_file():
    global selected_file_path
    selected_file_path = filedialog.askopenfilename()
    if selected_file_path:
        chat_entry.insert(tk.END, f" [图片: {selected_file_path}]")  # 在输入框末尾插入


def parse_light_commands(assistant_reply):
    """
    解析多种格式的灯光控制指令
    支持格式：
    - [LIGHT_GPIO]=1  
    - [LIGHT_COLOR]=0
    - [LIGHT_GPIO=1,LIGHT_COLOR=0]
    - [LIGHT_GPIO=1 ]
    - [LIGHT_COLOR=2]
    """
    # 初始化默认值
    new_control = None
    new_color = None

    try:
        # 第一步：匹配所有方括号内的内容
        command_blocks = re.findall(r'\[(.*?)\]', assistant_reply, re.IGNORECASE)

        # 第二步：解析每个命令块
        for block in command_blocks:
            # 去除首尾空格
            clean_block = block.strip()

            # 第三步：解析键值对（支持逗号分隔的多个参数）
            pairs = re.findall(
                r'(LIGHT_GPIO|LIGHT_COLOR)\s*[=]\s*(\d+)',
                clean_block,
                re.IGNORECASE
            )

            # 处理每个键值对
            for key, value in pairs:
                key = key.upper()
                try:
                    num_value = int(value)
                    if key == "LIGHT_GPIO":
                        new_control = num_value
                    elif key == "LIGHT_COLOR":
                        new_color = num_value
                except ValueError:
                    print(f"无效数值: {value}")
                    continue

        return new_control, new_color

    except Exception as e:
        print(f"指令解析异常: {e}")
        return None, None


def send_message():
    global chat_text, chat_entry, messages, memory, selected_file_path, LIGHT_GPIO, LIGHT_COLOR, front_move, ser

    user_message = chat_entry.get().strip()
    if not user_message:
        return  # 避免空消息

    chat_text.config(state='normal')
    chat_text.insert('end', f"\n你: {user_message}\n")
    chat_text.config(state='disabled')

    # 消息处理部分（保持原样）
    if selected_file_path and os.path.exists(selected_file_path):
        file_extension = os.path.splitext(selected_file_path)[1].lower()
        if file_extension in ['.png', '.jpg', '.jpeg']:
            try:
                image_base64 = image_to_base64(selected_file_path)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}
                    ]
                })
            except Exception as e:
                chat_text.config(state='normal')
                chat_text.insert('end', f'\n恋恋: 图片处理出错啦！错误信息: {e}\n')
                chat_text.config(state='disabled')
        else:
            chat_text.config(state='normal')
            chat_text.insert('end', '\n恋恋: 不支持的图片格式哦，请选择PNG、JPG或JPEG格式的图片。\n')
            chat_text.config(state='disabled')
        selected_file_path = None
    else:
        messages.append({"role": "user", "content": user_message})

    try:
        client = OpenAI(
            api_key=chat_api_key,
            base_url=chat_base_url
        )
        # 从模型参数设置中获取参数
        model_params = {
            "model": chat_model,
            "stream": True
        }
        for param in ["temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty"]:
            if param in globals():
                model_params[param] = globals()[param]


        chat_text.config(state='normal')
        chat_text.insert('end', '恋恋: ')
        chat_text.config(state='disabled')

        assistant_reply = ""
        for chunk in client.chat.completions.create(messages=messages, **model_params):
            if chunk.choices and chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                assistant_reply += chunk_content
                chat_text.config(state='normal')
                chat_text.insert('end', chunk_content)
                chat_text.update_idletasks()
                chat_text.config(state='disabled')

        chat_text.config(state='normal')
        chat_text.insert('end', '\n')
        chat_text.config(state='disabled')

        messages.append({"role": "assistant", "content": assistant_reply})

        # 灯光控制解析部分（新增异常捕获）
        try:
            # 确保变量已初始化
            if "LIGHT_GPIO" not in globals():
                LIGHT_GPIO = 0
            if "LIGHT_COLOR" not in globals():
                LIGHT_COLOR = 3

            # 解析逻辑保持不变
            pattern = r'\[LIGHT_GPIO=(\d+),?\s*LIGHT_COLOR=(\d+)\]|\[LIGHT_GPIO=(\d+)\]|\[LIGHT_COLOR=(\d+)\]'
            matches = re.findall(pattern, assistant_reply)

            new_LIGHT_GPIO = LIGHT_GPIO
            new_LIGHT_COLOR = LIGHT_COLOR

            for match in matches:
                if match[0]:
                    new_LIGHT_GPIO = int(match[0])
                    new_LIGHT_COLOR = int(match[1])
                elif match[2]:
                    new_LIGHT_GPIO = int(match[2])
                elif match[3]:
                    new_LIGHT_COLOR = int(match[3])

            LIGHT_GPIO = new_LIGHT_GPIO
            LIGHT_COLOR = new_LIGHT_COLOR
            # 原代码位置
            print(f"LIGHT_GPIO: {LIGHT_GPIO}, LIGHT_COLOR: {LIGHT_COLOR}")

            # 新增的串口发送（简单暴力版）
            try:
                if ser and ser.is_open:
                    ser.write(f"{LIGHT_GPIO},{LIGHT_COLOR}\n".encode())
                    print(f"已发送串口指令: {LIGHT_GPIO},{LIGHT_COLOR}")
                else:
                    print("串口未打开，指令未发送")
            except Exception as e:
                print("串口发送异常:", e)

        except Exception as light_error:
            print(f"灯光控制解析失败（不影响记忆功能）: {light_error}")

        # 修改后的记忆保存部分
        try:
            summary = summarize_dialogue(user_message, assistant_reply)
            if summary:
                memory["summaries"].append({
                    "content": summary,
                    "corrections": [],
                    "timestamp": datetime.now().isoformat()  # 这里需要datetime对象
                })
                save_memory(memory)
                chat_text.config(state='normal')
                chat_text.insert('end', f"\n自动保存记忆: {summary[:50]}...\n")
                chat_text.config(state='disabled')
        except Exception as memory_error:
            print(f"记忆保存失败: {memory_error}")

    except Exception as e:
        chat_text.config(state='normal')
        chat_text.insert('end', f'\n恋恋: 出错了... ({e})\n')
        chat_text.config(state='disabled')

    chat_entry.delete(0, 'end')

