

# imports
import urllib3, sys, time, re
import common_config as common
from configparser import ConfigParser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from proxmoxer import ProxmoxAPI

# connect to proxmox
def prox_init():

  # read proxmox config
  proxmox_config = ConfigParser()
  proxmox_conf = common.proxmox_conf
  proxmox_config.read(proxmox_conf)

  # check values in config
  endpoint = common.conf_check(proxmox_config,'proxmox','endpoint',proxmox_conf)
  user = common.conf_check(proxmox_config,'proxmox','user',proxmox_conf)
  token_name = common.conf_check(proxmox_config,'proxmox','token_name',proxmox_conf)
  api_key = common.conf_check(proxmox_config,'proxmox','api_key',proxmox_conf)

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
  config = common.read_kopsrox_ini()
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
      print('qaexec: agent not started on', vmid)
      time.sleep(7)

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
    return(pid_check['err-data'])

  # check for err-data
  try:
    if (pid_check['err-data']):
      return(pid_check['err-data'])
  except:
    return(pid_check['out-data'])

# return kopsrox_vms as list
def list_kopsrox_vm():

    # config
    config = common.read_kopsrox_ini()
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
    config = common.read_kopsrox_ini()
    proxnode = (config['proxmox']['proxnode'])
    proximgid = (config['proxmox']['proximgid'])

    # proxinit
    prox = prox_init()
    try:
      poweroff = prox.nodes(proxnode).qemu(vmid).status.stop.post()
      common.task_status(prox, poweroff, proxnode)
      delete = prox.nodes(proxnode).qemu(vmid).delete()
      common.task_status(prox, delete, proxnode)
    except:
      if (int(proximgid) != int(vmid)):
        print('unable to destroy', vmid)
        exit(0)

# clone
def clone(vmid):

    # read config
    config = common.read_kopsrox_ini()

    # normal defines
    proxnode = (config['proxmox']['proxnode'])
    proxstor = (config['proxmox']['proxstor'])
    proximgid = (config['proxmox']['proximgid'])

    # map network info
    networkgw = (config['kopsrox']['networkgw'])
    ip = common.vmip(vmid)

    # vm specs
    cores = (config['kopsrox']['vm_cpu'])
    ram = (config['kopsrox']['vm_ram']) 
    memory = int(int(ram) * 1024)

    # hostname
    hostname = common.vmname(int(vmid))

    # init proxmox
    prox = prox_init()
   
    # clone
    print('creating:', hostname)
    clone = prox.nodes(proxnode).qemu(proximgid).clone.post(
            newid = vmid,
            )
    common.task_status(prox, clone, proxnode)

    # configure
    configure = prox.nodes(proxnode).qemu(vmid).config.post(
                name = hostname,
                onboot = 1,
                hotplug = 0,
                cores = cores, 
                memory = memory,
                ipconfig0 = ( 'gw=' + networkgw + ',ip=' + ip + '/24' ))
    common.task_status(prox, str(configure), proxnode)

    # power on
    poweron = prox.nodes(proxnode).qemu(vmid).status.start.post()
    common.task_status(prox, str(poweron), proxnode)
    time.sleep(5)
