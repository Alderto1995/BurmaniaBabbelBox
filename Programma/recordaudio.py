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


class ExitThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        time_buttons_pressed = 0
        while True:
            time.sleep(0.3)
            yellow_button = GPIO.input(yellow_button_pin)
            blue_button = GPIO.input(blue_button_pin)
            if time_buttons_pressed > 10:
                time_buttons_pressed = 0
                shut_down_raspberry()
            elif yellow_button == False and blue_button == False:
                time_buttons_pressed += 0.3
            else:
                time_buttons_pressed = 0
                
def shut_down_raspberry():
    turn_on_all_led()
    from subprocess import call
    call("sudo shutdown -h now", shell=True)


#Thread voor de tijd bij te houden hoelang er is opgenomen
class TimeThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        show_time_recorded()
        
    def stop(self):
        exit_timer.set()   
        
    #Laat de tijd zien die is opgenomen
def show_time_recorded():
    recorded_time = 0
    while not exit_timer.is_set():
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconden opgenomen.".format(recorded_time))
        sys.stdout.flush()
        exit_timer.wait(1)
        recorded_time += 1
     
                 
#Thread die een keer in de zoveel keer welkom zegt
class WelcomeThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        exit_welcome.wait(time_between_saying_welcome)
        while not exit_welcome.is_set():
            if GPIO.input(movement_sensor_pin):
                play_random_sound('Welkom')
                exit_welcome.wait(time_between_saying_welcome)
            else:
                exit_welcome.wait(1) 
                
    def stop(self):
        exit_welcome.set()
        os.system("killall aplay")
        
                
        
#Speel een Random fragment
def play_random_sound(folder):
    path_sound = path_resources + folder + '/'
    list_sounds = os.listdir(path_sound)
    index = random.randrange(0, len(list_sounds))
    filename = list_sounds[index]
    play_command = 'aplay -q '+ '"' + path_sound+filename+'"'
    if folder == 'Bedankt':
        play_command += ' &'
    os.system(play_command)
    return filename
            
#Create random String, so no duplicates are made                
def create_random_string(string_length=7):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))
  
#record the audio  
def record_audio(chunk, frames):
    stop = False
    while True:      
        data = stream.read(chunk)
        frames.append(data)
        if stop == True:
            break
        #wait for enter press, then break recording
        button_yellow = GPIO.input(yellow_button_pin)
        button_blue = GPIO.input(blue_button_pin)
        if button_yellow == False:
            stop = True
        if button_blue == False:
            stop = True

#De Methode die steeds het scherm schrijft aan de hand van de status       
def paint_screen(status):
    clear_screen()
    if status == "NaamIngeven":
        print("Welkom bij de Burmania Babbelbox")
        print("Wat is je naam?")
    elif status == "KeuzeIngeven":
        print("Druk op de gele knop om een vraag te beantwoorden")
        print("Druk op de blauwe knop om een verhaal te vertellen")
        print("Hierna begint het opnemen automatisch")
    elif status == "vraagvertellen":
        print("Luister goed!")
    elif status == "Opnemen":
        print("Er wordt opgenomen!")
        print("Vertel je verhaal!\n")
        print("Druk op [enter] om te stoppen met opnemen")
    elif status == "vraaginspreken":
        print("Welke vraag wil je inspreken?")
    elif status == "Bedankt":
        print("Bedankt voor je verhaal!\n")
        print("Opslaan, eventjes geduld....")
    elif status == "Oeps":
        print("Oeps iets is missgegaan, probeer het nog eens")

#Maak het scherm leeg
def clear_screen():
    print("clearsceen")
    #os.system('cls' if os.name == 'nt' else 'clear')  

