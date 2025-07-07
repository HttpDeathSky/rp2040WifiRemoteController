import socket
import time
import threading
import os
import psutil
from pynput import keyboard, mouse
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

HOST = '192.168.100.222'
PORT = 8080
client = None
esc_press_time = 0
esc_press_count = 0
esc_timeout = 1

def singleCheck():
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['pid'] == os.getpid():
                continue
            if proc.info['cmdline'] and proc.info['cmdline'] == psutil.Process(os.getpid()).cmdline():
                os._exit(0)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def connect():
    global client
    while True:
        try:
            print(f"Connect to RP2040: {HOST}:{PORT}...")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1)
            client.connect((HOST, PORT))
            print("Connection Created")
            return
        except Exception as e:
            print(f"Lost Connection {e}，retry in 3s ...")
            time.sleep(3)

def receive_from_rp2040():
    global client
    while True:
        try:
            data = client.recv(1024)
            if data:
                print(f"RP2040: {data.decode().strip()}")
        except Exception as e:
            break

def send_to_rp2040(data):
    global client
    if not client:
        return
    try:
        client.sendall(data.encode())
    except Exception as e:
        print(f"Connection ERROR: {e}")
        client.close()
        connect()
        print("Reconnection...")
        try:
            client.sendall(data.encode())
        except Exception as e:
            print(f"Reconnection fail: {e}")

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        print(f"left click:({x}, {y})")
        send_to_rp2040("*")

def on_press(key):
    try:
        k = key.char
        if k.isalnum():
            print(f"Pressed: {k}")
            send_to_rp2040(k)
    except AttributeError:
        if key == keyboard.Key.enter:
            print("Pressed: <ENTER>")
            send_to_rp2040('+')
        elif key == keyboard.Key.backspace:
            print("Pressed: <BACKSPACE>")
            send_to_rp2040('-')
        elif key == keyboard.Key.home:
            print("Pressed: <HOME>")
            send_to_rp2040('_')
        elif key == keyboard.Key.end:
            print("Pressed: <END>")
            send_to_rp2040('=')
        elif key == keyboard.Key.up:
            print("Pressed: <UP>")
            send_to_rp2040('^')
        elif key == keyboard.Key.down:
            print("Pressed: <DOWN>")
            send_to_rp2040('?')
        elif key == keyboard.Key.left:
            print("Pressed: <LEFT>")
            send_to_rp2040('<')
        elif key == keyboard.Key.right:
            print("Pressed: <RIGHT>")
            send_to_rp2040('>')

def on_release(key):
    global esc_press_time, esc_press_count
    if key == keyboard.Key.esc:
        now = time.time()
        if now - esc_press_time <= esc_timeout:
            esc_press_count += 1
        else:
            esc_press_count = 1
        esc_press_time = now

        if esc_press_count >= 2:
            if client:
                client.close()
            print("Double Press ESC Exit !")
            os._exit(0)

def htpsIcon():
    img = Image.new('RGB', (64, 64), color='black')
    d = ImageDraw.Draw(img)
    d.rectangle([16, 16, 48, 48], fill='white')
    return img

def shutDown(icon=None, item=None):
    if client:
        client.close()
    icon.stop()
    os._exit(0)
    
def reconnect(icon=None, item=None):
    global client
    try:
        if client:
            client.close()
    except:
        pass
    connect()

def disconnect(icon=None, item=None):
    global client
    if client:
        try:
            client.close()
        except Exception as e:
            pass
        client = None

if __name__ == '__main__':
    singleCheck()
    connect()
    threading.Thread(target=receive_from_rp2040, daemon=False).start()
    mouse.Listener(on_click=on_click).start()
    keyboard.Listener(on_press=on_press, on_release=on_release).start()
    icon = Icon(
        "RP2040",
        htpsIcon(),
        menu=Menu(
            MenuItem('Reconnect', reconnect),
            MenuItem('Disconnect', disconnect),
            MenuItem('Exit', shutDown)
        )
    )
    icon.run()