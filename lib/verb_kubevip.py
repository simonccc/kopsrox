#!/usr/bin/env python3

# functions
from kopsrox_k3s import install_kube_vip

# sys
import sys

# passed command
cmd = sys.argv[2]

# map arg if passed
try:
  arg = sys.argv[3]
except:
  pass

# define kname
kname = 'kubevip_'+cmd

# create utility node
if cmd == 'reinstall':
    install_kube_vip()
