#!/usr/bin/env python3

# functions
#from kopsrox_config import vmnames,cluster_info, cluster_id, vms, vmip, cloudinituser
from kopsrox_k3s import export_k3s_token
#from kopsrox_proxmox import clone
from kopsrox_kmsg import kmsg

# other imports
import sys

# passed command
cmd = sys.argv[2]

# map arg if passed
try:
  arg = sys.argv[3]
except:
  pass

# define kname
kname = 'k3s_'+cmd

# k3s token
if cmd == 'k3stoken':
  export_k3s_token()
