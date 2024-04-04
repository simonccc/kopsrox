#!/usr/bin/env python3

# imports
import time, re

# functions 
from kopsrox_config import prox, vmip, kmsg_info, kmsg_err, kmsg_vm_info, kmsg_sys, kmsg_warn

# vars
from kopsrox_config import config,node,network_bridge,cluster_id,vmnames,vm_cpu,vm_ram,vm_disk,network_mask,network_gw,network_dns

# kname
kname = 'prox'

# run a exec via qemu-agent
# find out what doesn't call this as an int
def qaexec(vmid,cmd):

  # get vmname
  vmname = vmnames[int(vmid)]

  # get node
  node = get_node(vmid)

  # qagent no yet running check
  qagent_running = 'false'

  # max wait time/
  qagent_count = int(0)

  # while variable is false
  while qagent_running == 'false':
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

  # check for exitcode 127
  if int(pid_check['exitcode']) == 127:
    kmsg_err(('prox-qaexec-'+vmname), pid_check)
    exit()

  # check for err-data
  try:
    # if err-data exists
    if (pid_check['err-data']):
      return(pid_check['err-data'])
  except:
    try:
      # this is where data gets returned for an OK command
      if (pid_check['out-data']):
        # return it minus any line break
        return(pid_check['out-data'].strip())
    except:
      return('no output-' + cmd)

# return the node for a vmid
def get_node(vmid):

  # if it exists node is ok
  if int(vmid) == cluster_id:
    return(node)

  # check for vm id in proxmox cluster
  for vm in prox.cluster.resources.get(type = 'vm'):

    # matching id found
    if vm.get('vmid') == int(vmid):

      # return node vm is running on
      return(vm.get('node'))

  # error: node not found
  kmsg_info('prox_get_node', (vmnames[vmid]+'/'+str(vmid)+' not found'))
  exit(0)

# stop and destroy vm
def destroy(vmid):
    kname = 'prox-destroy'

    # get node and vmname
    vmid = int(vmid)
    vmname = vmnames[vmid]
    node = get_node(vmid)

    # if destroying image
    if vmid == cluster_id:
      task_status(prox.nodes(node).qemu(cluster_id).delete())
      return

    # power off and delete
    try:
      task_status(prox.nodes(node).qemu(vmid).status.stop.post())
      task_status(prox.nodes(node).qemu(vmid).delete())
      kmsg_info(kname, vmname)
    except:
      # is this image check still required?
      if not cluster_id == vmid:
        kmsg_err(kname, f'unable to destroy {vmid}')
        exit()

# clone
def clone(vmid):

  # check where this may called as a str
  vmid = int(vmid)

  # map network info
  ip = vmip(vmid) + '/' + network_mask

  # vm ram convert from G
  memory = vm_ram * 1024

  # hostname
  hostname = vmnames[vmid]
  kmsg_info('prox-clone', f'{hostname} {ip}')

  # clone
  task_status(prox.nodes(node).qemu(cluster_id).clone.post(newid = vmid))

  # configure
  task_status(prox.nodes(node).qemu(vmid).config.post(
    name = hostname,
    onboot = 1,
    cores = vm_cpu,
    memory = memory,
    ipconfig0 = (f'gw={network_gw},ip={ip}'),
    description = (f'{vmid}:{hostname}:{ip}') 
  ))

  # resize disk
  task_status(prox.nodes(node).qemu(vmid).resize.put(
    disk = 'virtio0',
    size = str(vm_disk) + 'G',
  ))

  # power on
  task_status(prox.nodes(node).qemu(vmid).status.start.post())

  # run uptime / wait for qagent to start
  qaexec(vmid, 'uptime')

  # check internet connection
  internet_check(vmid)

# proxmox task blocker
def task_status(task_id, node=node):

  # define default status
  status = {"status": ""}

  # until task stopped
  while (status["status"] != "stopped"):
    status = prox.nodes(node).tasks(task_id).status.get()

  # if task not completed ok
  if not status["exitstatus"] == "OK":
    kmsg_err('prox-task-status', f'task exited with non OK status ({status["exitstatus"]})\n' + task_log(task_id))
    exit(0)

# returns the task log
def task_log(task_id, node=node):

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
  get_file = prox.nodes(node).qemu(vmid).agent('file-read').get(file = path)
  return(get_file['content'])

# internet checker
def internet_check(vmid):
  vmname = vmnames[vmid]
  internet_cmd = 'curl -s --retry 5 --retry-all-errors --connect-timeout 1 www.google.com > /dev/null && echo ok || echo error'
  internet_check = qaexec(vmid, internet_cmd)
  if internet_check == 'error':
    kmsg_err('network-failure', (vmname + ' no internet access'))
    exit()
