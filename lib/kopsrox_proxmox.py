# imports
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time, re, base64

#from configparser import ConfigParser
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
proximgid = config['proxmox']['proximgid']
proxstor = config['proxmox']['proxstor']

# connect to proxmox
def prox_init():
  return prox

# run a exec via qemu-agent
def qaexec(vmid,cmd):

  # qagent no yet running check
  # needs a loop counter and check adding...
  qagent_running = 'false'
  while ( qagent_running == 'false' ):
    try:
      qa_ping = prox.nodes(proxnode).qemu(vmid).agent.ping.post()
      qagent_running = 'true'
    except:
      #print('proxmox::qaexec: agent not started on', vmid)
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
    print('exitcode 127')
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

# return kopsrox_vms as list
def list_kopsrox_vm():

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

    try:

      # power off
      poweroff = prox.nodes(proxnode).qemu(vmid).status.stop.post()
      task_status(prox, poweroff, proxnode)

      # delete
      delete = prox.nodes(proxnode).qemu(vmid).delete()
      task_status(prox, delete, proxnode)

      # map hostname
      vmname = common.vmname(vmid)
      print('proxmox::destroy: ' + vmname)

    except:
      if (int(proximgid) != int(vmid)):
        print('unable to destroy', vmid)
        exit(0)

# clone
def clone(vmid):

  # map network info
  networkgw = (config['kopsrox']['networkgw'])
  netmask  = (config['kopsrox']['netmask'])
  ip = common.vmip(vmid)

  # vm specs
  cores = (config['kopsrox']['vm_cpu'])
  ram = (config['kopsrox']['vm_ram']) 
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
              ipconfig0 = ( 'gw=' + networkgw + ',ip=' + ip + '/'+ netmask ))
  task_status(prox, str(configure), proxnode)

  # power on
  poweron = prox.nodes(proxnode).qemu(vmid).status.start.post()
  task_status(prox, str(poweron), proxnode)

  # sleep for qemu agent to start
  time.sleep(10)

# proxmox task blocker
def task_status(proxmox_api, task_id, node_name):
  data = {"status": ""}
  while (data["status"] != "stopped"):
    data = proxmox_api.nodes(node_name).tasks(task_id).status.get()

# get vm info
def vm_info(vmid):
  return(prox.nodes(proxnode).qemu(vmid).status.current.get())

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
