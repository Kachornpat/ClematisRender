import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
import threading
from configparser import ConfigParser

CONFIG_FILE = "treebase.ini"

format_dict = {
    "BMP": (".bmp", "BMP"),
    "Iris": (".rgb", "IRIS"),
    "PNG": (".png", "PNG"),
    "JPEG": (".jpg", "JPEG"),
    "JPEG 2000": (".jp2", "JP2"),
    "Targo": (".tga", "TGA"),
    "Cineon": (".cin", "CINEON"),
    "DPX": (".dpx", "DPX"),
    "OpenEXR": (".exr", "OPEN_EXR"),
    "Radiance HDR": (".hdr", "HDR"),
    "TIFF": (".tif", "TIFF"),
    "WebP": (".webp", "WEBP"),
}


process = None

parser = ConfigParser()
parser.read(CONFIG_FILE)

save_blender_path = parser.get("path", "blender_exe_path")
save_project_path = parser.get("path", "blender_project_path")
save_output_format = parser.get("output", "output_format")


def save_input(file_name, section, key, data):
    parser.set(section, key, data)
    with open(file_name, "w") as config_file:
        parser.write(config_file)


def browse_exe():
    exe_path = filedialog.askopenfilename(
        title="Select Blender executable",
        filetypes=(("Blender executable", "*.exe*"), ("All files", "*.*")),
    )
    if exe_path:
        exe_sv.set(exe_path)


def exe_callback(*args):
    save_input(CONFIG_FILE, "path", "blender_exe_path", exe_sv.get())
    global save_blender_path
    save_blender_path = exe_sv.get()


def browse_project_folder():
    folder_name = filedialog.askdirectory()
    if folder_name:
        project_sv.set(folder_name)


def project_entry_callback(*args):
    save_input(CONFIG_FILE, "path", "blender_project_path", project_sv.get())
    global save_project_path
    save_project_path = project_sv.get()


def browse_blender_file():
    filename = filedialog.askopenfilename(
        title="Select Blender File",
        filetypes=(("Blender Files", "*.blend*"), ("All files", "*.*")),
        initialdir=save_project_path,
    )
    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)


def browse_folder():
    filename = filedialog.askdirectory(initialdir=save_project_path)
    if filename:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, filename)


def format_option_change(data):
    save_input(CONFIG_FILE, "output", "output_format", data)


