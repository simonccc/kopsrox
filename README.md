# kopsrox
automate creating a k3s cluster with proxmox api with a "kops like" cli and cluster config files

## status
- barebone .ini files are generated and checked against proxmox
- generates a cloneable vm template with qemu-agent patched in via virt-customize
- clones the template to vm's and manages vms hostname and IPs per config paramters
- creates a k3s cluster with master(s)  and configurable worker count
- supports kubectl and exporting kubeconfig/k3s token
- nodes are added or deleted when the kopsprox.ini file changes

## in progress
- etcd snapshots

## install
- sudo apt install libguestfs-tools -y
- pip3 install --user -r requirements.txt

## commands
- image - creates a kopsrox image / displays when it was created
- cluster - creates and updates a cluster
- etcd - etcd operations eg backup restore etc

## problems
- has to run on a proxmox node to run "qm import" 
- needs virt-customize / libguestfs-tools to patch the image for qemu-agent
- user needs sudo qm access
- the api token needs quite high permissions
- no network customisation

## reqs
- support a cluster config file, instance type config files etc
- be able to size nodes ( cpu / ram )
- better docs / usage / examples

## ideas
- could it be a fat command to avoid dependencies and other complications?
- load balancer and bastion support?
- etcd on proxmox volume? can we write to them via api? unlikely

## will not support
- multiple clusters
- be able to select which proxmox instance each node gets deployed on
- docker
- network customisation beyond current approach
- private networking

## done
- logs into proxmox via API
- writes init ini files and does some basic checks
- select which node you want to work with and write to config?
- create an image / template for cloning
- create a master node and be able to add workers
- kubectl level support - should export a local kubeconfig
- be able to delete workers safely via cordon and purge
