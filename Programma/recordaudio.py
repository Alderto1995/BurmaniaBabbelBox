#!/usr/bin/python 
               
#import programs
import pyaudio
import wave 
import os
import sys
import select
import random
import string
import time
import pygame
import errno
import RPi.GPIO as GPIO
import threading
from threading import Event
from contextlib import contextmanager
try:
    import httplib
except:
    import http.clien as httplib


class exit_thread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        time_buttons_pressed = 0
        while True:
            time.sleep(0.3)
            yellow_button = GPIO.input(yellowButtonPin)
            blue_button = GPIO.input(blueButtonPin)
            if time_buttons_pressed > 10:
                time_buttons_pressed = 0
                shut_down_raspberry()
            elif yellow_button == False and blue_button == False:
                time_buttons_pressed += 0.3
            else:
                time_buttons_pressed = 0
                
def shut_down_raspberry():
    GPIO.output(greenLedPin, GPIO.HIGH)
    GPIO.output(yellowLedPin, GPIO.HIGH)
    GPIO.output(redLedPin, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(greenLedPin, GPIO.LOW)
    GPIO.output(yellowLedPin, GPIO.LOW)
    GPIO.output(redLedPin, GPIO.LOW)
    from subprocess import call
    call("sudo shutdown -h now", shell=True)


#Thread voor de tijd bij te houden hoelang er is opgenomen
class timeThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        ShowTimeRecorded()
        
    def stop(self):
        exitTimer.set()   
        
    #Laat de tijd zien die is opgenomen
def ShowTimeRecorded():
    recordedTime = 0
    while not exitTimer.is_set():
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconden opgenomen.".format(recordedTime))
        sys.stdout.flush()
        exitTimer.wait(1)
        recordedTime += 1
     
                 
#Thread die een keer in de zoveel keer welkom zegt
class WelkomThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        exitWelkom.wait(tijdTussenWelkomHeten)
        while not exitWelkom.is_set():
            if GPIO.input(bewegingsSensorPin):
                playRandomSound('Welkom')
                exitWelkom.wait(tijdTussenWelkomHeten)
            else:
                exitWelkom.wait(1) 
                
    def stop(self):
        exitWelkom.set()
        os.system("killall aplay")
                
        
#Speel een Random fragment
def playRandomSound(folder):
    path_sound = pathResources + folder + '/'
    list_sounds = os.listdir(path_sound)
    index = random.randrange(0, len(list_sounds))
    filename = list_sounds[index]
    play_command = 'aplay -q '+ '"' + path_sound+filename+'"'
    if folder == 'Bedankt':
        play_command += ' &'
    os.system(play_command)
    return filename
            
#Create random String, so no duplicates are made                
def randomString(stringLength=7):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
  
#record the audio  
def recordAudio(chunk, frames):
    stop = False
    while True:      
        data = stream.read(chunk)
        frames.append(data)
        if stop == True:
            break
        #wait for enter press, then break recording
        buttonYellow = GPIO.input(yellowButtonPin)
        buttonBlue = GPIO.input(blueButtonPin)
        if buttonYellow == False:
            stop = True
        if buttonBlue == False:
            stop = True

#De Methode die steeds het scherm schrijft aan de hand van de status       
def PaintScreen(status):
    ClearScreen()
    if status == "NaamIngeven":
        print("Welkom bij de Burmania Babbelbox")
        print("Wat is je naam?")
    elif status == "KeuzeIngeven":
        print("Druk op de gele knop om een vraag te beantwoorden")
        print("Druk op de blauwe knop om een verhaal te vertellen")
        print("Hierna begint het opnemen automatisch")
    elif status == "Vraagvertellen":
        print("Luister goed!")
    elif status == "Opnemen":
        print("Er wordt opgenomen!")
        print("Vertel je verhaal!\n")
        print("Druk op [enter] om te stoppen met opnemen")
    elif status == "VraagInspreken":
        print("Welke vraag wil je inspreken?")
    elif status == "Bedankt":
        print("Bedankt voor je verhaal!\n")
        print("Opslaan, eventjes geduld....")
    elif status == "Oeps":
        print("Oeps iets is missgegaan, probeer het nog eens")

#Maak het scherm leeg
def ClearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')  
   
#Als er geen map is, maak die dan
def CreatFolderIfNotExcist(FilePath):
    try:
        os.makedirs(FilePath)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise 
            
#check internet connection
def checkInternetConnection():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False
        
#upload everythong to drive    
def uploadToDrive(wav_output_filename, VraagWithoutExtension, keuze):
    if keuze == KeuzeRandomVraag:
        google_drive_Upload_Command = "rclone move " + wav_output_filename + ' "'+"babbelbox:/2020 StudioBurBus/BabbelBox/Antwoorden/" + VraagWithoutExtension+ '"'
    elif keuze == KeuzeEigenVerhaal:
        google_drive_Upload_Command = "rclone move " + wav_output_filename + ' "'+"babbelbox:/2020 StudioBurBus/BabbelBox/Verhalen/" + '"' 
    elif keuze == KeuzeVraagInspreken:
        google_drive_Upload_Command = "rclone copy " + wav_output_filename + ' "'+"babbelbox:/2020 StudioBurBus/BabbelBox/Vragen/" + '"'
    google_drive_Upload_Command = google_drive_Upload_Command + path_config_file
    os.system(google_drive_Upload_Command)

 
  
#Alle Variabbelen 
form_1 = pyaudio.paInt16    # 16-bit resolution
chans = 1                   # 1 channel
samp_rate = 44100           # 44kHz sampling rate
chunk = 4096                # 2^12 samples for buffer
dev_index = 2               # device index found by p.get_device_info_by_index(ii)
KeuzeRandomVraag = '1'      #De toets om een random vraag te beantwoorden
KeuzeEigenVerhaal = '2'     #De toets voor je eigen verhaal in te spreken
KeuzeVraagInspreken = '5'   #De toets om een nieuwe vraag in te stellen
tijdTussenWelkomHeten = 20  #De eerste keer duurt het wat langer voordat je welkom wordt geheten
bewegingsSensorPin = 26     #De pin voor de beweginssensor
yellowButtonPin = 32
blueButtonPin = 36
greenLedPin = 11
yellowLedPin = 13
redLedPin = 15
exitWelkom = Event()
exitTimer = Event()
pathResources = '/home/pi/BurmaniaBabbelBox/Resources/'
pathOpnames = '/home/pi/BurmaniaBabbelBox/Opnames/'
path_config_file = " --config /home/pi/.config/rclone/rclone.conf"

#Instellingen goedzetten
GPIO.setmode(GPIO.BOARD)
GPIO.setup(bewegingsSensorPin, GPIO.IN)
GPIO.setup(yellowButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(blueButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(greenLedPin,GPIO.OUT)
GPIO.setup(yellowLedPin,GPIO.OUT)
GPIO.setup(redLedPin,GPIO.OUT)
os.system('amixer cset numid=3 1') 
os.system("amixer sset 'PCM' 100%")
Exit_thread = exit_thread()
Exit_thread.start()



#De main loop waar je nooit uitkomt
while True: 
    try:
        exitWelkom.clear()
        exitTimer.clear()
        GPIO.output(greenLedPin, GPIO.HIGH)
        welkomThread = WelkomThread()
        welkomThread.start()
        naam_Opnemer = ""
        frames = []
        keuze = ""
        VraagWithoutExtension = ""
        waitForKeuze = True
        ClearScreen()
        PaintScreen("KeuzeIngeven")
        #Wachten op een keuze
        while waitForKeuze == True:
            time.sleep(0.1)
            buttonYellow = GPIO.input(yellowButtonPin)
            buttonBlue = GPIO.input(blueButtonPin)
            if buttonYellow == False:
                keuze = KeuzeRandomVraag
                waitForKeuze = False
            if buttonBlue == False:
                keuze = KeuzeEigenVerhaal
                waitForKeuze = False
        
        GPIO.output(greenLedPin, GPIO.LOW)

        naam_opnemer_random = randomString() 
        
        welkomThread.stop()
        welkomThread.join()
        
        #Handelen aan de hand van de verschillende keuzes die gemaakt zijn
        if keuze == KeuzeRandomVraag:        #beantwoord een random vraag
            PaintScreen("Vraagvertellen")
            Vraag = playRandomSound('Vragen')
            VraagWithoutExtension = os.path.splitext(Vraag)[0]
            FileFolder = pathOpnames + VraagWithoutExtension+"/" 
            CreatFolderIfNotExcist(FileFolder)
            wav_output_filename = FileFolder + naam_opnemer_random + ".wav"
        elif keuze == KeuzeEigenVerhaal:      #vertel een verhaal
            wav_output_filename = pathOpnames+ naam_opnemer_random + ".wav" 
            time.sleep(0.5)
        elif keuze == KeuzeVraagInspreken:      #spreek een vraag in
            PaintScreen("VraagInspreken")
            intesprekenVraag = raw_input()
            intesprekenVraag_Underscore = intesprekenVraag.replace(" ", "_")
            wav_output_filename = pathResources+"Vragen/" + intesprekenVraag_Underscore+ "_"+ randomString() +".wav"
        
        #create listening stream
        audio = pyaudio.PyAudio() # create pyaudio instantiation
        stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = dev_index,input = True, \
                            frames_per_buffer=chunk)
        
        #Begin met opnemen, en start de thread met de tijd dat er opgenomen is
        PaintScreen("Opnemen")
        tijdThread = timeThread()
        tijdThread.start()
        GPIO.output(yellowLedPin, GPIO.HIGH)     
        
        recordAudio(chunk, frames)
        tijdThread.stop()
        tijdThread.join()
        
        # stop the stream, close it, and terminate the pyaudio instantiation
        PaintScreen("Bedankt")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        GPIO.output(yellowLedPin, GPIO.LOW)
        # save the audio frames as .wav file
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()
        #if internet connection, then save to drive
        GPIO.output(redLedPin, GPIO.HIGH)
        if checkInternetConnection():
            playRandomSound('Bedankt')
            uploadToDrive(wav_output_filename, VraagWithoutExtension, keuze)
        GPIO.output(redLedPin, GPIO.LOW)  
        ClearScreen()
    except:
        ClearScreen()
        PaintScreen("Oeps")
        GPIO.output(greenLedPin, GPIO.HIGH)
        GPIO.output(yellowLedPin, GPIO.HIGH)
        GPIO.output(redLedPin, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(greenLedPin, GPIO.LOW)
        GPIO.output(yellowLedPin, GPIO.LOW)
        GPIO.output(redLedPin, GPIO.LOW)
    
    
    #ToDo:
    #-Check if writing  the file is possible to change, not writing to an array but to an file
    #-Delete error messages for creating audio stream
