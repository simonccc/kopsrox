#!/usr/bin/env python3

# imports
import time, re

# kopsrox
from kopsrox_config import prox, vmip, masterid
from kopsrox_config import node,network_bridge,cluster_id,vmnames,vm_cpu,vm_ram,vm_disk,network_mask,network_gw,network_dns,network_mtu, network_dns
from kopsrox_kmsg import kmsg

# run a exec via qemu-agent
def qaexec(vmid: int = masterid,cmd = 'uptime'):

  # define kname
  kname = 'proxmox_qaexec'

  # get vmname
  # fixme try?
  vmname = vmnames[vmid]

  # get node
  # fixme try?
  node = get_node(vmid)

  # qagent no yet running check
  qagent_running = 'false'

  # max wait time
  qagent_count = int(1)

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
  pid_status = int(0)

  # loop until command has finish
  # fixme needs a loop counter?
  while pid_status != int(1):
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
    exit(0)

  # check for err-data
  try:

    # if stderr / err-data exists
    if (pid_check['err-data']):

      # print data warning \
      kmsg('qaexec_stderr', ( 'CMD: ' +cmd + '\n' + pid_check['err-data'].strip()), 'err')

      # if there is output return that otherwise exit
      if (pid_check['err-data'] and pid_check['out-data']):
        return(pid_check['out-data'].strip())
      else:
        exit(0)

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

  # if it exists node is ok and we can return the configured node
  if vmid == cluster_id:
    return(node)

  # check for vm id in proxmox cluster
  for vm in prox.cluster.resources.get(type = 'vm'):

    # matching id found
    if vm.get('vmid') == vmid:

      # return node vm is running on
      return(vm.get('node'))

  # error: node not found
  if vmid == masterid:
    kmsg('cluster_error', f'no cluster exists', 'err')
    exit(0)

  # default error
  kmsg('proxmox_get-node', f'node for {vmid} not found', 'err')
  exit(0)

# stop and destroy vm
def prox_destroy(vmid: int):

    kname = 'prox_destroy-vm'

    # get node and vmname
    vmname = vmnames[vmid]
    node = get_node(vmid)

    # if destroying image
    if vmid == cluster_id:
      prox_task(prox.nodes(node).qemu(cluster_id).delete())
      return

    # power off and delete
    try:
      prox_task(prox.nodes(node).qemu(vmid).status.stop.post(),node)
      prox_task(prox.nodes(node).qemu(vmid).delete(),node)
      kmsg(kname, vmname)
    except Exception as e:
      kmsg(kname, f'unable to destroy {node}/{vmid}\n{e}', 'err')
      exit(0)

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
  prox_task(prox.nodes(node).qemu(cluster_id).clone.post(newid = vmid))

  # configure
  prox_task(prox.nodes(node).qemu(vmid).config.post(
    name = hostname,
    onboot = 1,
    cores = vm_cpu,
    memory = memory,
    balloon = '0',
    boot = ('order=scsi0'),
    net0 = (f'model=virtio,bridge={network_bridge},mtu={network_mtu}'),
    ipconfig0 = (f'gw={network_gw},ip={ip}'),
    nameserver = network_dns,
    description = (f'{vmid}:{hostname}:{ip}') 
  ))

  # resize disk
  prox_task(prox.nodes(node).qemu(vmid).resize.put(
    disk = 'scsi0',
    size = f'{vm_disk}G',
  ))

  # power on
  prox_task(prox.nodes(node).qemu(vmid).status.start.post())

  # run uptime / wait for qagent to start
  internet_check(vmid)
  kmsg(f'proxmox_{hostname}', 'ready')

# proxmox task blocker
def prox_task(task_id, node=node):

  # define default status
  status = {"status": ""}

  # until task stopped
  try:
    while (status["status"] != "stopped"):
      status = prox.nodes(node).tasks(task_id).status.get()
  except:
    kmsg('proxmox_task-status', f'unable to get task {task_id} node: {node}', 'err')
    exit(0)

  # if task not completed ok
  if not status["exitstatus"] == "OK":
    kmsg('proxmox_task-status', (f'task exited with non OK status ({status["exitstatus"]})\n' + task_log(task_id)), 'err')
    exit(0)

# returns the task log
def task_log(task_id, node=node):

  # define empty log line
  logline = ''

  # for each value in list
  # assuming task_id is valid
  try:
    for log in prox.nodes(node).tasks(task_id).log.get():

      # append log to logline
      logline += log['t'] + '\n'

    return(logline)
  except:
    kmsg('proxmox_task-log', f'failed to get log for task!', 'err')
    exit(0)

  # return string
  return(logline)

# internet checker
def internet_check(vmid):
  vmname = vmnames[vmid]
  internet_cmd = 'curl -s --retry 2 --retry-all-errors --connect-timeout 1 --max-time 2 www.google.com > /dev/null && echo ok || echo error'
  internet_check = qaexec(vmid, internet_cmd)

  # if curl command fails
  if internet_check == 'error':
    kmsg('prox_netcheck', f'{vmname} internet access check failed', 'err')
    exit(0)
