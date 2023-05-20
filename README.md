# kopsrox
automate creating a k3s cluster with proxmox api with a "kops like" cli and cluster config files

## status
- generates a cloneable vm template with qemu-agent patched in via virt-customize
- clones the template to vm's and manages vms hostname and IPs per config paramters
- barebone .ini files are generated and checked against proxmox
- creates a k3s cluster with a master node and configurable worker count
- supports kubectl and exporting kubeconfig/k3s token
- nothing else is working

## in progress
- deleting a node when the config is updated
- master slaves

## install
- sudo apt install libguestfs-tools -y
- pip3 install --user -r requirements.txt

## commands
- image - creates a kopsrox image / displays when it was created
- cluster - clones a vm from the template / lists the kopsrox related vms

## problems
- has to run on a proxmox node 'proxnode' to run "qm import" 
- needs virt-customize / libguestfs-tools to patch the image for qemu-agent
- user needs sudo qm access
- the api token needs quite high permissions
- no network customisation?

## done
- logs into proxmox via API
- writes init ini files and does some basic checks
- select which node you want to work with and write to config?
- download the cloudinit image
- create an image / template for cloning
- patch the image for qemu-agent 
- create a master node and be able to add workers
- kubectl level support - should export a local kubeconfig

## reqs
- support a cluster config file, instance type config files etc
- be able to size nodes ( cpu / ram )
- be able to delete workers safely via cordon and purge

## ideas
- could it be a fat command to avoid dependencies and other complications?
- load balancer and bastion support?
- private network? what networks mode to support
- multiple clusters?
- etcd on proxmox volume? can we write to them via api? unlikely
- be able to select which proxmox instance each node gets deployed on
