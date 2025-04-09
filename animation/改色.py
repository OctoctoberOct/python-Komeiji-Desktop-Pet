import os
from PIL import Image

def change_white_to_ivory(image_path):
    # 打开图片
    img = Image.open(image_path)
    # 转换为RGBA模式
    img = img.convert("RGBA")

    # 获取图片的尺寸
    width, height = img.size
    # 定义乳白色的RGBA值255, 255, 240, 255
    ivory = (245, 245, 245, 255)
    # 遍历图片的每一个像素
    for x in range(width):
        for y in range(height):
            r, g, b, a = img.getpixel((x, y))
            # 如果像素是白色，就把它改成乳白色
            if r == 255 and g == 255 and b == 255:
                img.putpixel((x, y), ivory)
    
    # 保存修改后的图片为一个新的文件，而不是覆盖原文件
    img.save( image_path)

# 获取当前目录下的所有文件
files = os.listdir('.')
# 遍历所有文件
for file in files:
    # 如果文件是.png或.gif图片
    if file.endswith('.png') or file.endswith('.gif'):
        # 调用函数处理图片
        change_white_to_ivory(file)

print("改色完成")
