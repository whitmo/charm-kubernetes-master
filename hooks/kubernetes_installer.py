import shlex
import subprocess
from path import path


def run(command, shell=False):
    """ A convience method for executing all the commands. """
    print(command)
    if shell is False:
        command = shlex.split(command)
    output = subprocess.check_output(command, shell=shell)
    print(output)
    return output


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
                        'kube-proxy': 'kube-proxy',
                        'kube-scheduler': 'scheduler',
                        'kubectl': 'kubectl',
                        'kubelet': 'kubelet'}
        self.arch = arch
        self.version = version
        self.output_dir = path(output_dir)

    def build(self, branch):
        """ Build kubernetes from a github repository using the Makefile. """
        # Remove any old build artifacts.
        make_clean = 'make clean'
        run(make_clean)
        # Always checkout the master to get the latest repository information.
        git_checkout_cmd = 'git checkout master'
        run(git_checkout_cmd)
        # When checking out a tag, delete the old branch (not master).
        if branch != 'master':
            git_drop_branch = 'git branch -D {0}'.format(self.version)
            rc = subprocess.call(git_drop_branch.split())
            if rc != 0:
                print(rc)
        # Make sure the git repository is up-to-date.
        git_fetch = 'git fetch origin {0}'.format(branch)
        run(git_fetch)

        if branch == 'master':
            git_reset = 'git reset --hard origin/master'
            run(git_reset)
        else:
            # Checkout a branch of kubernetes so the repo is correct.
            checkout = 'git checkout -b {0} {1}'.format(self.version, branch)
            run(checkout)

        # Compile the binaries with the make command using the WHAT variable.
        make_what = "make all WHAT='cmd/kube-apiserver cmd/kubectl "\
                    "cmd/kube-controller-manager plugin/cmd/kube-scheduler "\
                    "cmd/kubelet cmd/kube-proxy'"
        print(make_what)
        rc = subprocess.call(shlex.split(make_what))

    def install(self, install_dir=path('/usr/local/bin')):
        """ Install kubernetes binary files from the output directory. """

        if not install_dir.isdir():
            install_dir.makedirs_p()

        nginx_dir = path('/usr/share/nginx/html')
        web = 'kubernetes/{0}/bin/linux/{1}'.format(self.version, self.arch)
        hosted_dir = nginx_dir / web
        if not hosted_dir.isdir():
            hosted_dir.makedirs_p()
        hosted_dir.chown('www-data', 'www-data')

        # Create the symbolic links to the real kubernetes binaries.
        # This can be removed if the code is changed to call real commands.
        for key, value in self.aliases.iteritems():
            target = self.output_dir / key
            if target.exists():
                link = install_dir / value
                if link.exists():
                    link.remove()
                # Create a symlink to the target.
                target.symlink(link)
                # Copy the target to the hosted directory for the minions.
                target.copy(hosted_dir / key)
            else:
                print('Error target file {0} does not exist.'.format(target))
                exit(1)
