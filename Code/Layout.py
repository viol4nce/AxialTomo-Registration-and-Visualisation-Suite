import PySimpleGUI as sg

file_list_column = [
    [
        sg.Text("Image Folder", size=(10,1)),
        sg.In(size=(25,1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text("File type", size=(10,1)),
        sg.InputCombo((".tif",".lsm"),
            size=(5,1), enable_events=True, key="-FILE TYPE-",
            default_value=".tif"
            ),
    ],
    [
        sg.Text("           X [\u00B5m]", size=(10,1)),
        sg.In(size=(5,1), enable_events=True, default_text="1.0", key="-X DIM-"),
        sg.Text("Y [\u00B5m]"),
        sg.In(size=(5,1), enable_events=True, default_text="1.0", key="-Y DIM-"),
        sg.Text("Z [\u00B5m]"),
        sg.In(size=(5,1), enable_events=True, default_text="1.0", key="-Z DIM-"),
    ],
    [
        sg.Text("Winkelschritt in Grad", size=(10,1)),
        sg.In(size=(3,1), enable_events=True, default_text="45.0", key="-DEG STEP-"),
    ],
    [sg.HorizontalSeparator()],
    [sg.Text("Liste der Bilddateien im Ordner:")],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(50, 20),
            select_mode = "LISTBOX_SELECT_MODE_SINGLE",
            key="-FILE LIST-"
        )
    ],
]

image_viewer_column = [
    [sg.Text("Choose an image from the list on the left to display:", size=(40,1))],
    [sg.Text(size=(40,1), key="-TOUT-")],
    [sg.Text(size=(4,1)), sg.Image(key="-IMAGE-")],
    [sg.HorizontalSeparator()],
    [
        sg.Text("Noise Threshold: "),
        sg.Slider(range=(0,255),default_value=20,size=(20,15),orientation='horizontal',font=('Helvetica', 12), key="-NOISE THRESH-"),
    ],
    [sg.Checkbox("Rand der Volumen Anzeigen", key="-CAGED-")],
    [sg.Button("Solo Volume Renderer", size=(20, 1), key="-3D VIEW VTK-"),sg.Button("Multi Volume Renderer", size=(20, 1), key="-3D VIEW VTK Multi-")],
    [sg.Button("Solo Pointcloud Viewer", size=(20, 1), key="-3D VIEW O3D-"),sg.Button("Multi Pointcloud Viewer", size=(20, 1), key="-3D VIEW O3D Multi-")],
    [sg.Button("Hochaufgelöste Projektion generieren", size=(42, 1), key="-RENDER-")]
]

output_column = [
    [
        sg.Text("Output Folder: ", size=(10, 1)),
        sg.In(size=(25,1), enable_events=True, key="-OUT FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text("Filename: ", size=(10, 1)),
        sg.In(size=(25,1), enable_events=True, key="-SAVENAME-"),
        sg.InputCombo((".tif",".lsm"),
            size=(5,1), enable_events=True, key="-OUT FILE TYPE-",
            default_value=".tif"
            ),
    ],
    [sg.HorizontalSeparator()],
    [sg.Text("Algorithmen: ")],
    [sg.Button("Gradient: Insight Segmentation and Registration Toolkit", size=(40, 2), key="-GRADIENT-")],
    [sg.Button("Landmark nach Preibisch und Tomancak(2010)",size=(40, 2),button_color='gray', key="-MARKER-")],
    [sg.Button("Reinforcement Learning ", size=(40, 2),button_color='gray', key="-RL-")],
    [sg.Button("Fourier nach Heintzmann und Cremer(2002)",button_color='gray', size=(40, 2), key="-FOURIER-")],
    [sg.HorizontalSeparator()],
    [sg.Text("Informationen zum Ergebnis der Image Matchings: ")],
    [sg.Multiline(enable_events=True, size=(44, 10), key="-INFO-")]
]

layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
        sg.VSeperator(),
        sg.Column(output_column),
    ]
]