def render():
    if not (exe_entry.get()):
        tk.messagebox.showwarning(
            title="Invalid file path",
            message="Please enter Blender executable path",
        )
        return

    elif not (file_entry.get()):
        tk.messagebox.showwarning(
            title="Invalid file path",
            message="Please enter Blender file path",
        )
        return

    elif not (os.path.exists(exe_entry.get()) or os.path.exists(file_entry.get())):
        tk.messagebox.showwarning(
            title="Invalid file path",
            message="Blender executable/file path doesn't exist",
        )
        return

    elif not (output_entry.get()):
        tk.messagebox.showwarning(
            title="No output directory",
            message="Please enter the path of render output",
        )
        return

    elif not (start_entry.get() or end_entry.get()):
        tk.messagebox.showwarning(
            title="Frame number not found",
            message="Please enter the number of the start-end frame",
        )
        return

    scroll_text["state"] = "normal"
    scroll_text.insert(tk.END, "Start...\n")
    scroll_text["state"] = "disabled"

    command = []
    command.append("@echo off\n")
    command.append(":start_render\n")
    command.append(
        'IF EXIST "{}" (\n'.format(
            output_entry.get()
            + "/"
            + "{:04d}".format(int(end_entry.get()))
            + format_dict.get(format_var.get())[0],
        )
    )
    command.append(
        "    ECHO ------------------------ RENDER FINISH --------------------------\n"
    )
    command.append("    PAUSE\n")
    command.append("    EXIT\n")
    command.append(")\n")
    command.append(
        '"{}" -b "{}" -o {}/ -F {} -s {} -e {} -a\n'.format(
            exe_entry.get().replace("\x08", r"\b"),
            file_entry.get().replace("\x08", r"\b"),
            output_entry.get(),
            format_dict.get(format_var.get())[1],
            int(start_entry.get()),
            int(end_entry.get()),
        )
    )
    command.append("GOTO:start_render\n")

    with open("render.bat", "w") as f:
        f.write("".join(command))

    try:
        global process
        process = subprocess.Popen(
            ["render.bat"],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        update_th = threading.Thread(target=update_text)
        update_th.daemon = True
        update_th.start()

    except Exception as e:
        print(e)


def update_text():
    while True:
        output = process.stdout.readline()
        if output == b"" and process.poll() is not None:
            break
        scroll_text["state"] = "normal"
        scroll_text.insert(tk.END, output)
        scroll_text.see("end")
        scroll_text["state"] = "disabled"


def exit_prog():
    if process:
        process.kill()
    exit()


window = tk.Tk()
window.title("Clematis Render")
window.geometry("560x505")
window.resizable(0, 0)
window.update_idletasks()
icon = tk.PhotoImage(file="clematis.png")
window.iconphoto(True, icon)

# Blender executable
exe_label = tk.Label(window, text="Blender executable path")
exe_label.grid(row=0, column=0, sticky=tk.W, padx=5)

exe_sv = tk.StringVar()
exe_sv.trace_add("write", exe_callback)

exe_entry = tk.Entry(window, width=60, textvariable=exe_sv)
exe_entry.grid(row=1, column=0, columnspan=2)
exe_entry.insert(0, save_blender_path)

find_exe_btn = tk.Button(window, text="Browse exe", command=browse_exe, width=10)
find_exe_btn.grid(row=1, column=2)

# Project folder
project_label = tk.Label(window, text="Project folder")
project_label.grid(row=2, column=0, sticky=tk.W, padx=5)


project_sv = tk.StringVar()
project_sv.trace_add("write", project_entry_callback)

project_entry = tk.Entry(window, width=60, textvariable=project_sv)
project_entry.grid(row=3, column=0, columnspan=2)
project_entry.insert(0, save_project_path)

find_project_btn = tk.Button(
    window, text="Browse folder", command=browse_project_folder, width=10
)
find_project_btn.grid(row=3, column=2, padx=5)

# Blender file
file_label = tk.Label(window, text="Blender file")
file_label.grid(row=4, column=0, sticky=tk.W, padx=5)
file_entry = tk.Entry(window, width=60)
file_entry.grid(row=5, column=0, columnspan=2)

find_file_btn = tk.Button(
    window, text="Browse file", command=browse_blender_file, width=10
)
find_file_btn.grid(row=5, column=2, padx=5)

# # scrolltext
scroll_text = ScrolledText(window, width=65, height=13)
scroll_text.grid(row=6, column=0, columnspan=3, pady=7, padx=5)
scroll_text.update_idletasks()
scroll_text["state"] = "disabled"

# # output folder
output_label = tk.Label(window, text="Output folder")
output_label.grid(row=7, column=0, sticky=tk.W, padx=5)

output_entry = tk.Entry(window, width=60)
output_entry.grid(row=8, column=0, columnspan=2)
find_output_btn = tk.Button(window, text="Browse", command=browse_folder, width=10)
find_output_btn.grid(row=8, column=2)

# start frame number
start_label = tk.Label(window, text="Start Frame")
start_label.grid(row=9, column=0, padx=5)
start_entry = tk.Entry(window, width=25)
start_entry.grid(row=10, column=0, padx=5)

# last frame number
last_label = tk.Label(window, text="End Frame")
last_label.grid(row=9, column=1, padx=5)
end_entry = tk.Entry(window, width=25)
end_entry.grid(row=10, column=1, padx=5)

# format file
format_label = tk.Label(window, text="Output format")
format_label.grid(row=9, column=2, padx=5)

format_var = tk.StringVar(window, value=save_output_format)
format_dropdown = tk.OptionMenu(
    window, format_var, *format_dict.keys(), command=format_option_change
)
format_dropdown.grid(row=10, column=2, padx=5)

# render
render_button = tk.Button(window, text="Render", command=render, width=15)
render_button.grid(row=12, column=1, pady=5, sticky=tk.E)

# exit
exit_button = tk.Button(window, text="Exit", command=exit_prog, width=15)
exit_button.grid(row=12, column=2, pady=5)

window.mainloop()
