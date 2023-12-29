#!/usr/bin/env python3

# imports
import time, re

# common config
import kopsrox_config as kopsrox_config

# functions 
from kopsrox_config import prox, vmip, kmsg_info, kmsg_err, kmsg_vm_info, kmsg_sys, kmsg_warn

# vars
from kopsrox_config import config, proxnode, proxbridge, proximgid, proxstor, vmnames, vm_cpu, vm_ram, networkgw, vm_disk,netmask, networkgw

# run a exec via qemu-agent
def qaexec(vmid,cmd):

  # get vmname
  vmname = vmnames[int(vmid)]

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
      qa_ping = prox.nodes(node).qemu(vmid).agent.ping.post()

      # agent is running 
      qagent_running = 'true'

    # agent not running 
    except:
      # increment counter
      qagent_count += 1

      # exit if longer than 30 seconds
      if qagent_count == 30:
        kmsg_err('prox-qaexec', ('agent not responding on ' + vmname + ' [' + node + '] cmd: ' + cmd))
        exit(0)

      # sleep 1 second then try again
      time.sleep(1)

  # send command
  # could try redirecting stderr to out since we don't error on stderr
  try: 
    qa_exec = prox.nodes(node).qemu(vmid).agent.exec.post(
            command = "sh -c \'" + cmd +"\'",
            )
  except:
    print('proxmox::qaexec problem with cmd: ', cmd)
    print(qa_exec)
    exit(0)

  # get pid
  pid = qa_exec['pid']

  # loop until command has finish
  pid_status = int(0)
  while ( int(pid_status) != int(1) ):
    try:
      pid_check = prox.nodes(node).qemu(vmid).agent('exec-status').get(pid = pid)
    except:
      print('ERROR: qaexec problem with pid ' + str(pid) + ' cmd:', cmd)
      exit(0)

    # will equal 1 when process is done
    pid_status = pid_check['exited']

  # debug
  # print(pid_check)

  # check for exitcode 127
  if ( int(pid_check['exitcode']) == 127 ):
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

# return the proxnode for a vmid
def get_node(vmid):

  # if it exists proxnode is ok
  if int(vmid) == int(proximgid):
    return(proxnode)

  # check for vm id in proxmox cluster
  for vm in prox.cluster.resources.get(type = 'vm'):

    # matching id found
    if vm.get('vmid') == int(vmid):

      # return node vm is running on
      return(vm.get('node'))

  # error: node not found
  print('proxmox::get_node: ERROR: '+vmnames[vmid]+'/'+str(vmid)+' not found.')
  exit(0)

# stop and destroy vm
def destroy(vmid):

    # get node and vmname
    vmname = vmnames[vmid]
    proxnode = get_node(vmid)

    # if destroying image
    if ( int(vmid) == proximgid ):
      task_status(prox.nodes(proxnode).qemu(proximgid).delete())
      return

    # power off and delete
    try:
      task_status(prox.nodes(proxnode).qemu(vmid).status.stop.post())
      task_status(prox.nodes(proxnode).qemu(vmid).delete())
      kmsg_info('prox-destroy', vmname)
    except:
      # is this image check still required?
      if not int(proximgid) == int(vmid):
        kmsg_err('prox-destroy', ('unable to destroy ', vmid))
        exit()

# clone
def clone(vmid):
  vmid = int(vmid)

  # map network info
  ip = vmip(vmid) + '/' + netmask

  # vm ram convert
  memory = int(int(vm_ram) * 1024)

  # hostname
  hostname = vmnames[vmid]
  kmsg_info('prox-clone', hostname)

  # clone
  task_status(prox.nodes(proxnode).qemu(proximgid).clone.post(newid = vmid))

  # configure
  task_status(prox.nodes(proxnode).qemu(vmid).config.post(
    name = hostname,
    onboot = 1,
    cores = vm_cpu,
    memory = memory,
    ipconfig0 = ( 'gw=' + networkgw + ',ip=' + ip ),
    description = ( str(vmid) + ':' + hostname + ':' + ip ) 
  ))

  # resize disk
  task_status(prox.nodes(proxnode).qemu(vmid).resize.put(
    disk = 'virtio0',
    size = vm_disk,
  ))

  # power on and run uptime
  task_status(prox.nodes(proxnode).qemu(vmid).status.start.post())
  qaexec(vmid, 'uptime')

# proxmox task blocker
def task_status(task_id, node=proxnode):

  # define default status
  status = {"status": ""}

  # until task stopped
  while (status["status"] != "stopped"):
    status = prox.nodes(node).tasks(task_id).status.get()

  # if task not completed ok
  if not status["exitstatus"] == "OK":
    kmsg_err('prox-task-status', ('task exited with non OK status (' + status["exitstatus"] + ')\n' + task_log(task_id)))
    exit(0)

# returns the task log
def task_log(task_id, node=proxnode):

  # define empty log line
  logline = ''

  # for each value in list
  for log in prox.nodes(node).tasks(task_id).log.get():

    # append log to logline
    logline += log['t'] + '\n'

  # return string
  return(logline)

# get file
def getfile(vmid, path):
  get_file = prox.nodes(proxnode).qemu(vmid).agent('file-read').get(file = path)
  return(get_file['content'])

# writes a file from localdir to path
# used to write etcd token when restoring
def writefile(vmid,file,path):
  name = vmnames[vmid]
  print('proxmox:writefile: ' + name + ':' + path)
  myfile = open(file,"rb")
  file_bin = myfile.read()
  write_file = prox.nodes(proxnode).qemu(vmid).agent('file-write').post(file = path,content = file_bin)
  return(write_file)
