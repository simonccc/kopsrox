# kopsrox.ini 

Most values should be obvious and commented in the default kopsrox.ini 

see [SETUP.md](SETUP.md) for API access details


## cluster_id 

`620` - the proxmox id used for the kopsrox image/template and the basis of the cluster

kopsrox uses a simple static id/ip assignment scheme based on the `[proxmox] - proximgid` and `[kopsrox] - network` settings 

For example:

```
[kopsrox]
network = 192.168.0.170

[cluster]
cluster_id = 620
cname = kopsrox
```

|-|vmid|ip|type|host|
|--|--|--|--|--|
|0|620|192.168.0.170|image|kopsrox-i1|
|1|621|192.168.0.171|master 1|kopsrox-m1|
|2|622|192.168.0.172|master 2|kopsrox-m2|
|3|623|192.168.0.173|master 3|kopsrox-m3|
|4|624|192.168.0.174|utility 1|kopsrox-u1|
|5|625|192.168.0.175|worker 1|kopsrox-w1|
|6|626|192.168.0.176|worker 2|kopsrox-w2|
|7|627|192.168.0.177|worker 3|kopsrox-w3|
|8|628|192.168.0.178|worker 4|kopsrox-w4|
|9|629|192.168.0.179|worker 5|kopsrox-w5|

## kopsrox

### cloud_image_url <a name=cloud_image_url>

`https://cloud-images.ubuntu.com/minimal/daily/mantic/current/mantic-minimal-cloudimg-amd64.img` 

url to the cloud image you want to use as the koprox base template. 

during `kopsrox.py image create` this is downloaded and patched via `virt-customise` to install `qemu-guest-agent`

qcow images are also supported. 

Tested images so far: 

https://cdn.amazonlinux.com/os-images/2.0.20240306.2/kvm/amzn2-kvm-2.0.20240306.2-x86_64.xfs.gpt.qcow2
https://mirrors.vinters.com/rocky/9/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2
