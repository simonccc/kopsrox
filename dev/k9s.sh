c=`grep ^name kopsrox.ini | cut -d ' ' -f3`
k9s --kubeconfig=${c}.kubeconfig
