import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
import threading
from configparser import ConfigParser

CONFIG_FILE = "treebase.ini"

format_dict = {
    "BMP": ".bmp",
    "Tris": ".rgb",
    "PNG": ".png",
    "JPEG": ".jpg",
    "JPEG 2000": ".jp2",
    "Targo": ".tga",
    "Cineon": ".cin",
    "DPX": ".dpx",
    "OpenEXR": ".exr",
    "Radiance HDR": ".hdr",
    "TIFF": ".tif",
    "WebP": ".webp",
}


process = None
update_th = None

parser = ConfigParser()
parser.read(CONFIG_FILE)

save_blender_path = parser.get("path", "blender_exe_path")
save_output_format = parser.get("output", "output_format")


def save_input(file_name, section, key, data):
    parser.set(section, key, data)
    with open(file_name, "w") as config_file:
        parser.write(config_file)


def browse_folder():
    filename = filedialog.askdirectory()
    if filename:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, filename)


def browse_exe():
    exe_path = filedialog.askopenfilename(
        title="Select Blender executable",
        filetypes=(("Blender executable", "*.exe*"), ("All files", "*.*")),
    )
    if exe_path:
        exe_entry.delete(0, tk.END)
        exe_entry.insert(0, exe_path)
        save_input(CONFIG_FILE, "path", "blender_exe_path", exe_path)


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

    if last_entry.get() and os.path.exists(
        os.path.join(
            output_entry.get(),
            "{:04d}".format(int(last_entry.get())) + format_dict.get(option_var.get()),
        )
    ):
        scroll_text.insert(
            tk.END,
            "------------------------- RENDER FINISH --------------------------\n",
        )
        scroll_text.see("end")
        scroll_text["state"] = "disabled"
        return

    scroll_text.insert(
        tk.END, "-------------------------- START RENDER --------------------------\n"
    )

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
        if output == b"" and process.poll() is not None:
            break
        scroll_text.insert(tk.END, output)
        scroll_text.see("end")


def exit_prog():
    if process:
        process.kill()
    exit()


def format_option_change(data):
    save_input(CONFIG_FILE, "output", "output_format", data)


window = tk.Tk()
window.title("Clematis Render")
window.geometry("560x500")
window.resizable(0, 0)
window.grid_columnconfigure(0, weight=3)
window.grid_columnconfigure(1, weight=1)
window.update_idletasks()
icon = tk.PhotoImage(file="clemetis.png")
window.iconphoto(True, icon)


# Blender executable
exe_label = tk.Label(window, text="Blender executable path")
exe_label.grid(row=0, column=0, sticky=tk.W, padx=5)
exe_entry = tk.Entry(window, width=75)
exe_entry.grid(row=1, column=0)
exe_entry.insert(0, save_blender_path)

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

# output folder
output_label = tk.Label(window, text="Output folder")
output_label.grid(row=6, column=0, sticky=tk.W, padx=5)

output_entry = tk.Entry(window, width=75)
output_entry.grid(row=7, column=0)
find_output_btn = tk.Button(window, text="Browse", command=browse_folder, width=10)
find_output_btn.grid(row=7, column=1)

# last frame number
last_label = tk.Label(window, text="Last frame number")
last_label.grid(row=8, column=0, sticky=tk.W, padx=5)
last_entry = tk.Entry(window)
last_entry.grid(row=9, column=0, sticky=tk.W, padx=10)

# format file
format_label = tk.Label(window, text="Output format")
format_label.grid(row=10, column=0, sticky=tk.W, padx=5)

option_var = tk.StringVar(window, value=save_output_format)
format_dropdown = tk.OptionMenu(
    window, option_var, *format_dict.keys(), command=format_option_change
)
format_dropdown.grid(row=11, column=0, sticky=tk.W, padx=10)

# exit
exit_button = tk.Button(window, text="Exit", command=exit_prog, width=10)
exit_button.grid(row=12, column=1, pady=5)

# render
render_button = tk.Button(window, text="Render", command=render, width=10)
render_button.grid(row=12, column=0, sticky=tk.E, pady=5)


window.mainloop()
