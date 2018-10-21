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
import sys

TEST_NAMESPACE = "bba8b4ac-5e1e-5a54-825d-0ebaf96d60b3"


class UUIDSentinels(object):
    def __init__(self, namespace):
        import uuid

        self._uuid_module = uuid
        self.namespace = uuid.UUID(namespace)

    def __getattr__(self, name):
        if name.startswith("__"):
            raise ValueError("Sentinels must not start with __")

        return self._uuid_module.uuid5(self.namespace, name)


sys.modules[__name__] = UUIDSentinels(TEST_NAMESPACE)
