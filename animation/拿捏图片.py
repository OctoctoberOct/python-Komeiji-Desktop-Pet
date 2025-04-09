from PIL import Image
import os

def process_image(file_path, output_path):
    # 打开图片
    img = Image.open(file_path)
    
    # 改变图片大小
    img = img.resize((500, 500))
    
    # 改变rgb颜色值
    pixels = img.load()
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if 245 <= r <= 255 and 245 <= g <= 255 and 245 <= b <= 255:
                pixels[x, y] = (0, 0, 0)
    
    # 翻转图片
    img = img.rotate(180)
    
    # 水平翻转图片
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    
    # 保存图片
    img.save(output_path, 'PNG')

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            new_filename = 'front_' + filename.split('.')[0] + '_behind.png'
            process_image(os.path.join(directory, filename), os.path.join(directory, new_filename))

# 调用函数处理目录下的所有图片
process_directory('/path/to/your/directory')
