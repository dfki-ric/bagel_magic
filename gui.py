#! /usr/bin/env python

import os
import sys
import execute as ex
import subprocess
import yaml
import time

haveQT5 = True
try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except:
    haveQT5 = False
if not haveQT5:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
#import pybob

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Magic Bagel")

left = QWidget()
right = QWidget()

topVLayout = QVBoxLayout(window)

hLayout = QHBoxLayout()
vLayout = QVBoxLayout()
hLayout.addWidget(left)
hLayout.addWidget(right)
left.setLayout(vLayout)
spLeft = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
spLeft.setHorizontalStretch(1)
left.setSizePolicy(spLeft)

# setup right window
vLayout2 = QVBoxLayout()
right.setLayout(vLayout2)
spRight = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
spRight.setHorizontalStretch(3)
right.setSizePolicy(spRight)
#hLayout.addLayout(vLayout2)
outConsole = QTextEdit()
outConsole.setReadOnly(True)
outConsole.ensureCursorVisible()
debugConsole = outConsole

executeList = []

font = QFont()
font.setPointSize(16)
outConsole.setFont(font)

vLayout2.addWidget(outConsole)
#errConsole = QTextEdit()
#errConsole.setReadOnly(True)
#vLayout2.addWidget(errConsole)


startMARSPush = QPushButton("")
startMARSPush.setFixedSize(107, 100);
startMARSPush.setStyleSheet("QPushButton { background-image: url(images/mars_logo.png); border: 2px solid grey; border-radius: 8px;} \n QPushButton:pressed { border: 2px solid darkblue; border-radius: 8px;}");
#startMARSPush.setStyleSheet("*:pressed { border: 1 }");

startBagelPush = QPushButton("")
startBagelPush.setFixedSize(144, 100);
startBagelPush.setStyleSheet("QPushButton { background-image: url(images/bagel_gui.png); border: 2px solid grey; } \n QPushButton:pressed { border: 2px solid darkblue;}");

resetPush = QPushButton("")
resetPush.setFixedSize(100, 100);
resetPush.setStyleSheet("QPushButton { background-image: url(images/reset.png); border: 2px solid grey; border-radius: 8px;} \n QPushButton:pressed { border: 2px solid darkblue; border-radius: 8px;}");

rootPath = os.environ["AUTOPROJ_CURRENT_ROOT"]
modelsPath = os.path.join(rootPath, "models")

robotGroup = QGroupBox("Robot")
robotVLayout = QVBoxLayout(robotGroup)
robotsFolderCombo = QComboBox()
robotsCombo = QComboBox()
robotsPath = os.path.join(modelsPath, "robots")
robotsComboPath = []
if os.path.exists(robotsPath):
    for d in os.listdir(robotsPath):
        if os.path.isdir(os.path.join(robotsPath, d)):
            robotsFolderCombo.addItem(d)
robotVLayout.addWidget(robotsFolderCombo)
robotVLayout.addWidget(robotsCombo)

envGroup = QGroupBox("Environment")
envVLayout = QVBoxLayout(envGroup)
envFolderCombo = QComboBox()
envCombo = QComboBox()
envPath = os.path.join(modelsPath, "environments")
envComboPath = []
if os.path.exists(envPath):
    for d in os.listdir(envPath):
        if os.path.isdir(os.path.join(envPath, d)):
            envFolderCombo.addItem(d)
envVLayout.addWidget(envFolderCombo)
envVLayout.addWidget(envCombo)

modelGroup = QGroupBox("Bagel control")
modelVLayout = QVBoxLayout(modelGroup)
modelsCombo = QComboBox()
versionsCombo = QComboBox()
dbPath = os.path.join(rootPath, "bagel/bagel_db")
dbInfo = None
with open(os.path.join(dbPath, "info.yml")) as f:
    dbInfo = yaml.load(f)
compileBagelPush = QPushButton("compile")
createBagelPush = QPushButton("create new graph")
modelVLayout.addWidget(modelsCombo)
modelVLayout.addWidget(versionsCombo)
modelVLayout.addWidget(compileBagelPush)
modelVLayout.addWidget(createBagelPush)

