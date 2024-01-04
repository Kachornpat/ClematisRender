import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
import threading

process = None
update_th = None


def browse_exe():
    filename = filedialog.askopenfilename(
        title="Select Blender executable",
        filetypes=(("Blender executable", "*.exe*"), ("All files", "*.*")),
    )
    if filename:
        exe_entry.delete(0, tk.END)
        exe_entry.insert(0, filename)


def browse_file():
    filename = filedialog.askopenfilename(
        title="Select Blender File",
        filetypes=(("Blender Files", "*.blend*"), ("All files", "*.*")),
    )
    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)


def render():
    if not (exe_entry.get() or file_entry.get()):
        tk.messagebox.showwarning(
            title="Invalid file path",
            message="Please enter Blender executable/file path",
        )
        return

    elif not (os.path.exists(exe_entry.get()) or os.path.exists(file_entry.get())):
        tk.messagebox.showwarning(
            title="Invalid file path",
            message="Blender executable/file path doesn't exist",
        )
        return

    try:
        global process
        global update_th
        process = subprocess.Popen(
            [
                exe_entry.get().replace("\x08", r"\b"),
                "-b",
                file_entry.get().replace("\x08", r"\b"),
                "-a",
            ],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        update_th = threading.Thread(target=update_text, args=(process,))
        update_th.start()

    except Exception as e:
        print(e)


def update_text(process):
    while True:
        output = process.stdout.readline()
        # print(process.poll())
        if output == b"" and process.poll() is not None:
            break
        # print(output.decode().replace("\n", ""))
        scroll_text.insert(tk.END, output)
        scroll_text.see("end")

    render()


def exit_prog():
    exit()


window = tk.Tk()
window.title("Clematis Render")
window.geometry("560x355")
window.resizable(0, 0)
window.grid_columnconfigure(0, weight=3)
window.grid_columnconfigure(1, weight=1)
window.update_idletasks()

# Blender executable
exe_label = tk.Label(window, text="Blender executable path")
exe_label.grid(row=0, column=0, sticky=tk.W, padx=5)
exe_entry = tk.Entry(window, width=75)
exe_entry.grid(row=1, column=0)
exe_entry.insert(0, "C:\Program Files\Blender Foundation\Blender 4.0\\blender")

find_exe_btn = tk.Button(window, text="Browse exe", command=browse_exe, width=10)
find_exe_btn.grid(row=1, column=1)

# Blender file
file_label = tk.Label(window, text="Blender file path")
file_label.grid(row=3, column=0, sticky=tk.W, padx=5)
file_entry = tk.Entry(window, width=75)
file_entry.grid(row=4, column=0)

find_file_btn = tk.Button(window, text="Browse file", command=browse_file, width=10)
find_file_btn.grid(row=4, column=1)

# scrolltext
scroll_text = ScrolledText(window, width=70, height=13)
scroll_text.grid(row=5, column=0, columnspan=2, pady=7, padx=5)
scroll_text.update_idletasks()

# exit
exit_button = tk.Button(window, text="Exit", command=exit_prog, width=10)
exit_button.grid(row=6, column=1, pady=5)

# render
render_button = tk.Button(window, text="Render", command=render, width=10)
render_button.grid(row=6, column=0, sticky=tk.E, pady=5)

window.mainloop()
