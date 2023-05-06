# kopsrox
automate creating a k3s cluster with proxmox api with a "kops like" cli and cluster config files



## status
- generates a cloneable vm template based on a debian image with qemu-agent patched in via virt-customize
- clones the template to vm's and manages the hostname and IP
- barebone .ini files  are generated and checked against proxmox
- creates a vm as a 'master' ( no k3s yet ) 
- nothing else is working

## in progress
- creating a first master node


## commands
- image [ create | info ] - creates a koprox image / displays when it was created
- cluster [ create | info ] - clones a vm from the template / lists the kopsrox related vms




## problems
- has to run on a proxmox node to run "qm import" 
- needs virt-customize / libguestfs-tools to patch the image for qemu-agent
- user needs sudo qm access
- the api token needs quite high permissions

## done
- logs into proxmox via API
- writes init ini files and does some basic checks
- select which node you want to work with and write to config?
- downloads the cloudinit image
- create an image / template for cloning
- generate the image to be used
- patch the image for qemu-agent 

## reqs
- support a cluster config file, instance type config files etc
- create a master node and be able to add workers
- be able to size nodes ( cpu / ram )
- be able to delete workers safely via cordon and purge
- kubectl level support - should export a local kubeconfig

## ideas
- could it be a fat command to avoid dependencies and other complications?
- load balancer and bastion support?
- private network? what networks mode to support
- multiple clusters?
- etcd on proxmox volume? can we write to them via api? unlikely
- be able to select which proxmox instance each node gets deployed on
