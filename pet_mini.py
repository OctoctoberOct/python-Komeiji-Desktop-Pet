import sys
import tkinter as tk
from pathlib import Path

# 获取 pet_organ 目录的绝对路径
pet_organ_dir = Path(__file__).parent / 'pet_organ'
sys.path.append(str(pet_organ_dir))

from pet_organ.animation import change_image, play_loot_animation, play_animation, move_window
from pet_organ.menu_mini import show_menu
from pet_organ.eat import get_hunger, save_hunger, feed, decrease_hunger
import pet_organ.aichat

print(f"当前饥饿值: {get_hunger()}")

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-transparentcolor", "white")
root.wm_attributes("-topmost", 1)

label = tk.Label(root, bg='white')
label.pack()

label.bind('<Button-3>', lambda event: show_menu(root, label, event))
label.bind('<B1-Motion>', lambda event: move_window(root, label, event))

play_loot_animation(root, label)
change_image(label)

decrease_hunger(root)

root.protocol("WM_DELETE_WINDOW", lambda: [save_hunger(), root.destroy()])
root.mainloop()
