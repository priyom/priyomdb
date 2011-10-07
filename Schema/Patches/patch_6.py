"""
File name: patch_6.py
This file is part of: priyomdb

LICENSE

The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

Alternatively, the contents of this file may be used under the terms of
the GNU General Public license (the  "GPL License"), in which case  the
provisions of GPL License are applicable instead of those above.

FEEDBACK & QUESTIONS

For feedback and questions about priyomdb please e-mail one of the
authors:
    Jonas Wielicki <j.wielicki@sotecware.net>
"""

import os
import os.path

def apply(store):
    # first, drop all existing files
    fileNames = store.execute("SELECT `FileName` FROM `api-fileResources`")
    for fileName in fileNames:
        path = fileName[0]
        if os.path.isfile(path):
            os.unlink(path)
    statements = [
"""TRUNCATE `api-fileResources`;""",
"""ALTER TABLE `api-fileResources` DROP `ReferenceTable`, DROP `LocalID`;""",
"""ALTER TABLE `api-fileResources` ADD `ParameterHash` BINARY(32) NOT NULL AFTER `ResourceType`;""",
"""ALTER TABLE `api-fileResources` ADD UNIQUE (`ResourceType`, `ParameterHash`, `Timestamp`);"""
]
    for statement in statements:
        store.execute(statement)