hLayout2 = QHBoxLayout()
hLayout2.addWidget(resetPush)
hLayout2.addWidget(startBagelPush)
hLayout2.addWidget(startMARSPush)
spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
hLayout2.addItem(spacer)
topVLayout.addLayout(hLayout2)
topVLayout.addLayout(hLayout)
vLayout.addWidget(envGroup)
vLayout.addWidget(robotGroup)
vLayout.addWidget(modelGroup)
spacer3 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
vLayout.addItem(spacer3)

def makeDir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        pass

def saveState():
    lastState = {}
    lastState["robotsFolder"] = str(robotsFolderCombo.currentText())
    lastState["robot"] = str(robotsCombo.currentText())
    lastState["envFolder"] = str(envFolderCombo.currentText())
    lastState["env"] = str(envCombo.currentText())
    lastState["model"] = str(modelsCombo.currentText())
    lastState["version"] = str(versionsCombo.currentText())
    with open("lastState.yml", "w") as f:
        f.write(yaml.dump(lastState))


def modelChanged(i):
    global dbInfo
    versionsCombo.clear()

    model = str(modelsCombo.currentText())
    for d in dbInfo["models"]:
        if d["name"] == model:
            for v in d["versions"]:
                versionsCombo.addItem(v["name"])
            break

arrSceneSuffix = ["scene", "scn", "smurf", "smurfs"]
def robotChanged(i):
    global robotsFolderCombo, robotsCombo, robotsComboPath, robotsPath, arrSceneSuffix
    folder = str(robotsFolderCombo.currentText())
    robotsCombo.clear()
    robotsComboPath = []
    for root, dirs, files in os.walk(os.path.join(robotsPath, folder)):
        for name in files:
            arrName = name.split(".")
            if len(arrName) == 2:
                if arrName[1] in arrSceneSuffix:
                    robotsCombo.addItem(name)
                    robotsComboPath.append(root)
    robotsCombo.addItem("None")
    modelsCombo.clear()
    for d in dbInfo["models"]:
        if folder in d["name"]:
            modelsCombo.addItem(d["name"])
    modelChanged(0)

def envChanged(i):
    global envFolderCombo, envCombo, envComboPath, envPath, arrSceneSuffix
    folder = str(envFolderCombo.currentText())
    envCombo.clear()
    envComboPath = []
    for root, dirs, files in os.walk(os.path.join(envPath, folder)):
        for name in files:
            arrName = name.split(".")
            if len(arrName) == 2:
                if arrName[1] in arrSceneSuffix:
                    envCombo.addItem(name)
                    envComboPath.append(root)
    envCombo.addItem("None")

def loadState():
    if os.path.isfile("lastState.yml"):
        lastState = {}
        with open("lastState.yml") as f:
            lastState = yaml.load(f)
        index = robotsFolderCombo.findText(lastState["robotsFolder"])
        if index >= 0:
            robotsFolderCombo.setCurrentIndex(index)
            robotChanged(index)
        index = robotsCombo.findText(lastState["robot"])
        if index >= 0:
            robotsCombo.setCurrentIndex(index)

        index = envFolderCombo.findText(lastState["envFolder"])
        if index >= 0:
            envFolderCombo.setCurrentIndex(index)
            envChanged(index)
        index = envCombo.findText(lastState["env"])
        if index >= 0:
            envCombo.setCurrentIndex(index)
        index = modelsCombo.findText(lastState["model"])
        if index >= 0 and index != modelsCombo.currentIndex():
            modelsCombo.setCurrentIndex(index)
            modelChanged(index)
        index = versionsCombo.findText(lastState["version"])
        if index >= 0 and index != versionsCombo.currentIndex():
            versionsCombo.setCurrentIndex(index)
    else:
        robotChanged(0)
        envChanged(0)
        #modelChanged(0)
    window.repaint()


def resetInfo(saveState_=False):
    global dbInfo
    if saveState_:
        saveState()
    with open(os.path.join(dbPath, "info.yml")) as f:
        dbInfo = yaml.load(f)
    robotsFolderCombo.clear()
    if os.path.exists(robotsPath):
        for d in os.listdir(robotsPath):
            if os.path.isdir(os.path.join(robotsPath, d)):
                robotsFolderCombo.addItem(d)
    envFolderCombo.clear()
    if os.path.exists(envPath):
        for d in os.listdir(envPath):
            if os.path.isdir(os.path.join(envPath, d)):
                envFolderCombo.addItem(d)
    loadState()

