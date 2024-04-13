#!/usr/bin/env python3

# imports
import time, re

# kopsrox
from kopsrox_config import prox, vmip, kmsg_vm_info
from kopsrox_config import node,network_bridge,cluster_id,vmnames,vm_cpu,vm_ram,vm_disk,network_mask,network_gw,network_dns,network_mtu, network_dns
from kopsrox_kmsg import kmsg

# run a exec via qemu-agent
# find out what doesn't call this as an int
def qaexec(vmid,cmd):

  # define kname
  kname = 'proxmox_qaexec'

  # get vmname
  vmname = vmnames[int(vmid)]

  # get node
  node = get_node(vmid)

  # qagent no yet running check
  qagent_running = 'false'

  # max wait time
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
        kmsg(kname, f'agent not responding on {vmname} [{node}] cmd: {cmd}', 'err')
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
    kmsg(kname, f'problem running cmd: {cmd}', 'err')
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
      kmsg(kname, f'problem with pid: {pid} {cmd}', 'err')
      exit(0)

    # will equal 1 when process is done
    pid_status = pid_check['exited']

  # check for exitcode 127
  if int(pid_check['exitcode']) == 127:
    kmsg(kname, f'exit code 127: {pid} {cmd}', 'err')
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

  vmid = int(vmid)

  # if it exists node is ok
  if vmid == cluster_id:
    return(node)

  # check for vm id in proxmox cluster
  for vm in prox.cluster.resources.get(type = 'vm'):

    # matching id found
    if vm.get('vmid') == vmid:

      # return node vm is running on
      return(vm.get('node'))

  # error: node not found
  kmsg('proxmox_get-node', f'node for {vmid} not found', 'err')
  exit(0)

# stop and destroy vm
def destroy(vmid):

    kname = 'proxmox_destroy'

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
      kmsg(kname, vmname)
    except:
      # is this image check still required?
      if not cluster_id == vmid:
        kmsg(kname, f'unable to destroy {vmid}', 'err')
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
  kmsg('proxmox_clone', f'{hostname} {ip} {vm_cpu}c/{vm_ram}G ram {vm_disk}G disk')

  # clone
  task_status(prox.nodes(node).qemu(cluster_id).clone.post(newid = vmid))

  # configure
  task_status(prox.nodes(node).qemu(vmid).config.post(
    name = hostname,
    onboot = 1,
    cores = vm_cpu,
    memory = memory,
    net0 = (f'model=virtio,bridge={network_bridge},mtu={network_mtu}'),
    ipconfig0 = (f'gw={network_gw},ip={ip}'),
    nameserver = network_dns,
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
    kmsg('proxmox_task-status', (f'task exited with non OK status ({status["exitstatus"]})\n' + task_log(task_id)), 'err')
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

# internet checker
def internet_check(vmid):
  vmname = vmnames[vmid]
  internet_cmd = 'curl -s --retry 5 --retry-all-errors --connect-timeout 1 www.google.com > /dev/null && echo ok || echo error'
  internet_check = qaexec(vmid, internet_cmd)

  # if curl command fails
  if internet_check == 'error':
    kmsg('proxmox_netcheck', f'{vmname} no internet access')
    exit()
