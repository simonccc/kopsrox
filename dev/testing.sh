#set -e
#set -x

# vars
CFG="kopsrox.ini"
K="./kopsrox.py"
KC="$K cluster"
KCC="$KC create"
KCU="$KC update"
KCD="$KC destroy"
KI="$K image"
KID="$KI destroy"
KIC="$KI create"


# change 
kc() {
  sed -i /"$1 =/c\\$1 = $2" $CFG
}

# minimal cluster
MC="kc masters 1 ; kc workers 0"


# recreate 1 node
#./kopsrox.py cluster destroy && ./kopsrox.py cluster create
#$MC ; $KCD ; $KCC


# add a worker and delete it
#kc workers 0 ; $KCU ; kc workers 3 ; $KCU ; kc workers 0 ; $KCU
#kc masters 3 ; $KCU ; kc masters 1  ; $KCU

# image testing stuff
$MC ; $KCD ; $KID ; $KIC ; $KCC
