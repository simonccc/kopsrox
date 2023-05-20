# upstream image
up_image_url = 'https://cdimage.debian.org/images/cloud/bullseye/latest/debian-11-generic-amd64.qcow2'

# defines
kopsrox_prompt='kopsrox:'
proxmox_conf='proxmox.ini'
kopsrox_conf='kopsrox.ini'

# verbs
top_verbs = ['image', 'cluster']
verbs_image = ['info', 'create', 'destroy']
verbs_cluster = ['info', 'create', 'destroy', 'kubectl', 'kubeconfig']

# imports
import urllib3, sys, time, re
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

# connect to proxmox
def prox_init():

  # read proxmox config
  proxmox_config = ConfigParser()
  proxmox_config.read(proxmox_conf)

  # check values in config
  endpoint = conf_check(proxmox_config,'proxmox','endpoint',proxmox_conf)
  user = conf_check(proxmox_config,'proxmox','user',proxmox_conf)
  token_name = conf_check(proxmox_config,'proxmox','token_name',proxmox_conf)
  api_key = conf_check(proxmox_config,'proxmox','api_key',proxmox_conf)

  prox = ProxmoxAPI(
endpoint,
user=user,
token_name=token_name,
token_value=api_key,
verify_ssl=False,
timeout=10)

  return prox

# run a exec via qemu-agent
def qaexec(vmid,cmd):

  # config
  config = read_kopsrox_ini()
  proxnode = (config['proxmox']['proxnode'])

  # proxmox 
  prox = prox_init()

  # qagent no yet running check
  # needs a loop counter and check adding...
  qagent_running = 'false'
  while ( qagent_running == 'false' ):
    try:
      qa_ping = prox.nodes(proxnode).qemu(vmid).agent.ping.post()
      qagent_running = 'true'
    except:
      print('qaexec: ogent not started on', vmid)
      time.sleep(10)

  # send command
  qa_exec = prox.nodes(proxnode).qemu(vmid).agent.exec.post(
          command = "sh -c \'" + cmd +"\'",
          )

  # get pid
  pid = qa_exec['pid']

  # loop until command has finish
  pid_status = '0'
  while ( int(pid_status) != 1 ):
    try:
      pid_check = (prox.nodes(proxnode).qemu(vmid).agent("exec-status").get(pid = pid))
    except:
      print('qagent: waiting for', pid)
      time.sleep(2)

    # will equal 1 when process is done
    pid_status = pid_check['exited']

  # check for error
  if ( int(pid_check['exitcode']) == 127 ):
    print('ERROR: exec failure', pid_check['err-data'])
    exit(0)

  # check for err-data
  try:
    if (pid_check['err-data']):
      return('ERROR:', pid_check['err-data'])
  except:
    return(pid_check['out-data'])


# check for k3s status
def k3s_check(vmid):

    # get masterid
    masterid = get_master_id()

    # check for exiting k3s
    cmd = 'if [ -f /usr/local/bin/k3s ] ; then echo -n present; else echo -n fail;fi'
    k3s_check = qaexec(vmid,cmd)

    # fail early
    if ( k3s_check == 'fail' ):
      print('k3s_check: no k3s bin found')
      return('fail')

    # check node is healthy
    if (k3s_check == 'present'):

      # test call
      k = kubectl(masterid,'get nodes')

      while ( re.search('NotReady', k)):
        print('k3s_check: node not ready', vmid)
        time.sleep(5)
        k = kubectl(masterid,'get nodes')

      return('true')

    # else return fail
    return('fail')

# init 1st master
def k3s_init_master(vmid):

    # get config
    config = read_kopsrox_ini()
    k3s_version = (config['cluster']['k3s_version'])

    # check for existing k3s
    status = k3s_check(vmid)

    # if master check fails
    if ( status == 'fail'):
      print('k3s_init_master: installing k3s on', vmid)
      cmd = 'curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="' + k3s_version + '" sh -s'
      qaexec(vmid,cmd)

    status = k3s_check(vmid)
    return(status)

# return master id
def get_master_id():
    config = read_kopsrox_ini()
    return(int(config['proxmox']['proximgid']) + 1)

