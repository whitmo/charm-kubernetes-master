import os
import shutil
import subprocess
from path import path


class KubernetesInstaller():
    """
    This class contains the logic needed to install kuberentes binary files
    from a tar file or by using gsutil.
    """

    def __init__(self, arch, version, kubernetes_file):
        """ Gather the required variables for the install. """
        # The kubernetes-master charm needs certain commands to be aliased.
        self.aliases = {'kube-apiserver': 'apiserver',
                        'kube-controller-manager': 'controller-manager',
                        'kube-scheduler': 'scheduler',
                        'kubectl': 'kubectl'}
        self.arch = arch
        self.version = version
        self.kubernetes_file = path(kubernetes_file)

    def install(self, output_dir=path('/opt/kubernetes')):
        """ Install kubernetes binary files from the tar file or gsutil. """
        bindir = output_dir / 'bin'
        if bindir.exists():
            for fp in bindir.files():
                fp.remove()

        bindir.makedirs_p()

        kubernetes_repo = 'http://github.com/GoogleCloudPlatform/kubernetes'
        repo_dir = output_dir / 'kubernetes'
        if not repo_dir.exists():
            git_clone = 'git clone {0} {1}'.format(kubernetes_repo, output_dir)
            print(git_clone)
            subprocess.check_call(git_clone.split())

        if self.kubernetes_file.exists():
            # Untar the file to the output directory.
            command = 'tar -xvzf {0} -C {1}'.format(self.kubernetes_file,
                                                    bindir)
            print(command)
            output = subprocess.check_output(command, shell=True)
            print(output)
        else:
            # Get the binaries from the gsutil command.
            self.get_kubernetes_gsutil(bindir)

        # Create the symbolic links to the real kubernetes binaries.
        # This can be removed if the code is changed to call real commands.
        usr_local_bin = path('/usr/local/bin')
        for key, value in self.aliases.iteritems():
            target = output_dir / key
            link = usr_local_bin / value
            if link.exists():
                link.remove()
            target.symlink(link)

    def get_kubernetes_gsutil(self, directory):
        """ Download the kubernetes binary objects from gsutil. """
        uri = 'gs://kubernetes-release/release/{0}/bin/linux/{1}/'.format(
              self.version, self.arch)
        gs_command = 'gsutil cp {0} {1}'
        # Download all the keys in the aliases dictionary to this machine.
        for key in self.aliases:
            # Create the remote target by appending the key to the uri string.
            remote = uri + key
            # Create the local path and file name string.
            local = os.path.join(directory, key)
            command = gs_command.format(remote, local)
            print(command)
            subprocess.check_call(command.split())
