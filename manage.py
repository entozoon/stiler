#!/usr/bin/python
import sys
import os
import commands
import pickle

BottomPadding = 0
TopPadding = 0
LeftPadding = 0
RightPadding = 0
WinTitle = 21
WinBorder = 1
TempFile = "/tmp/tile_winlist"
MwFactor = 0.5

def initialize():
    desk_output = commands.getoutput("wmctrl -d").split("\n")
    desk_list = [line.split()[0] for line in desk_output]

    current =  filter(lambda x: x.split()[1] == "*" , desk_output)[0].split()

    desktop = current[0]
    width =  current[8].split("x")[0]
    height =  current[8].split("x")[1]
    orig_x =  current[7].split(",")[0]
    orig_y =  current[7].split(",")[1]

    win_output = commands.getoutput("wmctrl -lG").split("\n")
    win_list = {}


    for desk in desk_list:
        win_list[desk] = map(lambda y: hex(int(y.split()[0],16)) , filter(lambda x: x.split()[1] == desk, win_output ))


    return (desktop,orig_x,orig_y,width,height,win_list)


def get_active_window():
    return str(hex(int(commands.getoutput("xdotool getactivewindow").split()[0])))
    

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


 

(Desktop,OrigXstr,OrigYstr,MaxWidthStr,MaxHeightStr,WinList) = initialize()
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

def move_active(PosX,PosY,Width,Height):
  command =  " wmctrl -r :ACTIVE: -e 0," + str(PosX) + "," + str(PosY)+ "," + str(Width) + "," + str(Height)
  os.system(command)

def move_window(windowid,PosX,PosY,Width,Height):
  command =  " wmctrl -i -r " + windowid +  " -e 0," + str(PosX) + "," + str(PosY)+ "," + str(Width) + "," + str(Height)
  os.system(command)
  command = "wmctrl -i -r " + windowid + " -b remove,hidden,shaded"
  os.system(command)

def left():
    Width=MaxWidth/2-1
    Height=MaxHeight
    PosX=0
    PosY=0
    move_active(PosX,PosY,Width,Height)

def right():
    Width=MaxWidth/2-1
    Height=MaxHeight
    PosX=MaxWidth/2
    PosY=0
    move_active(PosX,PosY,Width,Height)
    
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


if sys.argv[1] == "left":
    left()
elif sys.argv[1] == "right":
    right()
elif sys.argv[1] == "simple":
    simple()
elif sys.argv[1] == "swap":
    swap()


