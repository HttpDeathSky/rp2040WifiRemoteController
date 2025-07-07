import board
import busio
import time
import usb_hid
import microcontroller
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse


# 初始化 UART（TX=GP0, RX=GP1，根据接线调整）
uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0.1)
kbd = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)
uart_buffer = ""

def writeInUart(cmd):
    uart.write(cmd.encode("utf-8") + b"\r\n")


def readFromUart():
    data = bytearray(128)
    n = uart.readinto(data)
    if n:
        return data[:n].decode("utf-8")
    return None


def sendCmdToEsp(cmd, ack="OK", timeout=2000):
    writeInUart(cmd)
    start = time.monotonic()
    while (time.monotonic() - start) * 1000 < timeout:
        data = readFromUart()
        if data and ack in data:
            break
    else:
        print("ESP模块无响应，3 秒后重启设备...")
        time.sleep(3)
        microcontroller.reset()


def getDataFromEsp():
    global uart_buffer
    new_data = readFromUart()
    if new_data:
        uart_buffer += new_data
    while "\r\n" in uart_buffer:
        line, uart_buffer = uart_buffer.split("\r\n", 1)
        if line.startswith("+IPD"):
            try:
                n1 = line.find("+IPD,")
                n2 = line.find(",", n1 + 5)
                n3 = line.find(":", n2)
                if n3 == -1:
                    uart_buffer = line + "\r\n" + uart_buffer  # 缓存回去
                    break
                data = line[n3 + 1 :].strip()
                data = data.replace(",CLOSED", "").replace("Key.", "").strip()
                if data == "*":
                    mouse.click(Mouse.LEFT_BUTTON)
                else:
                    ch = data[0].lower()
                    if ch in char_to_keycode:
                        kbd.press(char_to_keycode[ch])
                        kbd.release_all()
                time.sleep(0.01)
            except Exception as e:
                print("解析失败：", line, e)


# 字符映射到 HID Keycode
char_to_keycode = {
    "a": Keycode.A,
    "b": Keycode.B,
    "c": Keycode.C,
    "d": Keycode.D,
    "e": Keycode.E,
    "f": Keycode.F,
    "g": Keycode.G,
    "h": Keycode.H,
    "i": Keycode.I,
    "j": Keycode.J,
    "k": Keycode.K,
    "l": Keycode.L,
    "m": Keycode.M,
    "n": Keycode.N,
    "o": Keycode.O,
    "p": Keycode.P,
    "q": Keycode.Q,
    "r": Keycode.R,
    "s": Keycode.S,
    "t": Keycode.T,
    "u": Keycode.U,
    "v": Keycode.V,
    "w": Keycode.W,
    "x": Keycode.X,
    "y": Keycode.Y,
    "z": Keycode.Z,
    "0": Keycode.ZERO,
    "1": Keycode.ONE,
    "2": Keycode.TWO,
    "3": Keycode.THREE,
    "4": Keycode.FOUR,
    "5": Keycode.FIVE,
    "6": Keycode.SIX,
    "7": Keycode.SEVEN,
    "8": Keycode.EIGHT,
    "9": Keycode.NINE,
    "+": Keycode.ENTER,
    "-": Keycode.BACKSPACE,
    "_": Keycode.HOME,
    "=": Keycode.END,
    "^": Keycode.UP_ARROW,
    "?": Keycode.DOWN_ARROW,
    "<": Keycode.LEFT_ARROW,
    ">": Keycode.RIGHT_ARROW,
}

if __name__ == "__main__":
    try:
        # ESP Reset
        writeInUart("+++")
        time.sleep(1)

        # ESP Init
        sendCmdToEsp("AT")

        # ESP Config
        sendCmdToEsp("AT+CWMODE=3")  # 设置为 AP+STA 模式
        sendCmdToEsp("AT+CWQAP")  # 断开当前 WiFi
        sendCmdToEsp('AT+CWJAP="MIFI-D22F","1234567890"',"OK",100000)  # 连接WiFi
        sendCmdToEsp(
            'AT+CIPSTA="192.168.100.222","192.168.100.1","255.255.255.0"'
        )  # 固定IP
        sendCmdToEsp("AT+CIPMUX=1")  # 多连接模式
        sendCmdToEsp("AT+CIPSERVER=1,8080")  # 开启TCP服务器端口8080
        sendCmdToEsp("AT+CIFSR")  # 打印本地IP

        print("Wifi连接成功，等待TCP连接...")

        while True:
            getDataFromEsp()
    except KeyboardInterrupt:
        print("程序已手动终止。")
