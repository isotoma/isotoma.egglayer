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

class Profile(object):

    def __init__(self, profile_name='default'):
        self.profile_name = profile_name
        self.dependencies = []


class PlonePackage(Package):

    def __init__(self, io, name, version):
        Package.__init__(self, io, name, version)
        self.zcml_include_package = []
        self.zcml_include_file = []
        self.profiles = []

    def add_profile(self, profile):
        self.profiles.append(profile)

    def close(self):
        # Advertise this package to Zope
        self.entrypoint('z3c.autoinclude.plugin', 'target', 'plone')

        self.add_code('configure.zcml', self.get_template('plone/configure.zcml.j2'))

        return Package.close(self)



