#!/usr/bin/env python3

import os, sys

# use lib dir
sys.path[0:0] = ['lib/']

# check file exists
if not os.path.isfile('kopsrox.ini'):
  import kopsrox_ini as kopsrox_ini
  kopsrox_ini.init_kopsrox_ini()
  exit(0)

# checks config
import kopsrox_config as kopsrox_config

# verbs
import verbs as verbs;
