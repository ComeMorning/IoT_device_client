import glob
import operator
import winreg

import serial
import serial.tools.list_ports
from serial.serialutil import SerialException
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

import Utils


def get_usb_devices():
    """查询所有usb端口"""
    usb_devce = glob.glob(r'/dev/ttyUSB*')
    if len(usb_devce) <= 0:
        print("The USB port can't find!")
    return usb_devce


def get_com_devices():
    """查询win所有com口"""
    port_list = list(serial.tools.list_ports.comports())
    port_list_name = []
    if len(port_list) <= 0:
        print("The Serial port can't find!")
        return
    else:
        for each_port in port_list:
            # 打印端口详细信息
            # print(each_port)
            port_list_name.append(each_port[0])

    # key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
    # device_num = winreg.QueryInfoKey(key)[1]
    # if device_num <= 0:
    #     print("The Serial port can't find!")
    #     return

    # port_list_name = [winreg.EnumValue(key, i)[1] for i in range(0, device_num)]
    return port_list_name


def create_main(port):
    try:
        main = modbus_rtu.RtuMain(
            serial.Serial(port=port, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
        )
        main.port = port
        main.set_timeout(2.0)
        return main
    except SerialException as e:
        Utils.log(e, 'error')


def match_port(config, com=False, usb=False):

    # 按照采集的终止地址、起始地址、功能码、地址依次排序
    sorted_conf = sorted(config, key=operator.itemgetter(4, 3, 2, 1), reverse=True)
    ports = get_com_devices() if com else get_usb_devices()
    print('ports:', ports)
    if not ports:
        return
    mains = [main for main in [create_main(port) for port in ports] if main]

    for device in sorted_conf:
        for main in mains:
            try:
                Utils.log(main.execute(device[1], device[2], device[3], device[4]-device[3]))
            except Exception as e:
                pass
            else:
                # 打印设备与串口对应信息
                print(device[0], '>>>>', main.port)
                mains.remove(main)
                break


if __name__ == '__main__':
    # 根据配置自动监测设备在哪个串口上
    # 根据设备地址、功能码、起始地址、结束地址等特征，唯一地标识一个设备
    # 遍历所有串口，发送设备采集信息，如果采集正常，则此设备与串口对应

    # 测试用例
    config = [
        ('device1', 1, cst.READ_HOLDING_REGISTERS, 0, 10),
        ('device2', 2, cst.READ_INPUT_REGISTERS, 0, 5),
        ('device3', 1, cst.READ_COILS, 0, 10)
    ]
    match_port(config, com=True)



