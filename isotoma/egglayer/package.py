# Copyright 2011 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import zipfile, os
from jinja2 import Environment, PackageLoader

class Package(zipfile.ZipFile):

    def __init__(self, io, name, version):
        zipfile.ZipFile.__init__(self, io, mode='w')
        self.name = name
        self.version = version
        self.requires = []
        self.sources = []
        self.entrypoints = {}

        self.environment = Environment(loader=PackageLoader('isotoma.egglayer'))

    def get_root(self):
        """ All eggs are in a root folder of packagename-version """
        return "%s-%s" % (self.name, self.version)

    def get_prefix(self, name):
        """ Assemble a path by prefixing it with the root path """
        return "%s/%s" % (self.get_root(), name)

    def get_code_prefix(self, name):
        return "%s/%s/%s" % (self.get_root(), self.name.replace(".", os.path.sep), name)

    def get_egginfo_prefix(self, name):
        """ Assemble a path to some metadata in the egg-info directory """
        return "%s/%s/%s" % (self.get_root(), "%s.egg-info" % self.name, name)

    def get_sources(self):
        """ Yields paths relative to the root of the egg """
        for s in self.sources:
            yield os.path.relpath(s, self.get_root())
        yield os.path.relpath(self.get_egginfo_prefix("SOURCES.txt"), self.get_root())

    def get_namespace_packages(self):
        """ Build a namespace_packages.txt """
        parts = []
        name = self.name
        while name.rfind('.') >= 0:
            name = name[:name.rfind('.')]
            parts.append(name)
        parts.reverse()
        return parts

    def get_pkg_info(self):
        """ Build a PKG-INFO file for this package """
        return self.get_template("PKG-INFO.j2")

    def get_setup_py(self):
        return self.get_template("setup.py.j2")

    def get_template(self, tmpl, **context):
        context["package"] = self

        t = self.environment.get_template(tmpl)
        return t.render(**context)

    def writestr(self, name, data, compress_type=None):
        """ We override writestr so we can catalog all files added to the egg """
        if self.fp is None:
            raise RuntimeError("Trying to add to egg after it has been finalized")

        self.sources.append(name)

        # I will probably regret this.
        try:
            data = data.encode("UTF-8")
        except UnicodeError:
            pass

        return zipfile.ZipFile.writestr(self, name, data)

    def add(self, name, data):
        self.writestr(self.get_prefix(name), data)

    def add_code(self, name, data):
        self.writestr(self.get_code_prefix(name), data)

    def add_contents(self, addition):
        for path, data in addition.get_contents():
            self.add(path, data)

    def egginfo(self, name, data):
        self.writestr(self.get_egginfo_prefix(name), data)

    def entrypoint(self, section, key, value):
        self.entrypoints.setdefault(section, []).append((key, value))

    def close(self):
        # If close is called twice don't get upset
        if self.fp is None:
            return

        initpy = self.get_code_prefix("__init__.py")
        if not initpy in self.sources:
            self.add_code("__init__.py", "")

        self.add("setup.py", self.get_setup_py())

        # Generate namespacing __init__.py automatically.
        for ns in self.get_namespace_packages():
            self.add("%s/__init__.py" % (ns.replace(".", "/")), "__import__('pkg_resources').declare_namespace(__name__)")

        # For some reason eggs have 2 PKG-INFO files. Cope with it.
        self.add("PKG-INFO", self.get_pkg_info())
        self.egginfo("PKG-INFO", self.get_pkg_info())

        # The top level package is the package name up to the first '.'
        self.egginfo("top_level.txt", self.name.split(".")[0])

        # Namespace packages: isotoma, isotoma.level1, isotoma.level1.level2
        # New line seperated
        self.egginfo("namespace_packages.txt", "\n".join(self.get_namespace_packages()))

        # Inject the dependencies into the egg info
        self.egginfo("requires.txt", "\n".join(self.requires))

        # Entry points are written into the egg-info
        self.egginfo("entry_points.txt", self.get_template("entry_points.txt.j2"))

        # These files just need to exist
        self.egginfo("not-zip-safe", "")
        self.egginfo("dependency_links.txt", "")

        # Dump a list of all files in the egg into the egg
        self.egginfo("SOURCES.txt", "\n".join(self.get_sources()))

        return zipfile.ZipFile.close(self)


