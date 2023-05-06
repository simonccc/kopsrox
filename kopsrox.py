#!/usr/bin/env python3

import sys
sys.path[0:0] = ['lib/']

# checks proxmox and kopsrox ini
import kopsrox_config as kopsrox_config

# common functions
import common_config as common
config = common.read_kopsrox_ini()

global proxnode
proxnode = (config['proxmox']['proxnode'])
#print('proxnode in base', proxnode)

# verbs
import verbs as verbs;
