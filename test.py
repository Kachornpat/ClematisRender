import tkinter as tk


def create_popup():
    popup = tk.Toplevel(root)
    popup.title("Popup Window")

    # Disable the underlying window (root window)
    root.grab_set()

    # Add content to the popup window
    label = tk.Label(popup, text="This is a popup window.")
    label.pack(padx=20, pady=20)

    close_button = tk.Button(popup, text="Close", command=lambda: close_popup(popup))
    close_button.pack(padx=20, pady=10)


def close_popup(popup):
    # Re-enable the underlying window (root window)
    root.grab_release()
    popup.destroy()


root = tk.Tk()
root.title("Main Window")

popup_button = tk.Button(root, text="Open Popup", command=create_popup)
popup_button.pack(padx=20, pady=20)

root.mainloop()
