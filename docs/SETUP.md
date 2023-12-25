## Requirements

- password less sudo access on a proxmox VE host  ( tested up to 8.1.3 ) 
- network with internet access configured in proxmox
- a range of 10 free Proxmox 'vmids' eg 600 to 610
- a range of 10 IP's on your network for kopsrox to work with eg 192.168.0.160 to 192.168.0.170

## Install Packages

- `sudo apt install libguestfs-tools python3-termcolor -y`
- `pip3 install --break-system-packages --user -r requirements.txt`

_installs the required pip packages vs using os packages_

## Generate Proxmox API key

`sudo pvesh create /access/users/root@pam/token/kopsrox`

`sudo pveum acl modify / --roles Administrator --user root@pam  --token 'root@pam!kopsrox'`

Take a note of the token as we'll need this below

## Create kopsrox.ini

run `./kopsrox.py` and an example _kopsrox.ini_ will be generated - you will need to edit this for your setup

Kopsrox uses a simple static id/ip assignments based on `proximgid` and `network` settings eg 

```
[proxmox]
...
proximgid = 620
...
[kopsrox]
...
network = 192.168.0.170
...
```

|-|vmid|ip|type|
|--|--|--|--|
|0|620|-|image|
|1|621|192.168.0.171|master 1|
|2|622|192.168.0.172|master 2|
|3|623|192.168.0.173|master 3|
|4|624|-|spare|
|5|625|192.168.0.175|worker 1|
|6|626|192.168.0.176|worker 2|
|7|627|192.168.0.177|worker 3|
|8|628|192.168.0.178|worker 4|
|9|629|192.168.0.179|worker 5|
