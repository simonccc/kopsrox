#!/usr/bin/env python3

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from proxmoxer import ProxmoxAPI
import config as cfg

endpoint = cfg.proxmox['endpoint']
user = cfg.proxmox['user']
token_name = cfg.proxmox['token_name']
api_key = cfg.proxmox['api_key']

prox = ProxmoxAPI(
endpoint,
user=user,
token_name=token_name,
token_value=api_key,
verify_ssl=False,
timeout=10)

vms = prox.nodes.get()

print(vms)