loadState()
process = None
#hLayout.addWidget(QSpacerItem())

def setConsoleCursor(c):
    cursor = c.textCursor()
    if haveQT5:
        cursor.setPosition(len(c.toPlainText()))
    else:
        cursor.setPosition(c.toPlainText().size())
    c.setTextCursor(cursor)

def printLine(line, c):
    arrLine = line.decode("utf-8", "ignore").split("\033")
    for l in arrLine:
        if len(l) > 0:
            if l[:3] == "[0m":
                l = l[3:]
                c.setTextColor(QColor("black"))
            elif l[:6] == "[32;1m":
                l = l[6:]
                c.setTextColor(QColor("#228822"))
            elif l[:6] == "[31;1m":
                l = l[6:]
                c.setTextColor(QColor("#882222"))
            elif l[:6] == "[1;34m":
                l = l[6:]
                c.setTextColor(QColor("#aa5522"))
            elif l[:10] == "[38;5;166m":
                l = l[10:]
                c.setTextColor(QColor("#aa5522"))
            c.insertPlainText(l)
            c.verticalScrollBar().setValue(
                c.verticalScrollBar().maximum())

def execute(cmd):
    global process
    global debugConsole
    #, errConsole

    setConsoleCursor(debugConsole)
    #setConsoleCursor(errConsole)

    #print "call: " + " ".join(cmd)
    #process = subprocess.Popen(" ".join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    command = " ".join(cmd) + " &"
    if "MYLD_LIBRARY_PATH" in os.environ:
        command = "DYLD_LIBRARY_PATH="+os.environ["MYLD_LIBRARY_PATH"]+" "+command
    os.system(command)

def execute2(cmd):
    global process
    global debugConsole

    setConsoleCursor(debugConsole)

    #print "call: " + " ".join(cmd)
    command = " ".join(cmd)
    if "MYLD_LIBRARY_PATH" in os.environ:
        command = "DYLD_LIBRARY_PATH="+os.environ["MYLD_LIBRARY_PATH"]+" "+command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #os.system(" ".join(cmd)  + " &")

def compileBagel():
    global modelsCombo, versionsCombo
    model = str(modelsCombo.currentText())
    version = str(versionsCombo.currentText())
    execute2(["model_to_bagel", "--modelname="+model, "--version="+version])

def createBagel():
    global robotsFolderCombo, dbInfo, dbPath, lastState
    # todo: implement add graph to database
    # find new name and version
    # create empty model
    # store it to database
    robot = str(robotsFolderCombo.currentText())
    if len(robot) <= 0:
        return
    modelName = robot
    versionName = "1.0.0"
    versionNumber = 0
    for d in dbInfo["models"]:
        if d["name"] == modelName:
            done = False
            while not done:
                done = True
                for v in d["versions"]:
                    if versionName == v["name"]:
                        versionNumber += 1
                        versionName = ("1.0.%d" % versionNumber)
                        done = False
                        break
    model = {}
    model["name"] = modelName
    model["type"] = "bagel::subgraph"
    model["domain"] = "SOFTWARE"
    model["versions"] = []
    version = {}
    version["interfaces"] = []
    config = {"interfaces": {}}
    version["maturity"] = "INPROGRESS"
    version["name"] = versionName
    model["versions"].append(version)
    found = False
    # reload dbInfo
    with open(os.path.join(dbPath, "info.yml")) as f:
        dbInfo = yaml.load(f)
    for modelInfo in dbInfo["models"]:
        if modelInfo["name"] == modelName:
            found = True
            modelInfo["versions"].append({"name": versionName})
            break
    if not found:
        modelInfo = {"name": modelName, "type": model["type"], "versions": []}
        modelInfo["versions"].append({"name": versionName})
        dbInfo["models"].append(modelInfo)
    outFolder = os.path.join(dbPath, modelName + "/" + versionName)
    makeDir(outFolder)
    outFile = os.path.join(outFolder, "model.yml")
    # write model
    with open(outFile, "w") as f:
        yaml.dump(model, f)
    # write dbinfo
    with open(os.path.join(dbPath, "info.yml"), "w") as f:
        yaml.dump(dbInfo, f)
    lastState = {}
    lastState["robotsFolder"] = str(robotsFolderCombo.currentText())
    lastState["robot"] = str(robotsCombo.currentText())
    lastState["envFolder"] = str(envFolderCombo.currentText())
    lastState["env"] = str(envCombo.currentText())
    lastState["model"] = modelName
    lastState["version"] = versionName
    with open("lastState.yml", "w") as f:
        f.write(yaml.dump(lastState))
    resetInfo(False)

