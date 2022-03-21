# Complete project details at https://RandomNerdTutorials.com
from machine import Pin
try:
  import usocket as socket
except:
  import socket

import network
import _thread as thread

import esp
esp.osdebug(None)

import gc
gc.collect()

from time import sleep

a = Pin(33, Pin.OUT) # 4
b = Pin(25, Pin.OUT) # 5
c = Pin(4, Pin.OUT) # 8
d = Pin(5, Pin.OUT) # 7
e = Pin(18, Pin.OUT) # 6
f = Pin(27, Pin.OUT) # 2
g = Pin(26, Pin.OUT) # 1

global_vars={"cur_num":0};

add_button = Pin(19, Pin.IN,Pin.PULL_UP)


lis = [a,b,c,d,e,f,g]

class ButtonAdd:
    def __init__(self,button):
        self.button = button
        self.last_button_value = 1

    def read_button(self):
        cur = self.button.value()
        if(cur == self.last_button_value):
            return 0;
        self.last_button_value = cur
        return cur == 0


numbers = [
    [a,b,f,e,c,d],
    [b,c],
    [a,b,g,e,d],
    [a,b,g,c,d],
    [f,g,b,c],
    [a,f,g,c,d],
    [a,f,g,c,d,e],
    [a,b,c],
    [a,b,f,g,c,e,d],
    [a,b,f,g,c,d],
]

def clear():
    for i in lis:
        i.value(1);

def display(n):
    clear();
    for pin in numbers[n]:
        pin.value(0);




clear()



#for i in range(10):
#    display(i);
#    sleep(1)

#while True:
#  a.value(not led.value())
#  sleep(1)

# network connection
ssid = 'MicroPython-AP'
password = '123456789'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
  pass

print('Connection successful')
print(ap.ifconfig())


def web_page():
  html = """
    <html>
   <head>
      <title>ESP Web Server</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="icon" href="data:,">
      <style>
            html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
            h1{color: #0F3376; padding: 2vh;}
            p{font-size: 1.5rem;}
            .button{display: inline-block; background-color: #e7bd3b; border: none;
            border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
            .button2{background-color: #4286f4;}
      </style>
   </head>
   <body>
      <h1>ESP Web Server</h1>
      <p>Current Number: <strong>""" + str(global_vars['cur_num']) + """</strong></p>
      <p><a href="/?action=increase"><button class="button">increase</button></a></p>
      <p><a href="/?action=decrease"><button class="button">decrease</button></a></p>
      <p><a href="/?action=reset"><button class="button">reset</button></a></p>


   </body>
</html>
"""
  return html




def web_page_thread():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = str(request)
        print('Content = %s' % request)
        cur_num = global_vars['cur_num']
        increase = request.find('/?action=increase')
        decrease = request.find('/?action=decrease')
        reset = request.find('/?action=reset')

        if increase == 6:
            print('increase')
            global_vars['cur_num'] = (cur_num+1)%10
        if decrease == 6:
            print('decrease')
            global_vars['cur_num'] = (cur_num+9)%10
        if reset == 6:
            print('reset')
            global_vars['cur_num'] = 0

        print("current number ",global_vars['cur_num'])
        display(global_vars['cur_num']);
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()



def circuit_thread():

    a = ButtonAdd(add_button)
    while True:
        cur_num = global_vars['cur_num']
        adding = a.read_button()
        if(adding):
            global_vars['cur_num'] = (cur_num+1)%10
            display(global_vars['cur_num'])
            print("inside circuit",cur_num)
        sleep(0.1)


thread.start_new_thread(circuit_thread, ())
thread.start_new_thread(web_page_thread, ())
