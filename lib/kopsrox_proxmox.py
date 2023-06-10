# imports
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time, re, base64

from configparser import ConfigParser
from proxmoxer import ProxmoxAPI

import common_config as common
import kopsrox_ini as ini

# get proxmox config
proxmox_config = ConfigParser()
proxmox_conf = ini.proxmox_conf
proxmox_config.read(proxmox_conf)
endpoint = proxmox_config.get('proxmox', 'endpoint')
user = proxmox_config.get('proxmox', 'user')
token_name = proxmox_config.get('proxmox', 'token_name')
api_key = proxmox_config.get('proxmox', 'api_key')

# api connection
prox = ProxmoxAPI(
        endpoint,
        user=user,
        token_name=token_name,
        token_value=api_key,
        verify_ssl=False,
        timeout=5)

# config
config = common.config
proxnode = (config['proxmox']['proxnode'])
proximgid = (config['proxmox']['proximgid'])
proxstor = (config['proxmox']['proxstor'])

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
      time.sleep(7)
      print('qaexec: agent not started on', vmid)

  # send command
  try: 
    qa_exec = prox.nodes(proxnode).qemu(vmid).agent.exec.post(
            command = "sh -c \'" + cmd +"\'",
            )
  except:
    print('ERROR: qaexec problem with cmd: ', cmd)
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

  # map network info
  networkgw = (config['kopsrox']['networkgw'])
  ip = common.vmip(vmid)

  # vm specs
  cores = (config['kopsrox']['vm_cpu'])
  ram = (config['kopsrox']['vm_ram']) 
  memory = int(int(ram) * 1024)

  # hostname
  hostname = common.vmname(int(vmid))

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
  time.sleep(3)

# proxmox task blocker
def task_status(proxmox_api, task_id, node_name):
  data = {"status": ""}
  while (data["status"] != "stopped"):
    data = proxmox_api.nodes(node_name).tasks(task_id).status.get()
    time.sleep(0.5)

# get vm info
def vm_info(vmid):
  return(prox.nodes(proxnode).qemu(vmid).status.current.get())

# get file
def getfile(vmid, path):
  get_file = prox.nodes(proxnode).qemu(vmid).agent('file-read').get(file = path)
  return(get_file['content'])

# split string by filename length 
def SplitEvery(string, length):

    # if string less than size just return string 
    if len(string) <= length: return [string]

    # create sections count 
    sections = int( int((len(string) / int(length) ) + 1))
    # print(sections, "sections")

    # to be documemnted 
    lines = []
    start = 0;
    for i in range(int(sections)):
        line = string[start:start+length]
        lines.append(line)
        start += length
    return lines

# writes a file to /var/tmp
def writefile(vmid, file):
#  config = common.read_kopsrox_ini()
#  proxnode = (config['proxmox']['proxnode'])

  print('writefile:', file)

  # need to check is in localdir
  myfile = open(file,"rb")

  # read binary file
  file_bin = myfile.read()

  # base64 encode it
  content = (base64.b64encode(file_bin)).decode()

  # split it by the maximum size ( approx ) the api can handle
  lines = SplitEvery(content, int(55825))

  # a counter for the base 64 file names
  count = 1

  # for each line in the base64 file split 
  for line in lines:
    # write file name count.b64encoded.line
    write_file = prox.nodes(proxnode).qemu(vmid).agent('file-write').post(
          file = ( '/var/tmp/' + str(count) +'.'+ file + '.b64'), 
          content = line, 
          encode = 1 )
    # increment file name counter
    count = count + 1

  # command to make the zip file
  make_zip_cmd = ('cat `bin/ls -v /var/tmp/*.b64` | base64 -d > /var/tmp/' + file + ' && rm -f /var/tmp/*.b64 && echo ok')
  make_zip = qaexec(vmid, make_zip_cmd)
  return(write_file)