def startMARS():
    global robotsFolderCombo, modelsCombo, versionsCombo, robotsCombo, envCombo, robotsPath, envPath
    global executeList
    model = str(modelsCombo.currentText())
    version = str(versionsCombo.currentText())
    robotFolder = str(robotsFolderCombo.currentText())
    robot = str(robotsCombo.currentText())
    robotIndex = robotsCombo.currentIndex()
    env = str(envCombo.currentText())
    envIndex = envCombo.currentIndex()

    scene = None
    scene2 = None
    if len(robotsComboPath) >  0 and robotIndex < len(robotsComboPath):
        scene = os.path.join(robotsComboPath[robotIndex]+"/"+robot)
    if len(envComboPath) >  0 and envIndex < len(envComboPath):
        scene2 = os.path.join(envComboPath[envIndex]+"/"+env)
    cmd = ["bash create_mars_config", "--modelname="+model, "--version="+version]
    loadScene = None
    if scene:
        if scene2:
            cmd.append("--scene="+'"'+scene+';'+scene2+'"')
        else:
            cmd.append("--scene="+'"'+scene+'"')
    elif scene2:
        cmd.append("--scene="+'"'+scene2+'"')
    else:
        cmd.append("--scene=")
    execute2(cmd)
    scriptPath = os.path.join(rootPath, "install/bin/start_mars")
    executeList.append(["python "+scriptPath, "--modelname="+model, "--version="+version])
    #execute(["mars_app", "-s", '"'+scene+';'+scene2+'"'])

def startBagel():
    global modelsCombo, versionsCombo
    model = str(modelsCombo.currentText())
    version = str(versionsCombo.currentText())
    execute(["bash xrock_gui", "model="+model, "version="+version, "domain=software", "edition=software"])


def update():
    global process, debugConsole, outConsole, executeList

    if process:
        line = process.stdout.readline()
        if len(line) == 0:
            process = None
            debugConsole.insertPlainText("\n")
            for e in executeList:
                execute(e)
            executeList = []
        else:
            printLine(line, debugConsole)


if haveQT5:
    compileBagelPush.clicked.connect(compileBagel)
    createBagelPush.clicked.connect(createBagel)
    startMARSPush.clicked.connect(startMARS)
    startBagelPush.clicked.connect(startBagel)
    resetPush.clicked.connect(resetInfo)
    modelsCombo.currentIndexChanged.connect(modelChanged)
    robotsFolderCombo.currentIndexChanged.connect(robotChanged)
    envFolderCombo.currentIndexChanged.connect(envChanged)
else:
    compileBagelPush.connect(compileBagelPush, SIGNAL("clicked()"), compileBagel)
    createBagelPush.connect(createBagelPush, SIGNAL("clicked()"), createBagel)
    startMARSPush.connect(startMARSPush, SIGNAL("clicked()"), startMARS)
    startBagelPush.connect(startBagelPush, SIGNAL("clicked()"), startBagel)
    resetPush.connect(resetPush, SIGNAL("clicked()"), resetInfo)
    modelsCombo.connect(modelsCombo, SIGNAL("currentIndexChanged(int)"), modelChanged)
    robotsFolderCombo.connect(robotsFolderCombo, SIGNAL("currentIndexChanged(int)"), robotChanged)
    envFolderCombo.connect(envFolderCombo, SIGNAL("currentIndexChanged(int)"), envChanged)

window.resize(800, 500)
window.show()

timer = QTimer()
timer.timeout.connect(update)
timer.start(20)

r = app.exec_()

saveState()
sys.exit(r)
