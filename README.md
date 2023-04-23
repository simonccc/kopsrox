# kopsrox
automate creating a k3s cluster with proxmox api with a "kops like" cli and cluster config files

## status
- nothing is working

## todo
- support generation of barebones config and use of verbs
- select which node you want to work with and write to config?
- create an image / template for cloning

## reqs
- support a cluster config file, instance type config files etc
- create a master node and be able to add workers
- be able to size nodes ( cpu / ram )
- be able to delete workers safely via cordon and purge
- kubectl level support - should export a local kubeconfig
- generate the image to be used

## ideas
- could it be a fat command to avoid dependencies and other complications?
- load balancer and bastion support?
- private network? what networks mode to support
- multiple clusters?
- etcd on proxmox volume? can we write to them via api? unlikely
- be able to select which proxmox instance each node gets deployed on
