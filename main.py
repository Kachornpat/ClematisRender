import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
import threading
from configparser import ConfigParser

from shot_detail import ShotDetail

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


parser = ConfigParser()
parser.read(CONFIG_FILE)


class ClematisRender(tk.Tk):

    _process = None

    def __init__(self):
        super().__init__()
        self.save_blender_path = parser.get("path", "blender_exe_path")
        self.save_project_path = parser.get("path", "blender_project_path")
        self.save_output_format = parser.get("output", "output_format")
        self.title("Clematis Render")
        self.geometry("800x700")
        self.update_idletasks()
        self.iconphoto(True, tk.PhotoImage(file="clematis.png"))
        self.grid_columnconfigure(0, weight=1)

        self.create_blender_exe_entry()
        self.create_project_entry()
        self.create_shot_treeview()
        self.create_console_log()

        # render
        render_button = tk.Button(self, text="Render", command=self.render)
        render_button.grid(row=12, column=0, padx=5, sticky="nesw")

        # exit
        exit_button = tk.Button(self, text="Exit", command=self.exit_prog)
        exit_button.grid(row=12, column=1, sticky="nesw", columnspan=2, padx=2)

    def create_blender_exe_entry(self):
        exe_label = tk.Label(self, text="Blender executable path")
        exe_label.grid(row=0, column=0, sticky=tk.W)
        self.exe_sv = tk.StringVar()
        self.exe_sv.trace_add("write", self.exe_change_callback)

        self.exe_entry = tk.Entry(self, textvariable=self.exe_sv)
        self.exe_entry.grid(row=1, column=0, sticky="we", padx=5, columnspan=2)
        self.exe_entry.insert(0, self.save_blender_path)

        find_exe_btn = tk.Button(self, text="Browse exe", command=self.browse_exe)
        find_exe_btn.grid(row=1, column=2, sticky="nesw", padx=2)

    def create_project_entry(self):
        project_label = tk.Label(self, text="Project folder")
        project_label.grid(row=2, column=0, sticky=tk.W, padx=5)

        self.project_sv = tk.StringVar()
        self.project_sv.trace_add("write", self.project_entry_callback)

        project_entry = tk.Entry(self, width=60, textvariable=self.project_sv)
        project_entry.grid(row=3, column=0, sticky="we", padx=5, columnspan=2)
        project_entry.insert(0, self.save_project_path)

        find_project_btn = tk.Button(
            self, text="Browse folder", command=self.browse_project_folder
        )
        find_project_btn.grid(row=3, column=2, sticky="nesw", padx=2)

    def create_shot_treeview(self):
        columns = (
            "shot_name",
            "blender_file",
            "start_frame",
            "end_frame",
            "output_folder",
            "result_format",
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        self.tree.heading("shot_name", text="Shot name")
        self.tree.column("shot_name", minwidth=0, width=100, stretch=tk.NO)
        self.tree.heading("blender_file", text="Blender file")
        self.tree.column("blender_file", minwidth=0, width=100)
        self.tree.heading("start_frame", text="Start")
        self.tree.column("start_frame", minwidth=0, width=50, stretch=tk.NO)
        self.tree.heading("end_frame", text="End")
        self.tree.column("end_frame", minwidth=0, width=50, stretch=tk.NO)
        self.tree.heading("output_folder", text="Output folder")
        self.tree.column("output_folder", minwidth=0, width=10)
        self.tree.heading("result_format", text="Format")
        self.tree.column("result_format", minwidth=0, width=60, stretch=tk.NO)

        self.tree.grid(row=5, column=0, sticky="we", pady=5, rowspan=3, padx=(5, 0))
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=5, column=1, sticky="ns", rowspan=3, padx=(0, 2))

        # add new shot
        new_button = tk.Button(
            self, text="New", command=lambda: ShotDetail(self, "New Shot")
        )
        new_button.grid(row=5, column=2, sticky="nesw", padx=2)

        # edit shot
        edit_button = tk.Button(self, text="Edit", command=self.edit_shot)
        edit_button.grid(row=6, column=2, sticky="nesw", padx=2)

        # remove shot
        edit_button = tk.Button(self, text="Remove", command=self.remove_shot)
        edit_button.grid(row=7, column=2, sticky="nesw", padx=2)

    def edit_shot(self):
        selected_item = self.tree.selection()[0]
        (name, file_name, start_frame, end_frame, output_folder, file_format) = (
            self.tree.item(selected_item)["values"]
        )
        ShotDetail(
            self,
            "Edit Shot",
            data={
                "selected_item": selected_item,
                "name": name,
                "file_name": file_name,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "output_folder": output_folder,
                "file_format": file_format,
            },
        )

    def remove_shot(self):
        for selected_item in self.tree.selection():
            self.tree.delete(selected_item)

    def create_console_log(self):
        self.scroll_text = ScrolledText(self, width=65, height=20)
        self.scroll_text.grid(
            row=11, column=0, columnspan=3, pady=5, padx=5, sticky="nesw"
        )
        self.scroll_text.update_idletasks()
        self.scroll_text["state"] = "disabled"

    def save_input(self, file_name, section, key, data):
        parser.set(section, key, data)
        with open(file_name, "w") as config_file:
            parser.write(config_file)

    def browse_exe(self):
        exe_path = filedialog.askopenfilename(
            title="Select Blender executable",
            filetypes=(("Blender executable", "*.exe*"), ("All files", "*.*")),
        )
        if exe_path:
            self.exe_sv.set(exe_path)

    def exe_change_callback(self, *args):
        self.save_input(CONFIG_FILE, "path", "blender_exe_path", self.exe_sv.get())
        self.save_blender_path = self.exe_sv.get()

    def format_option_change(self, data):
        self.save_input(CONFIG_FILE, "output", "output_format", data)

    def browse_project_folder(self):
        folder_name = filedialog.askdirectory()
        if folder_name:
            self.project_sv.set(folder_name)

    def project_entry_callback(self, *args):
        self.save_input(
            CONFIG_FILE, "path", "blender_project_path", self.project_sv.get()
        )
        self.save_project_path = self.project_sv.get()

    def get_format_dict(self):
        return format_dict

    def render(self):
        if not ((self.exe_entry.get()) and os.path.exists(self.exe_entry.get())):
            tk.messagebox.showwarning(
                title="Path Error",
                message="Invalid executable file path",
            )
            return

        self.scroll_text["state"] = "normal"
        self.scroll_text.insert(tk.END, "Start...\n")
        self.scroll_text["state"] = "disabled"

        command = []
        # (name, file_name, start_frame, end_frame, output_folder, format)
        command.append("@echo off\n")
        for i, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item)["values"]
            command.append(f":SHOT_{i}\n")
            command.append(
                'IF EXIST "{}" (\n'.format(
                    values[4]
                    + "/"
                    + "{:04d}".format(int(values[3]))
                    + format_dict.get(values[5])[0],
                )
            )
            command.append(f"    GOTO:SHOT_{i + 1}\n")
            command.append(")\n")
            command.append(
                '"{}" -b "{}" -o {}/ -F {} -s {} -e {} -a\n'.format(
                    self.exe_entry.get().replace("\x08", r"\b"),
                    values[1].replace("\x08", r"\b"),
                    values[4],
                    format_dict.get(values[5])[1],
                    int(values[2]),
                    int(values[3]),
                )
            )
            command.append(f"GOTO:SHOT_{i}\n")

        command.append(f":SHOT_{len(self.tree.get_children())}\n")
        command.append(
            "ECHO ------------------------ RENDER FINISH --------------------------\n"
        )
        command.append("PAUSE\n")
        command.append("EXIT\n")

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

            update_th = threading.Thread(target=self.update_text)
            update_th.daemon = True
            update_th.start()

        except Exception as e:
            print(e)

    def update_text(self):
        while True:
            output = process.stdout.readline()
            if output == b"" and process.poll() is not None:
                break
            self.scroll_text["state"] = "normal"
            self.scroll_text.insert(tk.END, output)
            self.scroll_text.see("end")
            self.scroll_text["state"] = "disabled"

    def exit_prog(self):
        if self._process:
            self._process.kill()
        exit()

    def add_new_shot(
        self, name, file_name, start_frame, end_frame, output_folder, format
    ):
        self.tree.insert(
            "",
            tk.END,
            values=(name, file_name, start_frame, end_frame, output_folder, format),
        )

    def edit_shot_detail(
        self,
        selected_item,
        name,
        file_name,
        start_frame,
        end_frame,
        output_folder,
        format,
    ):
        self.tree.item(
            selected_item,
            values=(name, file_name, start_frame, end_frame, output_folder, format),
        )


if __name__ == "__main__":
    app = ClematisRender()
    app.mainloop()
