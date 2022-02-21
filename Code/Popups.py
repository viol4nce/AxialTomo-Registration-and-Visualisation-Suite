import PySimpleGUI as sg

# Popup for the Gradient Method Parameters
def popupGradient():
    layout = [
        [sg.Text("Einstellungen:")],
        [sg.HorizontalSeparator()],
        [sg.InputCombo(("Register to first", "Register to next"),
            size=(24,1), key="-CIRCLE-",
            default_value="Register to first")],
        [sg.InputCombo(("Gradient Descent", "GD Linesearch"),
            size=(24,1), key="-ALGORITHM-",
            default_value="Gradient Descent")],
        [sg.InputCombo(("MI - Mutual Index", "MSE - Mean Sqared Error"),
            size=(24,1), key="-METRIC-",
            default_value="MI - Mutual Index")],
        [sg.Text("Learning rate: ",size=(12,1)),sg.In( key="-LEARNING RATE-",default_text="0.1",size=(12,1))],
        [sg.Text("Epochs:",size=(12,1)),sg.In( key="-EPOCHS-", default_text="1000",size=(12,1))],
        [sg.Text("Sampling %: ",size=(12,1)),sg.In( key="-SAMPLING PERCENT-",default_text="1.0",size=(12,1))],
        [sg.Checkbox("mit isotropen Bildern arbeiten", key="-ISOTROPIE-")],
        [sg.Checkbox("Multiscale",key="-MULTISCALE-")],
        [sg.Text(" ")],
        [sg.Checkbox("Graphen erzeugen",key="-GRAPHS-",default=True)],
        [sg.Checkbox("45°*n Drehung zurücksetzen", key="-ROTATION-")],
        [sg.HorizontalSeparator()],
        [sg.Button('Registrierung starten!', size=(24,1))],
    ]
    answer = sg.Window('Gradient', layout, modal=True).read(close=True)
    print(answer)
    return answer

# Convert the answer of the Gradient menue
def convertGradientAns(answer, values):
    class settingClass():
        def __init__(self, answer, values):
            # Drop Down Choices#
            print("\nConstructor")
            print(answer["-CIRCLE-"])
            if answer["-CIRCLE-"] == "Register to first":
                self.cycle = "first"
            elif answer["-CIRCLE-"] == "Register to next":
                self.cycle = "next"
            if answer["-ALGORITHM-"] == "Gradient Descent":
                self.algorithm = "GD"
            elif answer["-ALGORITHM-"] == "GD Linesearch":
                self.algorithm = "GDLS"
            if answer["-METRIC-"] == "MI - Mutual Index":
                self.metric = "MI"
            elif answer["-METRIC-"] == "MSE - Mean Sqared Error":
                self.metric = "MSE"

            # Text inputs
            self.lr = float(answer["-LEARNING RATE-"])
            self.epochs = int(answer["-EPOCHS-"])
            self.samplingPercent = float(answer["-SAMPLING PERCENT-"])

            # Checkboxes
            self.isotropie = answer["-ISOTROPIE-"]
            self.multiscale = answer["-MULTISCALE-"]
            self.graph = answer["-GRAPHS-"]
            self.turnback = answer["-ROTATION-"]

            # settings from the main guiInfo
            self.dims = [float(values["-X DIM-"]),
                            float(values["-Y DIM-"]),
                            float(values["-Z DIM-"])]
            self.extIn = values["-FILE TYPE-"]
            self.extOut = values["-OUT FILE TYPE-"]
            self.folderIn = values["-FOLDER-"]
            self.folderOut = values["-OUT FOLDER-"]
            self.savename = values["-SAVENAME-"]
            self.degStep = float(values["-DEG STEP-"])
    settings = settingClass(answer, values)
    return settings

# Popup for the Marker Method Parameters
def popupMarker():
    layout = [
        [sg.Text("Leider noch nicht Fertig")],
        [sg.Button('Schließen', size=(24,1))],
    ]
    answer = sg.Window('Marker', layout, modal=True).read(close=True)
    print(answer)
    return answer

# Popup for the RL Method Parameters
def popupRL():
    layout = [
        [sg.Text("Leider noch nicht Fertig")],
        [sg.Button('Schließen', size=(24,1))],
    ]
    answer = sg.Window('RL', layout, modal=True).read(close=True)
    print(answer)
    return answer

# Popup for the Fourier Method Parameters
def popupFourier():
    layout = [
        [sg.Text("Leider noch nicht Fertig")],
        [sg.Button('Schließen', size=(24,1))],
    ]
    answer = sg.Window('Fourier', layout, modal=True).read(close=True)
    print(answer)
    return answer

# Popup for the Fourier Method Parameters
def popupRender():
    layout = [
        [sg.Text("Parameter: ")],
        [
            sg.Text("Rotation Z: "),
            sg.In(size=(5,1), default_text="45", key="-X ROT-")
        ],
        [
            sg.Text("Rotation Y: "),
            sg.In(size=(5,1), default_text="45", key="-Y ROT-")
        ],
        [
            sg.Text("Rotation X: "),
            sg.In(size=(5,1), default_text="45", key="-Z ROT-")
        ],
        [
            sg.Text("Zoom %: "),
            sg.In(size=(5,1), default_text="10", key="-ZOOM-")
        ],
        [sg.Button('Bild erzeugen', size=(24,1))],
    ]
    answer = sg.Window('Ausgabebild', layout, modal=True).read(close=True)
    print(answer)
    return answer

# Convert the answer of the Render menue
def convertRenderAns(answer, values):
    class settingClass():
        def __init__(self, answer, values):
            # Checkboxes
            self.rotX = float(answer["-X ROT-"])
            self.rotY = float(answer["-Y ROT-"])
            self.rotZ = float(answer["-Z ROT-"])
            self.zoom = int(answer["-ZOOM-"])

            # settings from the main guiInfo
            self.dims = [float(values["-X DIM-"]),
                            float(values["-Y DIM-"]),
                            float(values["-Z DIM-"])]
            self.extIn = values["-FILE TYPE-"]
            self.extOut = values["-OUT FILE TYPE-"]
            self.folderIn = values["-FOLDER-"]
            self.folderOut = values["-OUT FOLDER-"]
            self.savename = values["-SAVENAME-"]
    settings = settingClass(answer, values)
    return settings
