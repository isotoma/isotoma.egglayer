from unittest import TestCase
import zipfile
from StringIO import StringIO
from isotoma.egglayer import Package, PlonePackage

class TestPackageUtilities(TestCase):

    def test_get_namespace_packages_0(self):
        p = Package(StringIO(), "test", "1.0")
        self.assertEqual(p.get_namespace_packages(), [])

    def test_get_namespace_packages_1(self):
        p = Package(StringIO(), "test.test1", "1.0")
        self.assertEqual(p.get_namespace_packages(), ["test"])

    def test_get_namespace_packages_2(self):
        p = Package(StringIO(), "test.test1.test2", "1.0")
        self.assertEqual(p.get_namespace_packages(), ["test", "test.test1"])

    def test_get_namespace_packages_3(self):
        p = Package(StringIO(), "test.test1.test2.test3", "1.0")
        self.assertEqual(p.get_namespace_packages(), ["test","test.test1","test.test1.test2"])


class TestPackageBuilding(TestCase):

    def is_namespace_file(self, z, path):
        if not path in z.namelist():
            return False
        return z.open(path).read().strip() == "__import__('pkg_resources').declare_namespace(__name__)"

    def test_empty_package(self):
        s = StringIO()
        p = Package(s, "test", "1.0")
        p.close()

        # Verify all package metadata is present
        self.assertEqual(p.sources, [
            'test-1.0/setup.py',
            'test-1.0/PKG-INFO',
            'test-1.0/test.egg-info/PKG-INFO',
            'test-1.0/test.egg-info/top_level.txt',
            'test-1.0/test.egg-info/namespace_packages.txt',
            'test-1.0/test.egg-info/requires.txt',
            'test-1.0/test.egg-info/entry_points.txt',
            'test-1.0/test.egg-info/not-zip-safe',
            'test-1.0/test.egg-info/dependency_links.txt',
            'test-1.0/test.egg-info/SOURCES.txt'
            ])

        z = zipfile.ZipFile(s)

        # Verify SOURCES.txt is accurate
        SOURCES = ["test-1.0/" + x for x in z.open('test-1.0/test.egg-info/SOURCES.txt').read().splitlines()]
        self.assertEqual(SOURCES, p.sources)

        self.assertEqual(z.open("test-1.0/test.egg-info/entry_points.txt").read().strip(), "")

    def test_empty_namespace_package(self):
        s = StringIO()
        p = Package(s, "test.namespace", "1.0")
        p.close()

        self.assertEqual(p.sources, [
            'test.namespace-1.0/setup.py',
            'test.namespace-1.0/test/__init__.py',
            'test.namespace-1.0/PKG-INFO',
            'test.namespace-1.0/test.namespace.egg-info/PKG-INFO',
            'test.namespace-1.0/test.namespace.egg-info/top_level.txt',
            'test.namespace-1.0/test.namespace.egg-info/namespace_packages.txt',
            'test.namespace-1.0/test.namespace.egg-info/requires.txt',
            'test.namespace-1.0/test.namespace.egg-info/entry_points.txt',
            'test.namespace-1.0/test.namespace.egg-info/not-zip-safe',
            'test.namespace-1.0/test.namespace.egg-info/dependency_links.txt',
            'test.namespace-1.0/test.namespace.egg-info/SOURCES.txt'
            ])

        z = zipfile.ZipFile(s)

        # Verify SOURCES.txt is accurate
        SOURCES = ["test.namespace-1.0/" + x for x in z.open('test.namespace-1.0/test.namespace.egg-info/SOURCES.txt').read().splitlines()]
        self.assertEqual(SOURCES, p.sources)

        self.assert_(self.is_namespace_file(z, "test.namespace-1.0/test/__init__.py"))
        self.assert_(not self.is_namespace_file(z, "test.namespace-1.0/test/namespace/__init__.py"))

        self.assertEqual(z.open("test.namespace-1.0/test.namespace.egg-info/entry_points.txt").read().strip(), "")

    def test_empty_double_namespace_package(self):
        s = StringIO()
        p = Package(s, "test.namespace.another", "1.0")
        p.close()

        self.assertEqual(p.sources, [
            'test.namespace.another-1.0/setup.py',
            'test.namespace.another-1.0/test/__init__.py',
            'test.namespace.another-1.0/test/namespace/__init__.py',
            'test.namespace.another-1.0/PKG-INFO',
            'test.namespace.another-1.0/test.namespace.another.egg-info/PKG-INFO',
            'test.namespace.another-1.0/test.namespace.another.egg-info/top_level.txt',
            'test.namespace.another-1.0/test.namespace.another.egg-info/namespace_packages.txt',
            'test.namespace.another-1.0/test.namespace.another.egg-info/requires.txt',
            'test.namespace.another-1.0/test.namespace.another.egg-info/entry_points.txt',
            'test.namespace.another-1.0/test.namespace.another.egg-info/not-zip-safe',
            'test.namespace.another-1.0/test.namespace.another.egg-info/dependency_links.txt',
            'test.namespace.another-1.0/test.namespace.another.egg-info/SOURCES.txt'
            ])

        z = zipfile.ZipFile(s)

        # Verify SOURCES.txt is accurate
        SOURCES = ["test.namespace.another-1.0/" + x for x in z.open('test.namespace.another-1.0/test.namespace.another.egg-info/SOURCES.txt').read().splitlines()]
        self.assertEqual(SOURCES, p.sources)

        self.assert_(self.is_namespace_file(z, "test.namespace.another-1.0/test/__init__.py"))
        self.assert_(self.is_namespace_file(z, "test.namespace.another-1.0/test/namespace/__init__.py"))
        self.assert_(not self.is_namespace_file(z, "test.namespace.another-1.0/test/namespace/another/__init__.py"))

        self.assertEqual(z.open("test.namespace.another-1.0/test.namespace.another.egg-info/entry_points.txt").read().strip(), "")


class TestPlonePackage(TestCase):

    def test_z3c_auto(self):
        s = StringIO()
        p = PlonePackage(s, "testplone", "0.0")
        p.close()

        z = zipfile.ZipFile(s)

        self.assertEqual(z.open("testplone-0.0/testplone.egg-info/entry_points.txt").read().strip(), "[z3c.autoinclude.plugin]\n\ntarget = plone")

