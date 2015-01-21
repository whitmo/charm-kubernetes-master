#!/bin/bash

# This script downloads a Kubernetes release and packages up the files that
# are needed for this charm.

set -ex

ARCH="amd64"
VERSION="v0.8.1"

download_kubernetes() {
  URL_PREFIX="https://github.com/GoogleCloudPlatform/kubernetes"
  KUBERNETES_URL="${URL_PREFIX}/releases/download/${VERSION}/kubernetes.tar.gz"
  # Remove the previous temporary files to remain idempotent.
  if [ -f /tmp/kubernetes.tar.gz ]; then
    rm /tmp/kubernetes.tar.gz
  fi
  # Download the kubernetes release from the Internet.
  wget --no-verbose --tries 2 -O /tmp/kubernetes.tar.gz $KUBERNETES_URL
}

extract_kubernetes() {
  # Untar the kubernetes release file.
  tar -xvzf /tmp/kubernetes.tar.gz -C /tmp
  # Untar the server linux amd64 package.
  tar -xvzf /tmp/kubernetes/server/kubernetes-server-linux-$ARCH.tar.gz -C /tmp
}

recombine_kubernetes_master() {
  local OUTPUT_FILE=$1
  local OUTPUT_DIR=`dirname $OUTPUT_FILE`
  if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT
  fi
  
  # Change to the directory the binaries are.
  cd /tmp/kubernetes/server/bin/

  # Create a tar file with the binaries that are needed for kubernetes master.
  tar -cvzf $OUTPUT_FILE kube-apiserver kube-controller-manager kubectl kube-scheduler
}

