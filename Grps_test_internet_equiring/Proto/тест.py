import tkinter as tk
from tkinter import messagebox
import random


root = tk.Tk()
root.title("Проверка на ориентацию Айбы")


no_click_count = 0


def answer_yes():
    messagebox.showinfo("Ответ", "Айба Гей")
    root.quit()

def answer_no():
    global no_click_count
    no_click_count += 1
    if no_click_count < 5:

        new_x = random.randint(0, root.winfo_width() - no_button.winfo_width())
        new_y = random.randint(0, root.winfo_height() - no_button.winfo_height())
        no_button.place(x=new_x, y=new_y)
    else:

        messagebox.showinfo("Ответ", "Айба не сосал, но все равно Гей")
        root.quit()


label = tk.Label(root, text="Сосал?", font=("Arial", 14))
label.pack(pady=20)


yes_button = tk.Button(root, text="Да", command=answer_yes, width=10)
yes_button.pack(side="left", padx=20, pady=20)


no_button = tk.Button(root, text="Нет", command=answer_no, width=10)
no_button.place(x=150, y=100)


root.minsize(300, 200)


root.mainloop()