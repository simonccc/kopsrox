# kopsrox
automate creating a k3s cluster with proxmox api

## reqs
- create a master node and be able to add workers
- be able to size nodes ( cpu / ram ) 
- be able to delete workers safely via cordon and purge
- be able to select which proxmox instance each node gets deployed on
- kubectl level support - should export a local kubeconfig
- generate the image to be used

## ideas
- could it be a fat command to avoid dependencies and other complications?
- load balancer and bastion support?
- private network? what networks mode to support
- cluster config file - multiple clusters?
- 
