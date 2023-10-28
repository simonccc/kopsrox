#!/usr/bin/env python3

# used by eg vmnames
import kopsrox_proxmox as proxmox

from configparser import ConfigParser

# verbs
top_verbs = ['image', 'cluster', 'etcd']
verbs_image = ['info', 'create', 'destroy']
verbs_cluster = ['info', 'create', 'update', 'destroy', 'kubectl', 'kubeconfig']
verbs_etcd = ['snapshot', 'restore', 'list', 'prune']

# config dict
kopsrox_config = ConfigParser()
kopsrox_config.read('kopsrox.ini')
config = ({s:dict(kopsrox_config.items(s)) for s in kopsrox_config.sections()})

# used items
proximgid = int(config['proxmox']['proximgid'])
proxnode = config['proxmox']['proxnode']

# get token and strip linebreak
def get_token():
  f = open("kopsrox.k3stoken", "r")
  return(f.read().rstrip())

# return a list of valid koprox vms
def vmnames():
  vmid = proximgid
  vmnames = []
  for vmid in proxmox.list_kopsrox_vm():
    if ( vmid > proximgid ):
      vmnames.append(vmname(vmid))
  return(vmnames)

# look up vmid from name
def vmname2id(name):
  vmid = proximgid
  while ( vmid <= (int(proximgid) + 9 )):
    # if match return id
    if ( name == vmname(int(vmid)) ):
      return(int(vmid))
    vmid = (int(vmid) + 1)

# node token
def k3stoken(masterid):
    token = proxmox.qaexec(masterid, 'cat /var/lib/rancher/k3s/server/node-token')
    with open('kopsrox.k3stoken', 'w') as k3s:

      # this function name seems weird
      k3s.write(token)
