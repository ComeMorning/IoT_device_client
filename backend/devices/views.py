from django.shortcuts import render
from django.http import HttpResponse
import json
from django.utils import timezone
from .models import TCP_device, RTU_device
from gateway.models import GatewayBase


def create_tcp(request):
    if request.POST.get('edit_name') != 'undefined':
        # print('修改', request.POST.get('edit_name'))
        device = TCP_device.objects.get(device_name=request.POST['edit_name'], gateway_name=request.POST['gateway_name'])
    else:
        device = TCP_device()
    try:
        device.device_name = request.POST['name']
        device.description = request.POST['description']
        device.ip = request.POST['ip']
        device.port = request.POST['port']
        device.subordinate_id = request.POST['subordinate']
        device.gateway_name = GatewayBase.objects.get(gateway_name=request.POST['gateway_name'])
        device.create_time = timezone.datetime.now()
        device.protocol_way = 'TCP'
        device.save()
        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(str(e))
        return HttpResponse(json.dumps({'msg': '创建失败：' + str(e)}), content_type='application/json')


def create_rtu(request):
    device = RTU_device()
    try:
        device.device_name = request.POST['name']
        device.subordinate_id = request.POST['subordinate']
        device.description = request.POST['description']
        device.create_time = timezone.datetime.now()
        device.baud_rate = str(request.POST['baudRate'])
        device.stopbits = request.POST['stopbits']
        device.bite_size = request.POST['biteSize']
        device.parity = request.POST['parity']
        device.protocol_way = 'RTU'
        device.gateway_name = GatewayBase.objects.get(gateway_name=request.POST['gateway_name'])
        device.save()
        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(str(e))
        return HttpResponse(json.dumps({'msg': '创建失败：' + str(e)}), content_type='application/json')


def get_all(request):
    gateway_name = request.POST.get('gateway_name')
    if gateway_name:
        all_tcp = TCP_device.objects.filter(gateway_name=gateway_name)
        all_rtu = RTU_device.objects.filter(gateway_name=gateway_name)
    else:
        all_tcp = TCP_device.objects.all()
        all_rtu = RTU_device.objects.all()
        # RTU
    result = []
    for i in all_tcp:
        result.append({
            'name': i.device_name,
            'subordinate': i.subordinate_id,
            'description': i.description,
            'protocal': i.protocol_way,
            'create_time': i.create_time.strftime('%Y-%m-%d'),
            'gateway_name': i.gateway_name.gateway_name
        })
    for i in all_rtu:
        result.append({
            'name': i.device_name,
            'subordinate': i.subordinate_id,
            'description': i.description,
            'protocal': i.protocol_way,
            'create_time': i.create_time.strftime('%Y-%m-%d'),
            'gateway_name': i.gateway_name.gateway_name
        })
    return HttpResponse(json.dumps({'msg': 'ok', 'data': result}), content_type='application/json')


def delate(request):
    try:
        device = json.loads(request.POST['device'])
        print('网关：', device)
        for i in device:
            print(i, '----------')
            TCP_device.objects.filter(device_name=i['name'], gateway_name=i['gateway']).delete()
            RTU_device.objects.filter(device_name=i['name'], gateway_name=i['gateway']).delete()
        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(str(e))
        return HttpResponse(json.dumps({'msg': '删除失败：' + str(e)}), content_type='application/json')


def attribute(request):
    """获取属性对照表"""
    try:
        with open('config/need_attribute.json', encoding='utf-8')as f:
            data = json.loads(f.read())
        return HttpResponse(json.dumps({'msg': 'ok', 'data': data}), content_type='application/json')
    except Exception as e:
        print(str(e))
        return HttpResponse(json.dumps({'msg': '获取attribute失败：' + str(e)}), content_type='application/json')
