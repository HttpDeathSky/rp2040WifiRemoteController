import socket
import time
import threading
from pynput import keyboard
from pynput import mouse

HOST = '192.168.100.222'
PORT = 8080

client = None
esc_press_time = 0
esc_press_count = 0
esc_timeout = 1  # 1 秒内连续按两次 ESC 才退出

def connect():
    global client
    while True:
        try:
            print(f"🔄 尝试连接 {HOST}:{PORT}...")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1)
            client.connect((HOST, PORT))
            print("✅ 已连接到 RP2040")
            return
        except Exception as e:
            print(f"[连接失败] {e}，3 秒后重试...")
            time.sleep(3)

def receive_from_rp2040():
    global client
    while True:
        try:
            data = client.recv(1024)
            if data:
                print(f"📥 来自 RP2040: {data.decode().strip()}")
        except Exception as e:
            print(f"[接收出错] {e}")
            break

def send_to_rp2040(data):
    global client
    try:
        client.sendall(data.encode())
    except Exception as e:
        print(f"[ERROR] {e}")
        print("⚠️ 尝试重新连接...")
        client.close()
        connect()
        try:
            client.sendall(data.encode())
        except Exception as e:
            print(f"[重试失败] {e}")

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        print(f"🖱️ 鼠标左键点击 at ({x}, {y})")
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
            esc_press_count = 1  # reset if too slow
        esc_press_time = now

        if esc_press_count >= 2:
            if client:
                client.close()
            print("👋 连按两次 ESC，已退出。")
            return False

# 主流程
connect()
# 启动接收线程
threading.Thread(target=receive_from_rp2040, daemon=True).start()

# 启动鼠标监听
mouse.Listener(on_click=on_click).start()

print("🎹 正在监听键盘（仅字母和数字），按 ESC 退出。")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