# check vm is powered on 
def vm_info(vmid):
    config = read_kopsrox_ini()
    proxnode = (config['proxmox']['proxnode'])
    prox = prox_init()
    return(prox.nodes(proxnode).qemu(vmid).status.current.get())

# init worker node
def k3s_init_worker(vmid):

  # check for existing k3s
  status = k3s_check(vmid)

  # if check fails
  if ( status == 'fail'):

    print('k3s_init_worker: installing k3s on', vmid)
    config = read_kopsrox_ini()
    masterid = get_master_id()
    k3s_version = (config['cluster']['k3s_version'])
    ip = vmip(masterid)
    token = get_token()

    cmd = 'curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="' + k3s_version + '" K3S_URL=\"https://' + ip + ':6443\" K3S_TOKEN=\"' + token + '\" sh -s'
    qaexec(vmid,cmd)
     
    status = k3s_check(vmid)
    return(status)
  print('k3s_init_worker:', vmid, 'ok')

# get token
def get_token():
  f = open("kopsrox.k3stoken", "r")
  # return contents and strip linebreak
  return(f.read().rstrip())

# kubectl
def kubectl(masterid,cmd):
  k = str(('/usr/local/bin/k3s kubectl ' +cmd))
  return(qaexec(masterid,k))

# kubeconfig
def kubeconfig(masterid):
    ip = vmip(masterid)
    kubeconfig = qaexec(masterid, 'cat /etc/rancher/k3s/k3s.yaml')

    # replace localhost with masters ip
    kubeconfig = kubeconfig.replace('127.0.0.1', ip)

    # write file out
    with open('kopsrox.kubeconfig', 'w') as kubeconfig_file:
      kubeconfig_file.write(kubeconfig)
    print("kubeconfig: generated kopsrox.kubeconfig")

# node token
def k3stoken(masterid):
    token = qaexec(masterid, 'cat /var/lib/rancher/k3s/server/node-token')
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

# return kopsrox_vms as list
def list_kopsrox_vm():

    # config
    config = read_kopsrox_ini()
    proxnode = (config['proxmox']['proxnode'])
    proximgid = (config['proxmox']['proximgid'])

    #get proxmox connection
    prox = prox_init()

    # init list
    vmids = []

    # foreach returned vm
    for vm in prox.nodes(proxnode).qemu.get():
      vmid = vm.get('vmid')
      # if vm in range add to list
      if ((int(vmid) >= int(proximgid)) and (int(vmid) < (int(proximgid) + 10))):
        vmids.append(vmid)

    # return list
    vmids.sort()
    return(vmids)

# stop and destroy vm
def destroy(vmid):

    # get required config
    config = read_kopsrox_ini()
    proxnode = (config['proxmox']['proxnode'])
    proximgid = (config['proxmox']['proximgid'])

    # proxinit
    prox = prox_init()
    try:
      poweroff = prox.nodes(proxnode).qemu(vmid).status.stop.post()
      task_status(prox, poweroff, proxnode)
      delete = prox.nodes(proxnode).qemu(vmid).delete()
      task_status(prox, delete, proxnode)
    except:
      if (int(proximgid) != int(vmid)):
        print('unable to destroy', vmid)
        exit(0)

