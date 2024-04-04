# FAQ

__can I migrate the kopsrox vms to other hosts in my proxmox cluster?__

It is mostly supported but a bit untested at the moment

__can I use debian as a base image vs ubuntu?__

I had to switch from debian due to some problem with a discovered interface which was dhcp and caused some network problems. ymmv.

__k3s_mon 30 second timeouts?__

Check network settings - the vms can't connect to the internet

__ListObjectsV2 search parameter metadata not implemented? for etcd snapshots__

got this running v1.26.10+k3s2 with cloudflare - upgrading to v1.27.8+k3s2 resolved this for me

__where is the old demo__

https://asciinema.org/a/597074
