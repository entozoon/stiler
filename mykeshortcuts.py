#!/usr/bin/python
#                            MYKEMODS FOR DAYZ
############################################################################
# Based on https://github.com/nsrinath/stiler                              #
# Which is a fork of https://github.com/TheWanderer/stiler                 #
# And the menu opening from http://askubuntu.com/a/661766                  #
############################################################################

import sys
import os
import commands
import pickle
import ConfigParser
import subprocess
import time

def get_mousepos():
    cursordata = subprocess.check_output(["xdotool", "getmouselocation"]).decode("utf-8").split()
    return [d.split(":")[1] for d in cursordata[:2]]

def initconfig():
    rcfile=os.getenv('HOME')+"/.mykeshortcutsrc"
    if not os.path.exists(rcfile):
        cfg=open(rcfile,'w')
        cfg.write("""#Tweak these values
[default]
BottomPadding = 0
TopPadding = 0
LeftPadding = 0
RightPadding = 0
WinTitle = 21
WinBorder = 1
MwFactor = 0.65
TempFile = /tmp/tile_winlist
""")
        cfg.close()

    config=ConfigParser.RawConfigParser()
    config.read(rcfile)
    return config


def initialize():
    desk_output = commands.getoutput("wmctrl -d").split("\n")
    desk_list = [line.split()[0] for line in desk_output]

    current =  filter(lambda x: x.split()[1] == "*" , desk_output)[0].split()
    desktop = current[0]
    width =  current[8].split("x")[0]
    height =  current[8].split("x")[1]
    orig_x =  current[7].split(",")[0]
    orig_y =  current[7].split(",")[1]

    resolutionX = int(current[3].split("x")[0])
    resolutionY = int(current[3].split("x")[1])

    win_output = commands.getoutput("wmctrl -lG").split("\n")
    win_list = {}

    for desk in desk_list:
        win_list[desk] = map(lambda y: hex(int(y.split()[0],16)) , filter(lambda x: x.split()[1] == desk, win_output ))

    return (desktop,orig_x,orig_y,width,height,win_list, resolutionX, resolutionY)


def get_active_window():
    return str(hex(int(commands.getoutput("xdotool getactivewindow 2>/dev/null").split()[0])))


def store(object,file):
    with open(file, 'w') as f:
        pickle.dump(object,f)
    f.close()


def retrieve(file):
    try:
        with open(file,'r+') as f:
            obj = pickle.load(f)
        f.close()
        return(obj)
    except:
        f = open(file,'w')
        f.close
        dict = {}
        return (dict)


# Get all global variables
Config = initconfig()
BottomPadding = Config.getint("default","BottomPadding")
TopPadding = Config.getint("default","TopPadding")
LeftPadding = Config.getint("default","LeftPadding")
RightPadding = Config.getint("default","RightPadding")
WinTitle = Config.getint("default","WinTitle")
WinBorder = Config.getint("default","WinBorder")
MwFactor = Config.getfloat("default","MwFactor")
TempFile = Config.get("default","TempFile")
(Desktop,OrigXstr,OrigYstr,MaxWidthStr,MaxHeightStr,WinList, resolutionX, resolutionY) = initialize()
MaxWidth = int(MaxWidthStr) - LeftPadding - RightPadding
MaxHeight = int(MaxHeightStr) - TopPadding - BottomPadding
OrigX = int(OrigXstr) + LeftPadding
OrigY = int(OrigYstr) + TopPadding
OldWinList = retrieve(TempFile)


def get_simple_tile(wincount):
    rows = wincount - 1
    layout = []
    if rows == 0:
        layout.append((OrigX,OrigY,MaxWidth,MaxHeight-WinTitle-WinBorder))
        return layout
    else:
        layout.append((OrigX,OrigY,int(MaxWidth*MwFactor),MaxHeight-WinTitle-WinBorder))

    x=OrigX + int((MaxWidth*MwFactor)+(2*WinBorder))
    width=int((MaxWidth*(1-MwFactor))-2*WinBorder)
    height=int(MaxHeight/rows - WinTitle-WinBorder)

    for n in range(0,rows):
        y= OrigY+int((MaxHeight/rows)*(n))
        layout.append((x,y,width,height))

    return layout


def get_vertical_tile(wincount):
    layout = []
    y = OrigY
    width = int(MaxWidth/wincount)
    height = MaxHeight - WinTitle - WinBorder
    for n in range(0,wincount):
        x= OrigX + n * width
        layout.append((x,y,width,height))

    return layout


def get_horiz_tile(wincount):
    layout = []
    x = OrigX
    height = int(MaxHeight/wincount - WinTitle - WinBorder)
    width = MaxWidth
    for n in range(0,wincount):
        y= OrigY + int((MaxHeight/wincount)*(n))
        layout.append((x,y,width,height))

    return layout

def get_max_all(wincount):
    layout = []
    x = OrigX
    y = OrigY
    height = MaxHeight - WinTitle - WinBorder
    width = MaxWidth
    for n in range(0,wincount):
        layout.append((x,y,width,height))

    return layout





def move_active(PosX,PosY,Width,Height):
    command =  " wmctrl -r :ACTIVE: -e 0," + str(PosX) + "," + str(PosY)+ "," + str(Width) + "," + str(Height)
    os.system(command)


