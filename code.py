import board
import busio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse


# 初始化 UART（TX=GP0, RX=GP1，根据接线调整）
uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0.1)
kbd = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

def uart_write(cmd):
    uart.write(cmd.encode('utf-8') + b'\r\n')

def uart_read():
    data = bytearray(64)
    n = uart.readinto(data)
    if n:
        return data[:n].decode('utf-8')
    return None

def esp_sendCMD(cmd, ack, timeout=2000):
    uart_write(cmd)
    start = time.monotonic()
    while (time.monotonic() - start) * 1000 < timeout:
        s_get = uart_read()
        if s_get:
            print(s_get)
            if ack in s_get:
                return True
    return False

def esp_ReceiveData():
    s_get = uart_read()
    if not s_get:
        return []

    results = []
    lines = s_get.split('\r\n')  # 分割成每一条独立行（因为每条+IPD通常以回车换行结束）
    for line in lines:
        if '+IPD' in line:
            try:
                n1 = line.find('+IPD,')
                n2 = line.find(',', n1 + 5)
                ID = int(line[n1 + 5:n2])
                n3 = line.find(':', n2)
                if n3 == -1:
                    continue  # 格式不完整
                data = line[n3 + 1:].strip()
                data = data.replace(',CLOSED', '').replace('Key.', '').strip()
                if data:
                    results.append((ID, data))
            except Exception as e:
                print("解析失败：", line, e)
    return results


# 字符映射到 HID Keycode
char_to_keycode = {
    'a': Keycode.A, 'b': Keycode.B, 'c': Keycode.C, 'd': Keycode.D,
    'e': Keycode.E, 'f': Keycode.F, 'g': Keycode.G, 'h': Keycode.H,
    'i': Keycode.I, 'j': Keycode.J, 'k': Keycode.K, 'l': Keycode.L,
    'm': Keycode.M, 'n': Keycode.N, 'o': Keycode.O, 'p': Keycode.P,
    'q': Keycode.Q, 'r': Keycode.R, 's': Keycode.S, 't': Keycode.T,
    'u': Keycode.U, 'v': Keycode.V, 'w': Keycode.W, 'x': Keycode.X,
    'y': Keycode.Y, 'z': Keycode.Z,
    '0': Keycode.ZERO, '1': Keycode.ONE, '2': Keycode.TWO, '3': Keycode.THREE,
    '4': Keycode.FOUR, '5': Keycode.FIVE, '6': Keycode.SIX, '7': Keycode.SEVEN,
    '8': Keycode.EIGHT, '9': Keycode.NINE,
    '+':Keycode.ENTER, '-':Keycode.BACKSPACE, '_':Keycode.HOME, '=':Keycode.END,
    '^':Keycode.UP_ARROW, '?':Keycode.DOWN_ARROW, '<':Keycode.LEFT_ARROW, '>':Keycode.RIGHT_ARROW
}

if __name__ == "__main__":
    try:
        # 复位 ESP，进入命令模式
        uart_write('+++')
        time.sleep(1)

        # ESP WiFi 和 TCP Server 初始化
        if not esp_sendCMD("AT", "OK"):
            print("ESP模块无响应")
            while True:
                pass

        esp_sendCMD("AT+CWMODE=3", "OK")  # 设置为 AP+STA 模式
        esp_sendCMD('AT+CWJAP="4G-UFI-3A6A","1234567890"', "OK", 20000)  # 连接WiFi
        esp_sendCMD('AT+CIPSTA="192.168.100.222","192.168.100.1","255.255.255.0"', "OK")
        esp_sendCMD("AT+CIPMUX=1", "OK")  # 多连接模式
        esp_sendCMD("AT+CIPSERVER=1,8080", "OK")  # 开启TCP服务器端口8080
        esp_sendCMD("AT+CIFSR", "OK")  # 打印本地IP

        print("等待TCP连接...")

        while True:
            packets = esp_ReceiveData()
            for ID, data in packets:
                print(data)
                #鼠标操作
                if data == "*":
                    mouse.click(Mouse.LEFT_BUTTON)
                else:
                    #键盘操作
                    ch = data[0].lower()
                    if ch in char_to_keycode:
#                         print(ch)
                        kbd.press(char_to_keycode[ch])
                        kbd.release_all()
                        time.sleep(0.01)
    except KeyboardInterrupt:
        print("程序已手动终止。")