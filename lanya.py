# -*- coding:utf-8 -*-

# 导入模块
from machine import Pin
from machine import Timer
from time import sleep_ms
import bluetooth

# 定义全局变量
BLE_MSG = ""

class ESP32_BLE():
    def __init__(self, name):
        
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        self.name = name
        
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name=name)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        self.led.value(1)
        self.timer1.deinit()

    def disconnected(self):        
        self.timer1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))
        #self.led.value(0)

    def ble_irq(self, event, data):
        global BLE_MSG
        #_IRQ_CENTRAL_CONNECT 蓝牙终端链接了此设备
        if event == 1:
            self.connected()
        #_IRQ_CENTRAL_DISCONNECT 蓝牙终端断开此设备
        elif event == 2:
            self.advertiser()
            self.disconnected()
        #_IRQ_GATTS_WRITE 蓝牙终端向ESP32发送数据，接收数据处理
        elif event == 3:  
            buffer = self.ble.gatts_read(self.rx)
            BLE_MSG = buffer.decode('UTF-8').strip()
            print("接收到其他蓝牙终端发来的数据:",BLE_MSG)
            
    def register(self):        
        service_uuid = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        reader_uuid = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        sender_uuid = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
        services = (
            (
                bluetooth.UUID(service_uuid),
                (
                    (bluetooth.UUID(sender_uuid), bluetooth.FLAG_NOTIFY),
                    (bluetooth.UUID(reader_uuid), bluetooth.FLAG_WRITE),
                )
            ),
        )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(services)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02', 'UTF-8') + bytearray((len(name) + 1, 0x09), 'UTF-8') + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")

def main(BLE_NAME):
    global BLE_MSG
    #调用BLE 设置ESP32被发现的蓝牙名称 名称为主程序传参传入
    ble = ESP32_BLE(BLE_NAME)
    #蓝牙指示灯(板载蓝色LED)，当ESP32设备未被连接，则周期闪烁；若被连接，则常亮
    led = Pin(2, Pin.OUT)

    while True:
        #使用测试数据需要符合 r#hello
        if BLE_MSG.split("#")[0] == 'r':
            #打印获取到的数据
            print(BLE_MSG)
            # 清空接收的数据
            BLE_MSG = ""
        sleep_ms(100)


if __name__ == "__main__":
    main("ESP32")
