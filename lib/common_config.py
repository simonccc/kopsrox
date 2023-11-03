#!/usr/bin/env python3

# verbs
top_verbs = ['image', 'cluster', 'etcd']
verbs_image = ['info', 'create', 'destroy']
verbs_cluster = ['info', 'create', 'update', 'destroy', 'kubectl', 'kubeconfig']
verbs_etcd = ['snapshot', 'restore', 'list', 'prune']

# config dict
from configparser import ConfigParser
kopsrox_config = ConfigParser()
kopsrox_config.read('kopsrox.ini')
config = ({s:dict(kopsrox_config.items(s)) for s in kopsrox_config.sections()})

# used items
#proximgid = int(config['proxmox']['proximgid'])
#proxnode = config['proxmox']['proxnode']

# look up vmid from name
#def vmname2id(name):
#  vmid = proximgid
#  while ( vmid <= (int(proximgid) + 9 )):
#    # if match return id
#    if ( name == vmname(int(vmid)) ):
#      return(int(vmid))
#    vmid = (int(vmid) + 1)
