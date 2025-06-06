# RP2040 Synchronous

PressListener.pyw Client Script , use to listen keyboard and mouse event.

adafruit... : rp2040 firmware

boot.py : copy to rp2040 , rp2040 run config

code.py : copy to rp2040 , rp2040 run code

## Notice

> PressListener.pyw need python environment, program with python313

> code.py config
>
> 1. esp_sendCMD('AT+CWJAP="4G-UFI-3A6A","1234567890"', "OK", 20000)
>    - 4G-UFI-3A6A : wifiName
>    - 1234567890 : password
> 2. esp_sendCMD('AT+CIPSTA="192.168.100.222","192.168.100.1","255.255.255.0"', "OK")
>    - 192.168.100.222 : rp2040 ip
>    - 192.168.100.1 : netgate

now only support few board press for escape company review