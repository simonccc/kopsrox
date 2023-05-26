# upstream image
up_image_url = 'https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img'

# defines
kopsrox_prompt='kopsrox:'
proxmox_conf='proxmox.ini'
kopsrox_conf='kopsrox.ini'

# verbs
top_verbs = ['image', 'cluster', 'node', 'etcd']
verbs_image = ['info', 'create', 'destroy']
verbs_cluster = ['info', 'create', 'destroy', 'kubectl', 'kubeconfig']
verbs_node = ['snapshot', 'destroy']
verbs_etcd = ['snapshot', 'restore']

# imports
import urllib3, sys, time, re
import kopsrox_proxmox as proxmox
import kopsrox_k3s as k3s
from configparser import ConfigParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from proxmoxer import ProxmoxAPI

# print passed verbs
def verbs_help(verbs):
  print('commands:', '\n')
  for i in verbs:
    print(i)

# generating the proxmox kopsrox image name
def kopsrox_img(proxstor,proximgid):
  return(proxstor + ':base-' + proximgid + '-disk-0')

# config checker
def conf_check(config,section,value,filename):
  try:
    return(config.get(section, value))
  except:
    print('ERROR: no value found for ' + section + ':' + value + ' in ' + filename)
    exit(0)

# additional master
def k3s_init_slave(vmid):

    # get config
    config = read_kopsrox_ini()
    masterid = get_master_id()
    k3s_version = (config['cluster']['k3s_version'])

    # check for existing k3s
    status = k3s.k3s_check(vmid)

    # if master check fails
    if ( status == 'fail'):
      ip = vmip(masterid)
      token = get_token()
      print('k3s_init_slave: installing k3s on', vmid)
      cmd = 'curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_TOKEN=\"' + token + '\" sh -s - server --server ' + 'https://' + ip + ':6443'
      proxmox.qaexec(vmid,cmd)

    status = k3s.k3s_check(vmid)
    return(status)

# return master id
def get_master_id():
    config = read_kopsrox_ini()
    return(int(config['proxmox']['proximgid']) + 1)

# check vm is powered on 
def vm_info(vmid):
    config = read_kopsrox_ini()
    proxnode = (config['proxmox']['proxnode'])
    prox = proxmox.prox_init()
    return(prox.nodes(proxnode).qemu(vmid).status.current.get())

# init worker node
def k3s_init_worker(vmid):

  # check for existing k3s
  status = k3s.k3s_check(vmid)

  # if check fails
  if ( status == 'fail'):

    print('k3s_init_worker: installing k3s on', vmid)
    config = read_kopsrox_ini()
    masterid = get_master_id()
    k3s_version = (config['cluster']['k3s_version'])
    ip = vmip(masterid)
    token = get_token()

    cmd = 'curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_URL=\"https://' + ip + ':6443\" K3S_TOKEN=\"' + token + '\" sh -s'
    proxmox.qaexec(vmid,cmd)
     
    status = k3s.k3s_check(vmid)
    return(status)
  print('k3s_init_worker:', vmid, 'ok')

# get token and strip linebreak
def get_token():
  f = open("kopsrox.k3stoken", "r")
  return(f.read().rstrip())

# kubectl
def kubectl(masterid,cmd):
  k = str(('/usr/local/bin/k3s kubectl ' +cmd))
  kcmd = proxmox.qaexec(masterid,k)
  return(kcmd)

# remove a node
def k3s_rm(vmid):
    workername = vmname(vmid)
    masterid = get_master_id()
    print('k3s_rm:', workername)
    kubectl(masterid, ('cordon ' + workername))
    kubectl(masterid, ('drain --ignore-daemonsets --force ' +  workername))
    kubectl(masterid, ('delete node ' + workername))
    proxmox.destroy(vmid)

# map id to hostname
def vmname(vmid):
    vmid = int(vmid)
    config = read_kopsrox_ini()
    proximgid = int(config['proxmox']['proximgid'])
    names = { 
            (proximgid + 1 ): 'kopsrox-m1',
            (proximgid + 2 ): 'kopsrox-m2', 
            (proximgid + 3 ): 'kopsrox-m3', 
            (proximgid + 5 ): 'kopsrox-w1', 
            (proximgid + 6 ): 'kopsrox-w2', 
            (proximgid + 7 ): 'kopsrox-w3', 
            }
    return(names[vmid])

# kubeconfig
def kubeconfig(masterid):
    ip = vmip(masterid)
    kubeconfig = proxmox.qaexec(masterid, 'cat /etc/rancher/k3s/k3s.yaml')

    # replace localhost with masters ip
    kubeconfig = kubeconfig.replace('127.0.0.1', ip)

    # write file out
    with open('kopsrox.kubeconfig', 'w') as kubeconfig_file:
      kubeconfig_file.write(kubeconfig)
    print("kubeconfig: generated kopsrox.kubeconfig")

# node token
def k3stoken(masterid):
    token = proxmox.qaexec(masterid, 'cat /var/lib/rancher/k3s/server/node-token')
    with open('kopsrox.k3stoken', 'w') as k3s:
      k3s.write(token)
    print("k3stoken: generated kopsrox.k3stoken")

# pass a vmid return the IP
def vmip(vmid):
    config = read_kopsrox_ini()
    proximgid = (config['proxmox']['proximgid'])
    network = (config['kopsrox']['network'])
    network_octs = network.split('.')
    basenetwork = ( network_octs[0] + '.' + network_octs[1] + '.' + network_octs[2] + '.' )
    ip = basenetwork + str(int(network_octs[-1]) + ( int(vmid) - int(proximgid)))
    return(ip)

# returns a dict of all config
def read_kopsrox_ini():
  kopsrox_config = ConfigParser()
  kopsrox_config.read(kopsrox_conf)
  return({s:dict(kopsrox_config.items(s)) for s in kopsrox_config.sections()})
