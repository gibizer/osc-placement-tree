# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import subprocess
import tempfile

from graphviz import Source
from oslotest import base


class TestBase(base.BaseTestCase):
    VERSION = '1.14'

    @classmethod
    def openstack(cls, cmd, may_fail=False, use_json=False):
        result = None
        try:
            to_exec = ['openstack'] + cmd.split()
            if use_json:
                to_exec += ['-f', 'json']
            if cls.VERSION is not None:
                to_exec += ['--os-placement-api-version', cls.VERSION]

            output = subprocess.check_output(to_exec, stderr=subprocess.STDOUT)
            result = (output or b'').decode('utf-8')
        except subprocess.CalledProcessError as e:
            msg = 'Command: "%s"\noutput: %s' % (' '.join(e.cmd), e.output)
            e.cmd = msg
            if not may_fail:
                raise

        if use_json and result:
            return json.loads(result)
        else:
            return result

    def assertCommandFailed(self, message, func, *args, **kwargs):
        signature = [func]
        signature.extend(args)
        try:
            func(*args, **kwargs)
            self.fail('Command does not fail as required (%s)' % signature)

        except subprocess.CalledProcessError as e:
            self.assertIn(
                message, e.output,
                'Command "%s" fails with different message' % e.cmd)

    def assertDot(self, dot_src):
        """Generates the diagram in the background to verify syntax

        :param dot_src: the dot source string
        """
        dot = Source(dot_src)
        # This will raise CalledProcessError if the given source has a syntax
        # error
        dot.render(tempfile.mktemp())

    def create_rp(self, rp_uuid, parent_rp_uuid=None):
        parent = ('--parent-provider %s' % parent_rp_uuid
                  if parent_rp_uuid else '')
        self.openstack(('resource provider create %(uuid)s --uuid %(uuid)s ' %
                       {'uuid': rp_uuid}) + parent)
        self.addCleanup(lambda: self.delete_rp(rp_uuid))

    def delete_rp(self, rp_uuid):
        self.openstack('resource provider delete %s' % rp_uuid)

    def update_inventory(self, rp_uuid, *resources):
        cmd = 'resource provider inventory set {uuid} {resources}'.format(
            uuid=rp_uuid, resources=' '.join(
                ['--resource %s' % r for r in resources]))
        return self.openstack(cmd, use_json=True)
