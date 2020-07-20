import json
from django.http import HttpResponse
from django.utils import timezone
from .models import Gateway_task, TaskRecord
from gateway.models import GatewayBase


# Create your views here.


def get_all(request):
    all_task = Gateway_task.objects.all()
    result = []
    for i in all_task:
        result.append({
            'name': i.name,
            'protocol': i.protocol,
            'description': i.description,
            'gateway': i.gateway.gateway_name,
            'create_time': i.create_time.strftime('%Y-%m-%d'),
            'status': 'true' if i.status else 'false'
        })
    return HttpResponse(json.dumps({'msg': 'ok', 'data': result}), content_type='application/json')


def create(request):
    task = Gateway_task()
    try:
        task.name = request.POST['name']
        task.description = request.POST['description']
        task.create_time = timezone.datetime.now()
        task.protocol = 'Modbus'
        task.gateway = GatewayBase.objects.get(gateway_name=request.POST['gateway'])
        task.save()
        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'msg': '创建失败'}), content_type='application/json')


def delete(request):
    name = request.POST['name']
    try:
        name = name.split(',')
        for i in name:
            Gateway_task.objects.filter(name=i).delete()
        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'msg': '删除失败' + str(e)}), content_type='application/json')


def edit(request):
    try:
        before_edit = request.POST['before_edit']
        task = Gateway_task.objects.get(name=before_edit)
        task.name = request.POST['name']
        task.description = request.POST['description']
        task.save()
        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'msg': '修改失败'}), content_type='application/json')


def add_record(request):
    print(request.POST)
    # try:
    stop_address = int(request.POST['stop_address'])
    start_address = int(request.POST['start_address'])
    record_count = stop_address - start_address + 1
    function_name = request.POST['function_name'].split(',')
    identifier = request.POST['identifier'].split(',')
    gateway = GatewayBase.objects.get(gateway_name=request.POST['gateway'])
    subordinate_id = int(request.POST['subordinate_id'])

    modbus_function_code = request.POST['modbus_function_code']
    data_length = request.POST['data_length']
    top_limit = request.POST['top_limit']
    low_limit = request.POST['low_limit']
    scale = request.POST['scale']
    interval = request.POST['interval']
    send_way = request.POST['send_way']
    compute = request.POST['compute']
    for i in range(record_count):
        TaskRecord.objects.create(
            gateway=gateway,
            subordinate_id=subordinate_id,
            function_name=function_name[i],
            identifier=identifier[i],
            modbus_function_code=modbus_function_code,
            start_address=start_address + i,
            data_length=data_length,
            top_limit=top_limit,
            low_limit=low_limit,
            scale=scale,
            interval=interval,
            send_way=send_way,
            compute=compute,
            active_status=True
        )
    print('插入%s条记录' % record_count)
    return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    # except Exception as e:
    #     print(e)
    #     return HttpResponse(json.dumps({'msg': '添加失败' + str(e)}), content_type='application/json')


def get_all_record(request):
    gateway = request.POST.get('gateway')
    print(gateway, '的记录')
    if gateway and gateway != 'undefined':
        all_record = TaskRecord.objects.filter(gateway=gateway)
    else:
        all_record = TaskRecord.objects.all()
    result = []
    for i in all_record:
        result.append({
            'subordinate_id': i.subordinate_id,
            'modbus_function_code': i.modbus_function_code,
            "start_address": i.start_address,
            'identifier': i.identifier,
            'data_length': i.data_length,
            'function_name': i.function_name,
            'compute': i.compute,
            'send_way': '定时上报' if i.send_way == 'time' else '变更上报',
            'active_status': 'true' if i.active_status else 'false'
        })
    return HttpResponse(json.dumps({'msg': 'ok', 'data': result}), content_type='application/json')


def delete_record(request):
    try:
        subordinate_id = request.POST['subordinate_id']
        start_address = request.POST['start_address']
        TaskRecord.objects.filter(subordinate_id=subordinate_id, start_address=start_address).delete()
        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'msg': '修改失败'}), content_type='application/json')


def change_status(request):
    try:
        subordinate_id = request.POST['subordinate_id']
        start_address = request.POST['start_address']
        record = TaskRecord.objects.get(subordinate_id=subordinate_id, start_address=start_address)
        if record.active_status:
            record.active_status = False
        else:
            record.active_status = True
        record.save()
        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'msg': '失败'}), content_type='application/json')


def start_task(request):
    try:
        gateway = request.POST['gateway']
        # 获取所有活跃采集地址
        all_record = TaskRecord.objects.filter(gateway=gateway, active_status=True)

        return HttpResponse(json.dumps({'msg': 'ok'}), content_type='application/json')
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'msg': '失败'}), content_type='application/json')
