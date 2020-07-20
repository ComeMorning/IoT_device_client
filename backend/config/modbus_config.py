# -*- conding:utf-8 -*-

""" 
@author: Salted fish 
@file: modbus_config.py 
@time: 2019/01/15 
"""
import socket


configs = {
    "MODBUS_SLAVE_CONNECT": {
        "host": "192.168.9.101",
        "port": 502,
        "subordinate_id": 1
    },
    "MODBUS_PROTOCOL_ADDRESS": {
        "telemetry_start_address": 0,
        "telemetry_end_address": 2153,
        "get_telemetry_step": 100,
        "telecommand_start_address": 7000,
        "telecommand_end_address": 9075,
        "get_telecommand_step": 100,
        "electrical_start_address": 9500,
        "electrical_end_address": 9766,
        "get_electrical_step": 100
    },
    "CONNECTION_TIMEOUT": 6,
    "CONNECTION_FAILURE": 5
}
