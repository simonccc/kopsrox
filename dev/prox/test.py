#!/usr/bin/env python3

from proxmoxer import ProxmoxAPI
import config as cfg

api_key = cfg.proxmox['api_key']

prox = ProxmoxAPI('192.168.0.244', user='root@pam', token_name='kopsrox', token_value=api_key,  verify_ssl=False, timeout=10)

vms = prox.nodes.get()

print(vms)
