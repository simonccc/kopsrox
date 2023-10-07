# imports
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time, re, base64

from proxmoxer import ProxmoxAPI

import common_config as common
import kopsrox_ini as ini

# get proxmox config
config = common.config

# define api connection
prox = ProxmoxAPI(
  config['proxmox']['endpoint'],
  user=config['proxmox']['user'],
  token_name=config['proxmox']['token_name'],
  token_value=config['proxmox']['api_key'],
  verify_ssl=False,
  timeout=5)

# config
proxnode = config['proxmox']['proxnode']  
proxbridge = config['proxmox']['proxbridge']  
proximgid = int(config['proxmox']['proximgid'])
proxstor = config['proxmox']['proxstor']

# connect to proxmox
def prox_init():
  return prox

# run a exec via qemu-agent
def qaexec(vmid,cmd):

  # get vmname
  vmname = common.vmname(vmid)

  # get node
  node = get_node(vmid)

  # qagent no yet running check
  qagent_running = 'false'

  # max wait time
  qagent_count = int(0)

  # while variable is false
  while ( qagent_running == 'false' ):
    try:

      # qa ping the vm
      qa_ping = prox.nodes(proxnode).qemu(vmid).agent.ping.post()

      # agent is running 
      qagent_running = 'true'

    # agent not running 
    except:

      # increment counter
      qagent_count += 1

      # exit if longer than 30 seconds
      if qagent_count == 30:
        print('proxmox::qaexec: ERROR: agent not responding on ' + vmname + ': cmd: ', cmd)
        exit(0)

      # sleep 1 second then try again
      time.sleep(1)

  # send command
  # could try redirecting stderr to out since we don't error on stderr
  try: 
    qa_exec = prox.nodes(proxnode).qemu(vmid).agent.exec.post(
            command = "sh -c \'" + cmd +"\'",
            )
  except:
    print('proxmox::qaexec problem with cmd: ', cmd)
    print(qa_exec )
    exit(0)

  # get pid
  pid = qa_exec['pid']

  # loop until command has finish
  pid_status = int(0)
  while ( int(pid_status) != int(1) ):
    try:
      pid_check = prox.nodes(proxnode).qemu(vmid).agent('exec-status').get(pid = pid)
    except:
      print('ERROR: qaexec problem with pid ' + str(pid) + ' cmd:', cmd)
      exit(0)

    # will equal 1 when process is done
    pid_status = pid_check['exited']

  # debug
  # print(pid_check)

  # check for error
  if ( int(pid_check['exitcode']) == 127 ):
    print('exitcode 127', pid_check['err-data'])
    return(pid_check['err-data'])

  # check for err-data
  try:
    if (pid_check['err-data']):
      return(pid_check['err-data'])
  except:
    try:
      if (pid_check['out-data']):
        return(pid_check['out-data'])
    except:
      return('no output')

    # redundant?
    return('error')
    exit(0)

# return kopsrox vms as a dict with node
def list_kopsrox_vm():

  # init dict
  vmids = {}

  # foreach returned vm
  for vm in prox.cluster.resources.get(type = 'vm'):
    vmid = int(vm.get('vmid'))
    node = vm.get('node')

    # magic number ( end of the proxmox id range ) 
    if ((vmid >= proximgid) and (vmid < (proximgid + 10))):
      vmids[vmid] = node

  # return sorted dict
  return(dict(sorted(vmids.items())))

# return the proxnode for a vmid
def get_node(vmid):

  # check for vm id in proxmox cluster
  for vm in prox.cluster.resources.get(type = 'vm'):

    # matching id found
    if vm.get('vmid') == vmid:

      # return node vm is running on
      return(vm.get('node'))

  # error: node not found
  print('proxmox::get_node: ERROR: '+common.vmname(vmid)+'/'+str(vmid)+' not found.')
  exit(0)

# stop and destroy vm
def destroy(vmid):

    # get node and vmname
    proxnode = get_node(vmid)
    vmname = common.vmname(vmid)

    try:

      # power off
      poweroff = prox.nodes(proxnode).qemu(vmid).status.stop.post()
      task_status(prox, poweroff, proxnode)

      # delete
      delete = prox.nodes(proxnode).qemu(vmid).delete()
      task_status(prox, delete, proxnode)

      print('proxmox::destroyed: ' + vmname + ' [' + proxnode + ']')

    except:
      if (proximgid != vmid):
        print('proxmox::destroy: unable to destroy', vmid)
        exit(0)

# clone
def clone(vmid):

  # map network info
  networkgw = config['kopsrox']['networkgw']
  netmask  = config['kopsrox']['netmask']
  ip = common.vmip(vmid)

  # vm specs
  cores = config['kopsrox']['vm_cpu']
  ram = config['kopsrox']['vm_ram'] 
  memory = int(int(ram) * 1024)

  # hostname
  hostname = common.vmname(int(vmid))

  # clone
  print('proxmox::clone:', hostname)
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
              net0 = ('model=virtio,bridge=' + proxbridge),
              ipconfig0 = ( 'gw=' + networkgw + ',ip=' + ip + '/'+ netmask ))
  task_status(prox, str(configure), proxnode)

  # power on
  poweron = prox.nodes(proxnode).qemu(vmid).status.start.post()
  task_status(prox, str(poweron), proxnode)

# proxmox task blocker
def task_status(proxmox_api, task_id, node_name):
  data = {"status": ""}
  while (data["status"] != "stopped"):
    data = proxmox_api.nodes(node_name).tasks(task_id).status.get()

# get vm info
def vm_info(vmid,node):
  return(prox.nodes(node).qemu(vmid).status.current.get())

# get file
def getfile(vmid, path):
  get_file = prox.nodes(proxnode).qemu(vmid).agent('file-read').get(file = path)
  return(get_file['content'])

# writes a file from localdir to path
def writefile(vmid,file,path):
  name = common.vmname(vmid)
  print('proxmox:writefile: ' + name + ':' + path)
  myfile = open(file,"rb")
  file_bin = myfile.read()
  write_file = prox.nodes(proxnode).qemu(vmid).agent('file-write').post(
          file = path, 
          content = file_bin)
  return(write_file)
