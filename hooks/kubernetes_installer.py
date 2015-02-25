import os
import subprocess
from path import path


class KubernetesInstaller():
    """
    This class contains the logic needed to install kuberentes binary files
    from the output directory.
    """

    def __init__(self, arch, version, output_dir):
        """ Gather the required variables for the install. """
        # The kubernetes-master charm needs certain commands to be aliased.
        self.aliases = {'kube-apiserver': 'apiserver',
                        'kube-controller-manager': 'controller-manager',
                        'kube-scheduler': 'scheduler',
                        'kubectl': 'kubectl'}
        self.arch = arch
        self.version = version
        self.output_dir = path(output_dir)

    def install(self, install_dir=path('/usr/local/bin')):
        """ Install kubernetes binary files from the output directory. """

        if not install_dir.exists():
            install_dir.makedirs_p()

        # Create the symbolic links to the real kubernetes binaries.
        # This can be removed if the code is changed to call real commands.
        for key, value in self.aliases.iteritems():
            target = self.output_dir / key
            link = install_dir / value
            if link.exists():
                link.remove()
            target.symlink(link)
