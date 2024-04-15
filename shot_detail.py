import tkinter as tk
from tkinter import filedialog
import os
import re


class ShotDetail(tk.Toplevel):

    def __init__(self, master=None, title="", data={}):

        data: dict

        self.data = data
        super().__init__(master=master)
        self.geometry("+500+300")
        self.title(title)
        self.geometry("495x230")
        self.resizable(0, 0)
        self.grab_set()

        # Shot name
        shot_label = tk.Label(self, text="Shot name")
        shot_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        self.shot_entry = tk.Entry(self, width=60)
        self.shot_entry.grid(row=1, column=0, columnspan=2, padx=(5, 0))

        # Blender file
        file_label = tk.Label(self, text="Blender file")
        file_label.grid(row=2, column=0, sticky=tk.W, padx=5)
        self.file_entry = tk.Entry(self, width=60)
        self.file_entry.grid(row=3, column=0, columnspan=2, padx=(5, 0))

        find_file_btn = tk.Button(
            self, text="Browse file", command=self.browse_blender_file, width=10
        )
        find_file_btn.grid(row=3, column=2, padx=5)

        # # output folder
        output_label = tk.Label(self, text="Output folder")
        output_label.grid(row=4, column=0, sticky=tk.W, padx=5)

        self.output_entry = tk.Entry(self, width=60)
        self.output_entry.grid(row=5, column=0, columnspan=2, padx=(5, 0))
        find_output_btn = tk.Button(
            self, text="Browse", command=self.browse_folder, width=10
        )
        find_output_btn.grid(row=5, column=2)

        # start frame number
        start_label = tk.Label(self, text="Start Frame")
        start_label.grid(row=6, column=0)
        self.start_entry = tk.Entry(self, width=25)
        self.start_entry.grid(row=7, column=0)

        # last frame number
        last_label = tk.Label(self, text="End Frame")
        last_label.grid(row=6, column=1)
        self.end_entry = tk.Entry(self, width=25)
        self.end_entry.grid(row=7, column=1)

        # format file
        format_label = tk.Label(self, text="Output format")
        format_label.grid(row=6, column=2)

        self.format_var = tk.StringVar(
            self,
            value=(
                self.data["file_format"]
                if self.data
                else self.master.save_output_format
            ),
        )
        format_dropdown = tk.OptionMenu(
            self,
            self.format_var,
            *self.master.get_format_dict().keys(),
            command=self.master.format_option_change
        )
        format_dropdown.grid(row=7, column=2, sticky="nesw")

        # submit
        submit_button = tk.Button(self, text="Submit", command=self.submit)
        submit_button.grid(row=8, column=0, padx=5, sticky="nesw", columnspan=2, pady=5)

        # cancel
        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.grid(row=8, column=2, sticky="nesw", padx=2, pady=5)

        if self.data:
            self.shot_entry.insert(0, self.data["name"])
            self.file_entry.insert(0, self.data["file_name"])
            self.start_entry.insert(0, self.data["start_frame"])
            self.end_entry.insert(0, self.data["end_frame"])
            self.output_entry.insert(0, self.data["output_folder"])

    def browse_blender_file(self):
        filename = filedialog.askopenfilename(
            title="Select Blender File",
            filetypes=(("Blender Files", "*.blend*"), ("All files", "*.*")),
            initialdir=self.master.save_project_path,
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def browse_folder(self):
        filename = filedialog.askdirectory(initialdir=self.master.save_project_path)
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    def submit(self):
        if self.data:
            self.master.edit_shot_detail(
                self.data["selected_item"],
                (
                    self.shot_entry.get()
                    if self.shot_entry.get()
                    else re.search(r"[\w-]+?(?=\.)", self.file_entry.get()).group()
                ),
                self.file_entry.get(),
                self.start_entry.get(),
                self.end_entry.get(),
                self.output_entry.get(),
                self.format_var.get(),
            )
        else:
            self.master.add_new_shot(
                (
                    self.shot_entry.get()
                    if self.shot_entry.get()
                    else re.search(r"[\w-]+?(?=\.)", self.file_entry.get()).group()
                ),
                self.file_entry.get(),
                self.start_entry.get(),
                self.end_entry.get(),
                self.output_entry.get(),
                self.format_var.get(),
            )
        self.destroy()

    def check(self):
        if not ((self.file_entry.get()) and os.path.exists(self.file_entry.get())):
            tk.messagebox.showwarning(
                title="Path Error",
                message="Invalid Blender file path",
            )
            return

        if not (self.output_entry.get()):
            tk.messagebox.showwarning(
                title="No output directory",
                message="Please enter the path of render output",
            )
            return

        if not (self.start_entry.get() or self.end_entry.get()):
            tk.messagebox.showwarning(
                title="Frame number not found",
                message="Please enter the number of the start-end frame",
            )
            return
