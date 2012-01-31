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

from isotoma.egglayer.package import Package

class Registry(object):

    def __init__(self):
        self.values = {}

    def set(self, name, value):
        self.values[name] = value

    def render(self, pkg):
        return pkg.get_template('plone/registry.xml.j2', registry=self.values)


class PropertiesTool(object):

    def __init__(self):
        self.sheets = {}

    def set(self, sheet, key, value):
        s = self.sheets.setdefault(sheet, {})
        s[key] = value

    def render(self, pkg):
        return pkg.get_template('plone/propertiestool.xml.j2', sheets=self.sheets)


class Properties(object):

    def __init__(self):
        self.properties = {}

    def set(self, key, value):
        self.properties[key] = value

    def render(self, pkg):
        return pkg.get_template('plone/properties.xml.j2', properties=self.properties)


class Profile(object):

    def __init__(self, profile_name='default'):
        self.profile_name = profile_name
        self.dependencies = []
        self.contents = []
        self.registry = Registry()
        self.propertiestool = PropertiesTool()
        self.properties = Properties()

    def add(self, path, contents):
        self.contents.append((path, contents))

    def get_contents(self, pkg):
        for path, contents in self.contents:
            yield self.get_code_prefix("profiles/%s/%s" % (self.profile_name, path)), contents

        if self.registry.values:
            yield "profiles/%s/registry.xml" % self.profile_name, self.registry.render(pkg)

        if self.propertiestool.sheets:
            yield "profiles/%s/propertiestool.xml" % self.profile_name, self.propertiestool.render(pkg)

        if self.properties.properties:
            yield "profiles/%s/properties.xml" % self.profile_name, self.properties.render(pkg)

        yield "profiles/%s/metadata.xml" % self.profile_name, pkg.get_template('plone/metadata.xml.j2', profile=self)


class PlonePackage(Package):

    def __init__(self, io, name, version):
        Package.__init__(self, io, name, version)
        self.zcml_include_package = []
        self.zcml_include_file = []
        self.zcml_stanzas = []
        self.profiles = []

    def add_profile(self, profile):
        self.profiles.append(profile)

    def close(self):
        if self.fp is None:
            return

        initpy = self.get_code_prefix("__init__.py")
        if not initpy in self.sources:
            self.add_code("__init__.py", "def initialize(*args): pass\n")

        for p in self.profiles:
            for path, code in p.get_contents(self):
                self.add_code(path, code)

        if len(self.profiles) > 0:
            self.add_code("profiles.zcml", self.get_template("plone/profiles.zcml.j2"))
            self.zcml_include_file.append("profiles.zcml")

        # Advertise this package to Zope
        self.entrypoint('z3c.autoinclude.plugin', 'target', 'plone')

        self.add_code('configure.zcml', self.get_template('plone/configure.zcml.j2'))

        return Package.close(self)



