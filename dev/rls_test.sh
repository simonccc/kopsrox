#!/usr/bin/env bash

start_time=$(date +%s)

# vars
CFG="kopsrox.ini"
K="./kopsrox.py"
KC="$K cluster"
KCI="$KC info"
KCC="$KC create"
KCU="$KC update"
KCD="$KC destroy"
KCR="$KC restore"
KI="$K image"
KID="$KI destroy"
KIC="$KI create"
KII="$KI info"
KE="$K etcd"
KEL="$KE list"
KES="$KE snapshot"
KER="$KE restore"
KERL="${KER}-latest"


# change
kc() {
  sed -i /"$1 =/c\\$1 = $2" $CFG
}

# get pods
get_pods="$KC kubectl get pods -A"

# rm kubeconfig and tokend
rm *.kubeconfig
rm *.k3stoken
set -e

echo "START"

# 1 size cluster
$KCD
kc workers 0 ; kc masters 1

# ** 1 MASTER, SNAPSHOT RESTOR
# create image, create and update cluster
( $KIC && $KCC && $KCU ) || exit

# take snapshot , destroy cluster, create, restore
$KES ; $KCD ; $KCC ; $KERL

# ** MULTIPLE MASTERS AND WORKERS TEST
# add a worker and delete it
kc workers 1 ; $KCU ; kc workers 0 ; $KCU

# re add worker
kc workers 2 ; $KCU

# add 3 masters and go back to 1
kc masters 3 ; $KCU ; kc masters 1  ; $KCU

# change back to 1 node
kc masters 1 ; kc workers 0

# ** TEST cluster restore
# destroy cluster
$KCD ; $KCR

finish_time=$(date +%s) 
echo  $((finish_time - start_time)) secs
