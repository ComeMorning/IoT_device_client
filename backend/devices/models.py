from django.db import models
from gateway.models import GatewayBase
# Create your models here.


class TCP_device(models.Model):
    device_name = models.CharField(max_length=20, null=False)
    subordinate_id = models.IntegerField(null=False)
    description = models.TextField(max_length=200, default='', verbose_name='设备描述')
    create_time = models.DateField(null=False)
    protocol_way = models.CharField(max_length=3, null=False, verbose_name='设备接入方式')
    last_active = models.DateField(auto_now=True)
    work_flag = models.BooleanField(default=True, verbose_name='激活状态')
    gateway_name = models.ForeignKey(GatewayBase, on_delete=models.CASCADE, to_field='gateway_name')


class RTU_device(models.Model):
    device_name = models.CharField(max_length=20, null=False)
    subordinate_id = models.IntegerField(null=False)
    description = models.TextField(max_length=200, default='', verbose_name='设备描述')
    create_time = models.DateField(null=False)
    baud_rate = models.IntegerField(null=False, default=9600)
    bite_size = models.IntegerField(default=8)
    parity = models.CharField(max_length=1, default='N')
    stopbits = models.FloatField(default=1)
    protocol_way = models.CharField(max_length=3, null=False, verbose_name='设备接入方式')
    last_active = models.DateField(auto_now=True)
    work_flag = models.BooleanField(default=True, verbose_name='激活状态')
    gateway_name = models.ForeignKey(GatewayBase, on_delete=models.CASCADE, to_field='gateway_name')


class Attribute(models.Model):
    code = models.IntegerField()
    category = models.CharField(max_length=20, null=False)
    identifier = models.CharField(max_length=10, null=False)
    name = models.CharField(max_length=20, null=False)