import time
from collections import defaultdict
import serial
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
import schedule
import Utils
import config.config as config
from mqtt import tb_client

configs = config.configs
device_connection = tb_client.OnDeviceConnection
device_disconnection = tb_client.OnDeviceDisconnection

# 串口、设备运行状态信息
devices_status = config.Dict()
# 样例
# devices_status = {
#     '/dev/ttyUSB1':{
#         'access': False,  # 串口是否可用
#         1:{                      # 设备地址
#             'status_func':None,  # 设备状态函数
#             'failure_count':0,   # 失败次数
#           }
#     }
# }


def init_dict():
    return [
            {'ts': None,
             'values': {}}
        ]


def modebus_rtu_client(port, baudrate=9600, timeout=6, set_verbose=True):
    global devices_status
    try:
        main = modbus_rtu.RtuMain(
            serial.Serial(port=port, baudrate=baudrate, bytesize=8, parity='N', stopbits=1, xonxoff=0)
        )
        main.set_timeout(timeout)
        if set_verbose:
            main.set_verbose(True)
        main.port = port
    except BaseException as e:
        # 串口不可用
        devices_status[port]['access'] = False
        Utils.log('连接 {} 串口失败\n{}'.format(port, e), 'error')
        return
    devices_status[port]['access'] = True
    Utils.log('连接 {} 成功'.format(port))
    return main


def init_send():
    Utils.log('init send')
    for port, devices in device_info_map.items():
        # 检查串口是否可用
        if devices_status[port]['access']:
            for device in devices:
                try:
                    address = device['address']
                    device_name = device['device_name']
                    # 记录设备状态
                    devices_status[port][address] = {
                        'status_func': device_connection,
                        'failure_count': 0,  # 失败次数
                    }
                    # 发送初始化状态
                    tb_client.OnDeviceConnection(device_name)
                except Exception:
                    Utils.log('init send failure{}-{}-{}'.format(port, address, device_name), 'error')
                    continue


def device_status_handler(port, address, device_name, status_func):
    """
    判断与处理设备状态
    port: 串口
    address：设备地址
    """
    global devices_status
    failure_count = devices_status[port][address]['failure_count']
    # 判断状态是否改变
    if status_func == devices_status[port][address]['status_func']:
        if status_func == device_connection and failure_count > 0:
            devices_status[port][address]['failure_count'] = 0
        return

    # 重新连接
    if status_func == device_connection:
        # 修改状态,发送消息
        devices_status[port][address]['status_func'] = status_func
        status_func(device_name)
        # 清空失败次数
        devices_status[port][address]['failure_count'] = 0
        Utils.log('{}-{}-{} - 设备重新连接'.format(port, address, device_name), 'info')

    # 连接断开
    elif status_func == device_disconnection:
        # 失败计数
        devices_status[port][address]['failure_count'] = failure_count + 1
        # 判断失败次数
        if failure_count + 1 >= configs.CONNECTION_FAILURE:
            # 修改状态,发送消息
            devices_status[port][address]['status_func'] = status_func
            status_func(device_name)
            Utils.log('{}-{}-{} -设备连接断开'.format(port, address, device_name), 'error')


def collect_data(main, *args, **kwargs):
    """modbus-RTU采集+预处理"""
    try:
        data = main.execute(1, 3, 0, 2, *args, **kwargs)
        data = {
            'temperature': data[0]/10,
             'shidu': data[1]/10
        }
        return data
    except Exception as e:
        Utils.log(e, 'error')


def error_handler(port, address, device_name):
    """采集异常处理"""
    Utils.log('{}-{}-{}设备采集异常')


def send():
    Utils.log("send start")
    send_data = defaultdict(init_dict)
    for main in mains:
        ts = Utils.getTS()
        # 获取此main 对应串口的设备s
        devices = device_info_map[main.port]
        for device in devices:
            device_name = device['device_name']
            address = device['address']
            # 采集
            data = device['collect_func'](main)
            # 组装设备数据结构
            if data:
                send_data[device_name][0]['ts'] = ts
                send_data[device_name][0]['values'] = data
                status = device_connection
            else:
                # 异常常处理
                error_handler(main.port, address, device_name)
                status = device_disconnection
            # 维护设备状态
            device_status_handler(main.port, address, device_name, status)
    if send_data.keys():
        # mqtt发送数据
        tb_client.SendTelemetry(data, True)
    Utils.log("send end")


if __name__ == '__main__':
    # 串口-地址-设备 映射
    device_info_map = {
        '/dev/ttyUSB1': [
            {'address': 1,
             'device_name': '温湿度传感器1',
             'collect_func': collect_data},
            {'address': 2,
                'device_name': 'other',
                'collect_func': collect_data}
        ],
        '/dev/ttyUSB2': [
            {'address': 1,
             'device_name': '温湿度传感器2',
             'collect_func': collect_data},
        ],
        '/dev/ttyUSB3': [
            {'address': 1,
             'device_name': '温湿度传感器3',
             'collect_func': collect_data},
        ],
    }

    mains = [modebus_rtu_client(i) for i in device_info_map.keys()]
    print(devices_status)
    init_send()
    schedule.every(3).seconds.do(send)
    while True:
        schedule.run_pending()
        time.sleep(1)
