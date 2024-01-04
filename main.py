import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
import threading

process = None
update_th = None


def browse_folder():
    filename = filedialog.askdirectory()
    if filename:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, filename)


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
    scroll_text["state"] = "normal"
    if os.path.exists(
        os.path.join(
            output_entry.get(),
            "{:04d}".format(int(last_entry.get())) + format_entry.get(),
        )
    ):
        scroll_text.insert(tk.END, "--------- RENDER FINISH ---------\n")
        scroll_text.see("end")
        scroll_text["state"] = "disabled"
        return
    # print(
    #     os.path.join(
    #         output_entry.get(),
    #         "{:04d}".format(int(last_entry.get())) + format_entry.get(),
    #     )
    # )
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

    if not os.path.exists(
        os.path.join(
            output_entry.get(),
            "{:04d}".format(int(last_entry.get())) + format_entry.get(),
        )
    ):
        render()
        return
    scroll_text.insert(tk.END, "--------- RENDER FINISH ---------\n")
    scroll_text.see("end")
    scroll_text["state"] = "disabled"


def exit_prog():
    process.kill()
    exit()


window = tk.Tk()
window.title("Clematis Render")
window.geometry("560x510")
window.resizable(0, 0)
window.grid_columnconfigure(0, weight=3)
window.grid_columnconfigure(1, weight=1)
window.update_idletasks()

# Blender executable
exe_label = tk.Label(window, text="Blender executable path")
exe_label.grid(row=0, column=0, sticky=tk.W, padx=5)
exe_entry = tk.Entry(window, width=75)
exe_entry.grid(row=1, column=0)
exe_entry.insert(0, "C:\Program Files\Blender Foundation\Blender 4.0/blender")

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
scroll_text["state"] = "disabled"

# exit
exit_button = tk.Button(window, text="Exit", command=exit_prog, width=10)
exit_button.grid(row=6, column=1, pady=5)

# render
render_button = tk.Button(window, text="Render", command=render, width=10)
render_button.grid(row=6, column=0, sticky=tk.E, pady=5)

# output folder
output_label = tk.Label(window, text="Output folder")
output_label.grid(row=7, column=0, sticky=tk.W, padx=5)
output_entry = tk.Entry(window, width=75)
output_entry.grid(row=8, column=0)

find_output_btn = tk.Button(window, text="Browse", command=browse_folder, width=10)
find_output_btn.grid(row=8, column=1)

# last frame number
last_label = tk.Label(window, text="Last frame number")
last_label.grid(row=9, column=0, sticky=tk.W, padx=5)
last_entry = tk.Entry(window)
last_entry.grid(row=10, column=0, sticky=tk.W, padx=10)

# format file
format_label = tk.Label(window, text="format file")
format_label.grid(row=11, column=0, sticky=tk.W, padx=5)
format_entry = tk.Entry(window)
format_entry.grid(row=12, column=0, sticky=tk.W, padx=10)


window.mainloop()