def turn_on_all_led():
    GPIO.output(green_led_pin, GPIO.HIGH)
    GPIO.output(yellow_led_pin, GPIO.HIGH)
    GPIO.output(red_led_pin, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(green_led_pin, GPIO.LOW)
    GPIO.output(yellow_led_pin, GPIO.LOW)
    GPIO.output(red_led_pin, GPIO.LOW)
   
#Als er geen map is, maak die dan
def create_folder_if_not_exicst(FilePath):
    try:
        os.makedirs(FilePath)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise 
            
#check internet verbinding
def check_internet_connection():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False
        
#upload alles naar google drive   
def upload_to_drive(wav_output_filename, question_without_extension, choice):
    if choice == choice_random_question:
        google_drive_upload_command = "rclone move " + wav_output_filename + ' "'+"babbelbox:/2020 StudioBurBus/BabbelBox/Antwoorden/" + question_without_extension+ '"'
    elif choice == choice_tell_story:
        google_drive_upload_command = "rclone move " + wav_output_filename + ' "'+"babbelbox:/2020 StudioBurBus/BabbelBox/Verhalen/" + '"' 
    elif choice == choice_ask_question:
        google_drive_upload_command = "rclone copy " + wav_output_filename + ' "'+"babbelbox:/2020 StudioBurBus/BabbelBox/Vragen/" + '"'
    google_drive_upload_command = google_drive_upload_command + path_config_file
    os.system(google_drive_upload_command)

 
  
#Alle Variabbelen 
form_1 = pyaudio.paInt16    # 16-bit resolution
chans = 1                   # 1 channel
samp_rate = 44100           # 44kHz sampling rate
chunk = 4096         # 2^12 samples for buffer
dev_index = 2               # device index found by p.get_device_info_by_index(ii)
choice_random_question = '1'      #De toets om een random vraag te beantwoorden
choice_tell_story = '2'     #De toets voor je eigen verhaal in te spreken
choice_ask_question = '5'   #De toets om een nieuwe vraag in te stellen
time_between_saying_welcome = 20  #De eerste keer duurt het wat langer voordat je welkom wordt geheten
movement_sensor_pin = 26     #De pin voor de beweginssensor
yellow_button_pin = 32
blue_button_pin = 36
green_led_pin = 11
yellow_led_pin = 13
red_led_pin = 15
exit_welcome = Event()
exit_timer = Event()
path_resources = '/home/pi/BurmaniaBabbelBox/Resources/'
path_recordings = '/home/pi/BurmaniaBabbelBox/Opnames/'
path_config_file = " --config /home/pi/.config/rclone/rclone.conf"

#Instellingen goedzetten
GPIO.setmode(GPIO.BOARD)
GPIO.setup(movement_sensor_pin, GPIO.IN)
GPIO.setup(yellow_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(blue_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(green_led_pin,GPIO.OUT)
GPIO.setup(yellow_led_pin,GPIO.OUT)
GPIO.setup(red_led_pin,GPIO.OUT)
os.system('amixer cset numid=3 1') 
os.system("amixer sset 'PCM' 100%")
exit_thread = ExitThread()
exit_thread.start()



#De main loop waar je nooit uitkomt
while True: 
    try:
        exit_welcome.clear()
        exit_timer.clear()
        GPIO.output(green_led_pin, GPIO.HIGH)
        welcome_thread = WelcomeThread()
        welcome_thread.start()
        frames = []
        choice = ""
        question_without_extension = ""
        file_name_recording = ""
        wait_for_choice= True
        clear_screen()
        paint_screen("KeuzeIngeven")
        #Wachten op een keuze
        while wait_for_choice== True:
            time.sleep(0.1)
            yellow_button = GPIO.input(yellow_button_pin)
            blue_button = GPIO.input(blue_button_pin)
            if yellow_button == False and blue_button == False:
                wait_for_choice = True
            elif yellow_button == False:
                choice= choice_random_question
                wait_for_choice= False
            elif blue_button == False:
                choice= choice_tell_story
                wait_for_choice= False
        
        GPIO.output(green_led_pin, GPIO.LOW)

        file_name_recording = create_random_string() 
        
        welcome_thread.stop()
        welcome_thread.join()
        
        #Handelen aan de hand van de verschillende keuzes die gemaakt zijn
        if choice== choice_random_question:        #beantwoord een random vraag
            paint_screen("vraagvertellen")
            question = play_random_sound('Vragen')
            question_without_extension = os.path.splitext(question)[0]
            file_folder = path_recordings + question_without_extension+"/" 
            create_folder_if_not_exicst(file_folder)
            wav_output_filename = file_folder + file_name_recording + ".wav"
        elif choice== choice_tell_story:      #vertel een verhaal
            wav_output_filename = path_recordings+ file_name_recording + ".wav" 
            time.sleep(0.5)
        elif choice== choice_ask_question:      #spreek een vraag in
            paint_screen("vraaginspreken")
            question_to_record = raw_input()
            question_to_record_underscore = question_to_record.replace(" ", "_")
            wav_output_filename = path_resources+"Vragen/" + question_to_record_underscore+ "_"+ create_random_string() +".wav"
        
        #create listening stream
        audio = pyaudio.PyAudio() # create pyaudio instantiation
        stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = dev_index,input = True, \
                            frames_per_buffer=chunk)
        
        #Begin met opnemen, en start de thread met de tijd dat er opgenomen is
        paint_screen("Opnemen")
        time_thread = TimeThread()
        time_thread.start()
        GPIO.output(yellow_led_pin, GPIO.HIGH)     
        
        record_audio(chunk, frames)
        time_thread.stop()
        time_thread.join()
        
        # stop the stream, close it, and terminate the pyaudio instantiation
        paint_screen("Bedankt")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        GPIO.output(yellow_led_pin, GPIO.LOW)
        # save the audio frames as .wav file
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()
        #if internet connection, then save to drive
        GPIO.output(red_led_pin, GPIO.HIGH)
        play_random_sound('Bedankt')
        if check_internet_connection():
            upload_to_drive(wav_output_filename, question_without_extension, choice)
        GPIO.output(red_led_pin, GPIO.LOW)  
        clear_screen()
    except:
        clear_screen()
        paint_screen("Oeps")
        turn_on_all_led()
    
    
    #ToDo:
    #-Check if writing  the file is possible to change, not writing to an array but to an file
    #-Delete error messages for creating audio stream
