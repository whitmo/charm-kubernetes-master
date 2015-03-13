#!/bin/bash 
DEBUG=false
if [[ "$1" == "--debug" ]]; then
  DEBUG=true
  set -x
fi
cd /opt/kubernetes/
# Step One Turn up the redis master
kubectl create -f examples/guestbook/redis-master.json 
if [[ "$DEBUG" == true ]]; then
  kubectl get pods
fi
# Step Two: Turn up the master service
kubectl create -f examples/guestbook/redis-master-service.json
if [[ "$DEBUG" == true ]]; then
  kubectl get services
fi
# Step Three: Turn up the replicated slave pods
kubectl create -f examples/guestbook/redis-slave-controller.json 
if [[ "$DEBUG" == true ]]; then
  kubectl get replicationcontrollers
  kubectl get pods
fi
# Step Four: Create the redis slave service
kubectl create -f examples/guestbook/redis-slave-service.json 
if [[ "$DEBUG" == true ]]; then
  kubectl get services
fi
# Step Five: Create the frontend pod
kubectl create -f examples/guestbook/frontend-controller.json
if [[ "$DEBUG" == true ]]; then
  kubectl get replicationcontrollers
  kubectl get pods
fi

echo "# Now run the following commands on your juju client"
echo "juju run --service kubernetes 'open-port 8000'"
echo "juju expose kubernetes"
echo "# Go to the kubernetes public address on port 8000 to see the guestbook application"

