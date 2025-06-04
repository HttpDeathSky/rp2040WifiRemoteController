# WorkWith RP2040

KeyRun.bat:Client Run

adafruit...:firmware

boot.py:copy to rp2040

code.py:copy to rp2040

keyboard_to_rp2040.py work with KeyRun.bat

client need python env

code.py :

esp_sendCMD('AT+CWJAP="4G-UFI-3A6A","1234567890"', "OK", 20000)

4G-UFI-3A6A : wifiname

1234567890 : password

esp_sendCMD('AT+CIPSTA="192.168.100.222","192.168.100.1","255.255.255.0"', "OK")

192.168.100.222 : rp2040 ip

192.168.100.1 : netgate

now only support few board press for escape company review