# Clematis Render

Python GUI by Tkinter library for creating the .bat file to render Blender files sufficiently

![ClematisRender Image](https://github.com/Kachornpat/ClematisRender/blob/master/clematisRender.JPG?raw=true)

## ----- Main ------

Blender executable path: Path for Blender.exe to run
Browse exe button: Open the file explorer to choose the Blender.exe
Project folder: The Project's folder. This folder will be chosen by default when you open the file explorer
Browse folder: Open the file explorer to choose the Project's folder
New button: OPen the Shot Detail(below) to add new shot
Edit button: Edit the shot that chosen
Remove button: remove the shots that chosen
Save .bat file button: save the .bat file for rendering
Exit: exit the program

![ShotDetail Image](https://github.com/Kachornpat/ClematisRender/blob/master/shotDetail.png?raw=true)

## ---- Shot Detail -----

Shot name: the name of the Shot
Blender file: the path of the files .blend
Browse file button: Open file explorer to choose file .blend
Output folder: the destination that keep the renders
Browse: Open file explorer to choose Output folder
Start Frame: the first to render
End Frame: the last frame to render
Output format: for example, .png, .jpg, etc.
Submit button: the shot's information to the treeview(table)
Close button: close the window

## How to use ClematisRender

(1) Click "Browse exe" and choose the "blender.exe".
(2) (optional) Click "Browse folder" and choose the Project's folder or the folder that you keep the .blend files.
(3) Click "Add" button to open the shot detail window.
(4) add all the information (shot name is optional, if the shot name is blank, the file's name will be used as shot name).
(5) Click "Submit" the information will be added to the tree view.
(6) Click "Close" button.
(7) Click "Save .bat file" and choose the folder that you want to keep the .bat file, write the file's name and then click "Save".
(8) run the .bat file (not writeLog.bat).

## Note:

- When you add a new shot, the detail window will not close after you submit the data for convenient reason
- You can select multiple shots to remove from the treeview(table).
- For the first time you create the .bat file, the writeLog.bat will be created automatically which will be used for writting the log file.
- After you run .bat file, the `/log` folder will be created and keep the rendering's history.
