#!/usr/bin/python 

import os

#Download newest record audio
#print("Programma Bestanden ophalen")
#os.system("rclone copy babbelbox:/2020/Babbelbox/Programma_bestanden/  /home/pi/BurmaniaBabbelbox/Programma/")
#print("Bestanden zijn binnen")

#Download newest question
#print("Vragen ophalen!")
#os.system("rclone copy" +'" ' +"babbelbox:/2020 StudioBurBus/Babbelbox/Vragen/  /home/pi/BurmaniaBabbelbox/Resources/Vragen" + '"')
#print("Vragen zijn binnen")

#Make it compile
babbelBoxLocation = '/home/pi/BurmaniaBabbelBox/Programma/'

os.system("cp " + babbelBoxLocation + "recordaudio.py " + babbelBoxLocation + "recordaudio")
os.system("chmod a+x " + babbelBoxLocation + "recordaudio")
os.system("sudo mv " + babbelBoxLocation + "recordaudio /usr/bin/ ")


os.system("cp " + babbelBoxLocation + "autoUpdate.py " + babbelBoxLocation + "autoUpdate")
os.system("chmod a+x " + babbelBoxLocation + "autoUpdate")
os.system("sudo mv " + babbelBoxLocation + "autoUpdate /usr/bin/ ")
print("Klaar")
#Change it to good directory
#sudo mv /home/pi/Programma_bestanden/recordaudio /usr/bin/ 

