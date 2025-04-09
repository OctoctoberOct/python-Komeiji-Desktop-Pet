from PIL import Image
import os

def convert_images(directory, format):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 检查文件是否是图片
        if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".gif"):
            # 打开图片
            img = Image.open(filename)
            # 获取文件名（不包括扩展名）
            base = os.path.splitext(filename)[0]
            # 保存为新格式
            img.save(base + "." + format)
            # 删除原始文件
            os.remove(filename)

# 调用函数，把当前目录的所有图片转换为PNG格式，并删除原始文件
convert_images(".", "gif")