# clone
def clone(vmid):

    # read config
    config = read_kopsrox_ini()

    # normal defines
    proxnode = (config['proxmox']['proxnode'])
    proxstor = (config['proxmox']['proxstor'])
    proximgid = (config['proxmox']['proximgid'])

    # map network info
    networkgw = (config['kopsrox']['networkgw'])
    ip = vmip(vmid)

    # vm specs
    cores = (config['kopsrox']['vm_cpu'])
    ram = (config['kopsrox']['vm_ram']) 
    memory = int(int(ram) * 1024)

    # defaults
    hostname = 'unknown'

    # map hostname
    if ( int(vmid) == ( int(proximgid) + 1 )):
      hostname = 'kopsrox-m1'
    if ( int(vmid) == ( int(proximgid) + 5 )):
      hostname = 'kopsrox-w1'
    if ( int(vmid) == ( int(proximgid) + 6 )):
      hostname = 'kopsrox-w2'
    if ( int(vmid) == ( int(proximgid) + 7 )):
      hostname = 'kopsrox-w3'

    # init proxmox
    prox = prox_init()
   
    # clone
    print('creating:', hostname)
    clone = prox.nodes(proxnode).qemu(proximgid).clone.post(
            newid = vmid,
            )
    task_status(prox, clone, proxnode)

    # configure
    configure = prox.nodes(proxnode).qemu(vmid).config.post(
                name = hostname,
                onboot = 1,
                hotplug = 0,
                cores = cores, 
                memory = memory,
                ipconfig0 = ( 'gw=' + networkgw + ',ip=' + ip + '/24' ))
    task_status(prox, str(configure), proxnode)

    # power on
    poweron = prox.nodes(proxnode).qemu(vmid).status.start.post()
    task_status(prox, str(poweron), proxnode)
    time.sleep(2)

# returns a dict of all config
def read_kopsrox_ini():
  kopsrox_config = ConfigParser()
  kopsrox_config.read(kopsrox_conf)
  return({s:dict(kopsrox_config.items(s)) for s in kopsrox_config.sections()})

# generate the default kopsrox.ini
def init_kopsrox_ini():

  # get config
  kopsrox_config = ConfigParser()
  kopsrox_config.read(kopsrox_conf)

  # create sections
  kopsrox_config.add_section('proxmox')
  # node to operate on
  kopsrox_config.set('proxmox', 'proxnode', 'proxmox')
  # storage on node
  kopsrox_config.set('proxmox', 'proxstor', 'local-lvm')
  # local image id
  kopsrox_config.set('proxmox', 'proximgid', '600')
  # upstream image
  kopsrox_config.set('proxmox', 'up_image_url', up_image_url)
  # network bridge
  kopsrox_config.set('proxmox', 'proxbridge', 'vmbr0')

  # kopsrox config
  kopsrox_config.add_section('kopsrox')

  # size for kopsrox nodes
  kopsrox_config.set('kopsrox', 'vm_disk', '20G')
  kopsrox_config.set('kopsrox', 'vm_cpu', '1')
  kopsrox_config.set('kopsrox', 'vm_ram', '4')

  # cloudinit user and key
  kopsrox_config.set('kopsrox', 'cloudinituser', 'user')
  kopsrox_config.set('kopsrox', 'cloudinitsshkey', 'ssh-rsa cioieocieo')
  # kopsrox network baseip
  kopsrox_config.set('kopsrox', 'network', '192.168.0.160')
  kopsrox_config.set('kopsrox', 'networkgw', '192.168.0.1')

  # cluster level
  kopsrox_config.add_section('cluster')
  kopsrox_config.set('cluster', 'masters', '1')
  kopsrox_config.set('cluster', 'workers', '0')
  kopsrox_config.set('cluster', 'k3s-version', 'v1.24.6+k3s1')

  # write default config
  with open(kopsrox_conf, 'w') as configfile:
    kopsrox_config.write(configfile)
  print('NOTE: please edit', kopsrox_conf, 'as required for your setup')
  exit(0)

# generate a default proxmox.ini
def init_proxmox_ini():

  # proxmox conf
  conf = proxmox_conf
  proxmox_config = ConfigParser()
  proxmox_config.read(conf)
  proxmox_config.add_section('proxmox')

  # need to add port in the future
  proxmox_config.set('proxmox', 'endpoint', 'domain or ip')
  proxmox_config.set('proxmox', 'user', 'root@pam')
  proxmox_config.set('proxmox', 'token_name', 'token name')
  proxmox_config.set('proxmox', 'api_key', 'xxxxxxxxxxxxx')

  # write file
  with open(conf, 'w') as configfile:
    proxmox_config.write(configfile)
  print('NOTE: please edit', conf, 'as required for your setup')
  exit(0)

# proxmox api task blocker
def task_status(proxmox_api, task_id, node_name):
    data = {"status": ""}
    while (data["status"] != "stopped"):
      data = proxmox_api.nodes(node_name).tasks(task_id).status.get()
    #print('d', data)
