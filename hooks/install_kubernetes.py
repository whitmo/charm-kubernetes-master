#!/usr/bin/python

import os
import shutil
import socket
import subprocess
import sys


class InstallKubernetes()

    # The kubernetes-master charm needs certain commands to be aliased.
    ALIASES = { 'kube-apiserver': 'apiserver',
                'kube-controller-manager': 'controller-manager',
                'kube-scheduler': 'scheduler',
                'kubectl': 'kubectl'}
    # Get the package architecture rather than  kernel architecture (uname -m).
    ARCH = subprocess.check_output(['dpkg', '--print-architecture']).strip()
    CHARM_DIR = os.environ.get('CHARM_DIR', '')
    # Get the version from the configuration
    VERSION = subprocess.check_output(['config-get', 'version']).strip()
    # Create the kubernetes tar name from the version and architecture.
    KUBERNETES_TAR_FILE = 'kubernetes-master-{0}-{1}.tar.gz'.format(VERSION, 
                                                                    ARCH)
    # The kubernetes file could be stored in this charm in the files directory.
    KUBERNETES_FILE = os.path.join(CHARM_DIR, 'files', KUBERNETES_TAR_FILE)
    # The directory to write the kubernetes binary filesn for key in dict out.
    OUTPUT_DIR = '/opt/kubernetes/bin'

    def install():
        """ Install kubernetes binary files based on configuration. """
        if os.path.isdir(OUTPUT_DIR):
            # Remote old content to remain idempotent.
            shutil.rmtree(OUTPUT_DIR)
        # Create the OUTPUT directory.
        os.makedirs(OUTPUT_DIR)

        if os.path.exists(KUBERNETES_FILE):
            # Untar the file.
            command = 'tar -xvzf {0} -C {1}'.format(KUBERNETES_FILE, OUTPUT_DIR)
            print(command)
            output = subprocess.check_output(command.split(), shell=True)
            print(output)
        else:
            # Get the binaries from the gsutil command.
            get_kubernetes_gsutil(OUTPUT_DIR)

        # Create the symbolic links to the real kubernetes binary files.
        # This can be removed if the code is changed to call real commands.
        usr_local_bin = '/usr/local/bin'
        for key, value in ALIASES.iteritems():
            target = os.path.join(OUTPUT_DIR, key)
            link = os.path.join(usr_local_bin, value)
            ln_command = 'ln -s {0} {1}'.format(target, link)
            command = ln_command.format(target, link)
            print(command)
            subprocess.check_call(command.split())


    def get_kubernetes_gsutil(directory):
        """ Download the kubernetes binary objects from gsutil. """
        # Create the URI with the version and architecture.
        uri = 'gs://kubernetes-release/release/{0}/bin/linux/{1}/'.format(VERSION,
                                                                          ARCH)
        gs_command = 'gsutil cp {0} {1}'
        # Download all the keys in the ALIASES dictionary to this machine.
        for key in ALIASES:
            # Create the remote target by appending the key to the uri string.
            remote = uri + key
            # Create the local path and file name string.
            local = os.path.join(directory, key)
            command = gs_command.format(remote, local)
            print(command)
            subprocess.check_call(command.split())


