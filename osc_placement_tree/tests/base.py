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
import os
import tempfile

from graphviz import Source
from oslotest import base


class TestBase(base.BaseTestCase):
    def assertDot(self, dot_src):
        """Generates the diagram in the background to verify syntax

        :param dot_src: the dot source string
        """
        dot = Source(dot_src)
        # This will raise CalledProcessError if the given source has a syntax
        # error

        if "OS_TEST_SAVE_DOT" in os.environ and os.environ["OS_TEST_SAVE_DOT"]:
            file = self.id()
        else:
            file = tempfile.mktemp()
        dot.render(file)
