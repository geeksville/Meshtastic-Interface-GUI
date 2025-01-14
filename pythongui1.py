#!/usr/bin/python3
from datetime import *
import sys
import tkinter
import random
from tkinter import *
import meshtastic
from pubsub import pub
import threading
import pygame
import time
import datetime
import json
import base64

root = Tk()

txt = Text(root, bg = "black", foreground = "#FFFFFF", font = ("Sans_Serif", 10))


class RepeatedTimer(object): # Timer helper class
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False


def randchar():
	file = open('myFile.txt', 'r')
	while True:
        	rando = file.readline()
        	rando = rando.strip()
        	LoadMyEntry(txt, rando)
        	time.sleep(2)
        	print(rando)
        	if not rando:
        		break
        	interface.sendText(rando)
        	#Scroll to the bottom of chat windows
        	txt.yview(END)
	file.close()


def playsound(soundfile):
    """Play sound through default mixer channel in blocking manner.
       This will load the whole sound into memory before playback
    """    
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound(soundfile)
    clock = pygame.time.Clock()
    sound.play()
    while pygame.mixer.get_busy():
        clock.tick(1000)    
        

def LoadConnectionInfo(txt, EntryText):
    if EntryText != '':
        txt.config(state=NORMAL)
        if txt.index('end') != None:
            now = datetime.datetime.now()
            txt.insert(END, EntryText+'\n')
            LineNumber = float(txt.index('end'))-1.0            
            txt.tag_add(EntryText, LineNumber, LineNumber+1.0)
            txt.tag_config(EntryText, foreground="#FFFFFF", font = ("Sans_Serif", 10))
            txt.config(state=DISABLED)
            txt.yview(END)


def LoadMyEntry(txt, EntryText):
    if EntryText != '':
        txt.config(state=NORMAL)
        if txt.index('end') != None:
            """current_time = datetime.datetime.now().time()
            LineNumber = float(txt.index('end'))-1.0
            txt.insert(END, "\nDevice_1-> " + EntryText + "\t\t" + str(current_time))
            txt.tag_add("Device_1->", LineNumber, LineNumber+1.0)
            txt.tag_config("Device_1->", foreground="#FF8000", font=("Arial", 14, "bold"))
            txt.config(state=DISABLED)
            txt.yview(END)"""

def LoadOtherEntry(txt, EntryText, value):
    if EntryText != '':
        txt.config(state=NORMAL)
        if txt.index('end') != None:
            if value == 0:
            	dev = "Device_1->"
            	color = "#FF8000"
            else:
            	dev = "Device_2->"
            	color = "#32CD32"
            LineNumber = float(txt.index('end'))-1.0 
            txt.insert(END, "\n" + dev + EntryText)
            txt.tag_add(dev, LineNumber, LineNumber+1.0)
            txt.tag_config(dev, foreground=color, font=("Arial", 14, "bold"))
            txt.config(state=DISABLED)
            txt.yview(END)
            

def onReceive(packet, interface): # called when a packet arrives
  #print("Received: "+str(packet))
  try:
  	size = sys.getsizeof(packet['decoded']['payload'])
  	fromid = (packet['fromId'])
  	data = (packet['decoded']['payload']).decode('utf-8')
  except Exception as ex:
    print(ex)
  	data = (packet).decode('utf-8')
  
  data = str(data)
  
  try:
  	value = (packet['rxSnr'])
  except:
  	value = 0
  	
  #Write message to chat window
  LoadOtherEntry(txt, data, value)
  	
  input_dict = {'data': data, 'size': size, 'fromId': fromid, 'Time_stamp': str(datetime.datetime.now().time())}
  result = []
  for data, size in input_dict.items():
    result.append({'Size': size, 'Data': data})
  
  playsound("/home/arijit/meshtasticGUI/notif.wav")

  #Scroll to the bottom of chat windows
  txt.yview(END)
  

    
  """data = json.dumps(data, indent = 2).encode('utf-8')
  data = data.encode('ascii')
  base64_bytes = base64.b64encode(data)
  packet = base64_bytes.decode('ascii')
  packet = base64.b64encode(packet)
  data = json.dumps(packet, indent = 2)"""
  
  new = open('/home/arijit/meshtasticGUI/new.json', "a")
  new.write(json.dumps(result))
  new.close()


def onConnection(interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
   LoadConnectionInfo(txt,"\nStarting..")
   time.sleep(2)
   LoadConnectionInfo(txt,"Connection established Successfully\nStart Communicating..")

def timer(x):
    if x != 3:
        print("starting random messages...")
        randchar()
       	#rt = RepeatedTimer(10,randchar)

        
def stop():
    LoadConnectionInfo(txt, "\n\nConnection is closing now..")
    timer(3)
    interface.close()
    time.sleep(2)
    LoadConnectionInfo(txt, "Disconnected now..")


def send():
    
    EntryText = e.get()
    #Erase previous message in Entry Box
    e.delete('0',END)
    # Loading the message on the chat window
    LoadMyEntry(txt, EntryText)
    #Scroll to the bottom of chat windows
    txt.yview(END)
               
    #Send my mesage to all others
    interface.sendText(EntryText)

def true():
    timer(1)

def exit():
    root.destroy()

def PressAction(event):
	e.config(state=NORMAL)
	send()

def DisableEntry(event):
	e.config(state=DISABLED)

root.configure(background = "White")
root.title("MeshtasticGUI") #"tk" is replaced with "Meshtastic"
img = tkinter.Image("photo", file="/home/arijit/meshtasticGUI/41zvoDg7HlL.png")
root.tk.call('wm','iconphoto',root._w, img)
#root.iconbitmap(r"@/home/arijit/Documents/M.Tech Final Year Project/code/41zvoDg7HlL.xbm")
txt.grid(row=0,column=0,columnspan = 5) #line txt for increasing text area
e = Entry(root,width = 50)
pub.subscribe(onConnection, "meshtastic.connection.established")
#start = Button(root,text = "START",command = subscribe).grid(row = 1,column = 2)
stop = Button(root,text = "STOP",command = stop).grid(row = 1,column = 2)
sent = Button(root,text = "SEND",command = send).grid(row = 1,column = 1)
e.bind("<Return>", DisableEntry)
e.bind("<KeyRelease-Return>", PressAction)
randomchar = Button(root,text = "RAND",command = true).grid(row = 1,column = 3)
exit = Button(root,text = "EXIT",command = exit).grid(row = 1,column = 4)
e.grid(row = 1,column = 0)
pub.subscribe(onReceive, "meshtastic.receive")# By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
interface = meshtastic.SerialInterface()
root.mainloop()