def move_window(windowid,PosX,PosY,Width,Height):
    command =  " wmctrl -i -r " + windowid +  " -e 0," + str(PosX) + "," + str(PosY)+ "," + str(Width) + "," + str(Height)
    os.system(command)
    command = "wmctrl -i -r " + windowid + " -b remove,hidden,shaded"
    os.system(command)


def raise_window(windowid):
    if windowid == ":ACTIVE:":
        command = "wmctrl -r :ACTIVE: -b remove,shaded && wmctrl -a :ACTIVE: "
    else:
        command - "wmctrl -i -a " + windowid

    os.system(command)

def min_window(windowid):
    if windowid == ":ACTIVE:":
        command = "wmctrl -r :ACTIVE: -b add,shaded"
    else:
        command = "wmctrl -i -r " + windowid + " -b add,shaded"
        #command = "wmctrl -i -r " + windowid + " -b toggle,hidden" #does nothing?
        #command = "wmctrl -i -r " + windowid + " -b add,minimized"
        #I've thought of a better command, wmctrl -k on
    os.system(command)

def left():
    Width=MaxWidth/2-1
    Height=MaxHeight - WinTitle -WinBorder
    PosX=LeftPadding
    PosY=TopPadding
    move_active(PosX,PosY,Width,Height)
    raise_window(":ACTIVE:")


def right():
    Width=MaxWidth/2-1
    Height=MaxHeight - WinTitle - WinBorder
    PosX=MaxWidth/2
    PosY=TopPadding
    move_active(PosX,PosY,Width,Height)
    raise_window(":ACTIVE:")


def compare_win_list(newlist,oldlist):
    templist = []
    for window in oldlist:
        if newlist.count(window) != 0:
            templist.append(window)
    for window in newlist:
        if oldlist.count(window) == 0:
            templist.append(window)
    return templist


def create_win_list():
    Windows = WinList[Desktop]

    if OldWinList == {}:
        pass
    else:
        OldWindows = OldWinList[Desktop]
        if Windows == OldWindows:
            pass
        else:
            Windows = compare_win_list(Windows,OldWindows)

    return Windows


def arrange(layout,windows):
    for win , lay  in zip(windows,layout):
        move_window(win,lay[0],lay[1],lay[2],lay[3])
    WinList[Desktop]=windows
    store(WinList,TempFile)


def simple():
    Windows = create_win_list()
    arrange(get_simple_tile(len(Windows)),Windows)


def swap():
    winlist = create_win_list()
    active = get_active_window()
    winlist.remove(active)
    winlist.insert(0,active)
    arrange(get_simple_tile(len(winlist)),winlist)


def vertical():
    winlist = create_win_list()
    active = get_active_window()
    winlist.remove(active)
    winlist.insert(0,active)
    arrange(get_vertical_tile(len(winlist)),winlist)


def horiz():
    winlist = create_win_list()
    active = get_active_window()
    winlist.remove(active)
    winlist.insert(0,active)
    arrange(get_horiz_tile(len(winlist)),winlist)


def cycle():
    winlist = create_win_list()
    winlist.insert(0,winlist[len(winlist)-1])
    winlist = winlist[:-1]
    arrange(get_simple_tile(len(winlist)),winlist)


def maximize():
    Width=MaxWidth
    Height=MaxHeight - WinTitle -WinBorder
    PosX=LeftPadding
    PosY=TopPadding
    move_active(PosX,PosY,Width,Height)
    raise_window(":ACTIVE:")

def minimize():
    winlist = create_win_list()
    active = get_active_window()
    min_window(active)

def max_all():
    winlist = create_win_list()
    active = get_active_window()
    winlist.remove(active)
    winlist.insert(0,active)
    arrange(get_max_all(len(winlist)),winlist)

def min_or_max_all():
    #winlist = create_win_list()
    #for window in winlist:
    #    min_window(window)
    # thought of a way better way! ::
    command = "wmctrl -m"
    #result = os.system(command)
    result = subprocess.check_output(command, shell=True)
    #print(result)
    if ("desktop\" mode: OFF" in result):
        command = "wmctrl -k on" # minimize everything
    else:
        command = "wmctrl -k off" # maximise everything
    os.system(command)

# Menu button toggle open/close
def menu():
    menuButtonX = 1
    menuButtonY = resolutionY - 1
    coords = str(menuButtonX) + " " + str(menuButtonY)

    cmd1 = "xdotool mousemove "+coords
    cmd2 = "xdotool click 1"
    cmd3 = "xdotool mousemove "+(" ").join(get_mousepos())
    for cmd in [cmd1, cmd2, cmd3]:
        subprocess.Popen(["/bin/bash", "-c", cmd])
        time.sleep(0.05)

if len(sys.argv) <= 1:
    print("You must give an argument, e.g. min_or_max_all or menu")
elif sys.argv[1] == "left":
    left()
elif sys.argv[1] == "right":
    right()
elif sys.argv[1] == "simple":
    simple()
elif sys.argv[1] == "vertical":
    vertical()
elif sys.argv[1] == "horizontal":
    horiz()
elif sys.argv[1] == "swap":
    swap()
elif sys.argv[1] == "cycle":
    cycle()
elif sys.argv[1] == "maximize":
    maximize()
elif sys.argv[1] == "minimize":
    minimize()
elif sys.argv[1] == "max_all":
    max_all()
elif sys.argv[1] == "min_or_max_all":
    min_or_max_all()
elif sys.argv[1] == "menu":
    menu()
else:
    print("Unknown stiler command")