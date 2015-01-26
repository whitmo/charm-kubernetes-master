from path import Path
import pytest
import sys

d = Path('__file__').parent.abspath() / 'hooks'
sys.path.insert(0, d.abspath())


class TestKubernetesInstaller():

    def makeone(self, *args, **kw):
        from kubernetes_installer import KubernetesInstaller
        return KubernetesInstaller(*args, **kw)

    def test_init(self):
        ki = self.makeone('i386', '3.0.1', 'kubes-master-i386-3.0.1.tar.gz')
        assert ki.arch == 'i386'
