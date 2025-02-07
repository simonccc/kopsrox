#!/usr/bin/env python3

# functions
from kopsrox_config import * 

# proxmox functions
from kopsrox_proxmox import prox_task, prox_destroy

# define command
cmd = sys.argv[2]
kname = 'image_'

# create image
if cmd == 'create':

  # get image name from url 
  cloud_image = cloud_image_url.split('/')[-1]
  kmsg(f'{kname}create', f'{cloud_image}/{k3s_version} {storage}/{cluster_name}-i0/{cluster_id}', 'sys')

  # check if image already exists
  if os.path.isfile(cloud_image):
    kmsg(f'image_check', f'{cloud_image} already exists - removing', 'warn')
    try:
      os.remove(cloud_image)
      if os.path.isfile(cloud_image):
        exit(0)
    except:
      kmsg(f'{kname}check', f'{cloud_image} cannot delete', 'err')
      exit(0)

  # check img can be downloaded
  try:
    kmsg(f'{kname}wget', f'{cloud_image_url}')
    wget.download(cloud_image_url)
    print()
  except:
    kmsg(f'{kname}check', f'unable to download {cloud_image_url}', 'err')
    exit(0)

  # kubevip
  # open the generic kubevip deployment and patch it with our network_ip in memory
  kv_manifest = open('./lib/kubevip/kubevip.yaml', 'r').read().replace('KOPSROX_IP', network_ip).strip()

  # define the name/location of the patched kubevip 
  kv_yaml = f'./lib/kubevip/{cluster_name}-kubevip.yaml'

  # open the new kubevip path
  kv_write_out = open(kv_yaml, 'w') 

  # write the patched in memory version to file
  kv_write_out.write(kv_manifest)

  # close files
  kv_write_out.close()

  # script to run in kopsrox image
  virtc_script = f'''\
curl -v https://get.k3s.io > /k3s.sh 
cat /k3s.sh | \
INSTALL_K3S_SKIP_ENABLE=true \
INSTALL_K3S_SKIP_START=true \
INSTALL_K3S_SKIP_SELINUX_RPM=true \
INSTALL_K3S_VERSION={k3s_version} \
sh -s - server --cluster-init > /{cluster_name}-image-install.log 2>&1

if [ ! -f /usr/bin/qemu-ga ] 
then
  if [ -f /bin/yum ]  
  then 
    yum install -y qemu-guest-agent
  else
    apt update && apt install qemu-guest-agent -y 
  fi 
fi

if [ -f /etc/selinux/config ] 
then
  sed -i s/enforcing/disabled/g /etc/selinux/config
fi 

if [ -f /etc/sysconfig/qemu-ga ]
then
  cp /dev/null /etc/sysconfig/qemu-ga 
fi

mkdir -p /var/lib/rancher/k3s/server/manifests/
echo '
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |-
    service:
      spec:
        loadBalancerIP: "{network_ip}"' > /var/lib/rancher/k3s/server/manifests/traefik-config.yaml

mkdir -p /etc/rancher/k3s/config.yaml.d/
echo -n '
etcd-s3: true
etcd-snapshot-retention: 14
etcd-s3-region: {region_string}
etcd-s3-endpoint: {s3endpoint}
etcd-s3-access-key: {access_key}
etcd-s3-secret-key: {access_secret}
etcd-s3-bucket: {bucket}
etcd-s3-skip-ssl-verify: true
etcd-snapshot-compress: true'  > /etc/rancher/k3s/config.yaml.d/etcd-backup.yaml

echo -n '
disable:
  - servicelb
disable-network-policy: true
write-kubeconfig-mode: "0600"
disable-cloud-controller: true
disable-network-policy: true
flannel-backend: wireguard-native
tls-san: {network_ip}' > /etc/rancher/k3s/config.yaml
'''
  # shouldn't really need root/sudo but run into permissions problems
  kmsg(f'{kname}virt-customize', 'configuring image')
  virtc_cmd = f'''
sudo virt-customize -a {cloud_image}   \
--run-command "{virtc_script}"  \
--copy-in {kv_yaml}:/var/lib/rancher/k3s/server/manifests/'''
  local_os_process(virtc_cmd)

  # destroy template if it exists
  try:
    prox_destroy(cluster_id)
  except:
    pass

  # define image desc
  img_ts = str(datetime.now())
  image_desc = f'''<pre>
▗▖ ▗▖ ▗▄▖ ▗▄▄▖  ▗▄▄▖▗▄▄▖  ▗▄▖ ▗▖  ▗▖
▐▌▗▞▘▐▌ ▐▌▐▌ ▐▌▐▌   ▐▌ ▐▌▐▌ ▐▌ ▝▚▞▘ 
▐▛▚▖ ▐▌ ▐▌▐▛▀▘  ▝▀▚▖▐▛▀▚▖▐▌ ▐▌  ▐▌  
▐▌ ▐▌▝▚▄▞▘▐▌   ▗▄▄▞▘▐▌ ▐▌▝▚▄▞▘▗▞▘▝▚▖

cluster_name: {cluster_name}
cloud_img: {cloud_image}
k3s_version: {k3s_version}
created: {img_ts}'''

  # create new server
  prox_task(prox.nodes(node).qemu.post(
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
    description = image_desc,
    ciuser = cloudinituser, 
    cipassword = cloudinitpass,
    sshkeys = cloudinitsshkey,
  ))

  # shell to import disk
  # import-from requires the full path os.getcwd required here
  import_cmd = f'''
sudo qm set {cluster_id} --scsi0 {storage}:0,import-from={os.getcwd()}/{cloud_image},iothread=true,aio=io_uring
mv {cloud_image} {cloud_image}.patched'''

  # run shell command to import
  local_os_process(import_cmd)

  # convert to template via create base disk also vm config
  prox_task(prox.nodes(node).qemu(cluster_id).template.post())
  prox_task(prox.nodes(node).qemu(cluster_id).config.post(template = 1))
  kmsg(f'{kname}qm-import', f'done')

# image info
if cmd == 'info':
  image_info()

# destroy image
if cmd == 'destroy':
   kmsg(f'{kname}destroy', f'{kopsrox_img()}/{cloud_image_desc}', 'sys')
   prox_destroy(cluster_id)
