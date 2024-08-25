#!/usr/bin/env python3

# functions
from kopsrox_config import prox, local_os_process, image_info, cloud_image_desc, kopsrox_img, k3s_version

# variables
from kopsrox_config import node, storage, cluster_id, cloud_image_url, cluster_name, cloudinitsshkey, cloudinituser, cloudinitpass

# general imports
import wget,sys,os

# proxmox functions
from kopsrox_proxmox import task_status, prox_destroy

# kmsg
from kopsrox_kmsg import kmsg

# define command
cmd = sys.argv[2]
kname = 'image_'

# create image
if cmd == 'create':
  kmsg(f'{kname}create', f'name:{cluster_name}-i1', 'sys')

  # get image name from url 
  cloud_image = cloud_image_url.split('/')[-1]
  kmsg(f'{kname}download', f'{cloud_image_url}')

  # check if image already exists
  if os.path.isfile(cloud_image):
    kmsg(kname, f'{cloud_image} already exists', 'err')
    exit(0)

  # check img can be downloaded
  try:
    wget.download(cloud_image_url)
    print()
  except:
    kmsg(kname, f'unable to download {cloud_image_url}', 'err')
    exit(0)

  # script to install disable selinux on Rocky
  virtc_script = f'''\
curl -v https://get.k3s.io > /k3s.sh 
cat /k3s.sh | \
INSTALL_K3S_SKIP_ENABLE=true \
INSTALL_K3S_SKIP_SELINUX_RPM=true \
INSTALL_K3S_VERSION={k3s_version} \
sh -s - server --cluster-init > /k3s-image-install.log 2>&1

if [ -f /etc/selinux/config ] 
then
  sed -i s/enforcing/disabled/g /etc/selinux/config
fi 

if [ -f /etc/sysconfig/qemu-ga ]
then
  cp /dev/null /etc/sysconfig/qemu-ga 
fi'''
  # shouldn't really need root but run into permissions problems
  patch_cmd = f'sudo virt-customize --smp 2 -m 2048 -a {cloud_image} --install qemu-guest-agent --run-command "{virtc_script}"'

  kmsg('image_virt-customize', 'configuring image')
  patch_out = local_os_process(patch_cmd)

  # destroy template if it exists
  try:
    prox_destroy(cluster_id)
  except:
    pass

  # create new server
  task_status(prox.nodes(node).qemu.post(
    vmid = cluster_id,
    cores = 1,
    memory = 1024,
    bios = 'ovmf',
    efidisk0 = f'{storage}:0',
    machine = 'q35',
    cpu = ('cputype=x86-64-v3'),
    scsihw = 'virtio-scsi-single',
    name = f'{cluster_name}-i0',
    ostype = 'l26',
    scsi2 = (f'{storage}:cloudinit'),
    tags = cluster_name,
    serial0 = 'socket',
    agent = ('enabled=true'),
    hotplug = 0,
    ciupgrade = 0,
    description = f'<pre>{cluster_name} template\n{cloud_image}\n{k3s_version}',
    ciuser = cloudinituser, 
    cipassword = cloudinitpass,
    sshkeys = cloudinitsshkey,
    tdf = '1',
  ))

  # shell to import disk
  # import-from requires the full path os.getcwd required here
  import_cmd = f'''
sudo qm set {cluster_id} --scsi0 {storage}:0,import-from={os.getcwd()}/{cloud_image},iothread=true,aio=native,discard=on,ssd=1 
mv {cloud_image} {cloud_image}.patched'''

  # run shell command to import
  kmsg(f'image_qm-import', f'{cloud_image} > {storage}/{cluster_id}')
  local_os_process(import_cmd)

  # convert to template via create base disk also vm config
  task_status(prox.nodes(node).qemu(cluster_id).template.post())
  task_status(prox.nodes(node).qemu(cluster_id).config.post(template = 1))

# image info
if cmd == 'info':
  image_info()

# destroy image
if cmd == 'destroy':
   kmsg(kname, f'{kopsrox_img()}/{cloud_image_desc}', 'warn')
   prox_destroy(cluster_id)
