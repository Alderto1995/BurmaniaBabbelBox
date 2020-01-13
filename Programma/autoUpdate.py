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

os.system("cp /home/pi/BurmaniaBabbelbox/Programma/recordaudio.py /home/pi/BurmaniaBabbelbox/Programma/recordaudio")
os.system("chmod a+x /home/pi/BurmaniaBabbelbox/Programma/recordaudio")
os.system("sudo mv /home/pi/BurmaniaBabbelbox/Programma/recordaudio /usr/bin/ ")


os.system("cp /home/pi/BurmaniaBabbelbox/Programma/autoUpdate.py /home/pi/BurmaniaBabbelbox/Programma/autoUpdate")
os.system("chmod a+x /home/pi/BurmaniaBabbelbox/Programma/autoUpdate")
os.system("sudo mv /home/pi/BurmaniaBabbelbox/Programma/autoUpdate /usr/bin/ ")
print("Klaar")
#Change it to good directory
#sudo mv /home/pi/Programma_bestanden/recordaudio /usr/bin/ 

