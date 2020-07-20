from django.db import models
from gateway.models import GatewayBase
from django.utils import timezone

# Create your models here.


class Gateway_task(models.Model):
    name = models.CharField(max_length=20, null=False)
    gateway = models.ForeignKey(GatewayBase, on_delete=models.CASCADE, to_field='gateway_name')
    description = models.TextField(default='', max_length=200)
    protocol = models.CharField(default='modbus', max_length=10)
    create_time = models.DateField()
    status = models.BooleanField(default=False)


class TaskRecord(models.Model):
    SEND_WAY = (
        ("change", u"改变上报"),
        ("time", u"定时上报")
    )
    gateway = models.ForeignKey(GatewayBase, on_delete=models.CASCADE, to_field='gateway_name')
    subordinate_id = models.IntegerField(null=False, default=1, verbose_name='设备地址')
    function_name = models.CharField(max_length=20, null=True, verbose_name='功能名称')
    identifier = models.CharField(max_length=10, verbose_name='标识符')
    modbus_function_code = models.IntegerField(null=False, verbose_name='modbus功能码')
    start_address = models.IntegerField(null=False)
    # address_length = models.IntegerField(default=1)
    data_length = models.IntegerField(default=16)
    top_limit = models.FloatField(null=True)
    low_limit = models.FloatField(null=True)
    scale = models.FloatField(default=1, verbose_name='缩放因子')
    interval = models.IntegerField(default=5, verbose_name='采集间隔（s）')
    send_way = models.CharField(choices=SEND_WAY, max_length=6)
    compute = models.TextField(max_length=200, default='', verbose_name='计算公式')
    active_status = models.BooleanField(default=True)




