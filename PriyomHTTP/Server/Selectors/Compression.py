"""
File name: Compression.py
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
from WebStack.Generic import EndOfResponse
import zlib
import cStringIO
import io

class CompressionStream(io.IOBase):
    def __init__(self, target):
        self.target = target

class DeflateCompressionStream(CompressionStream):
    def __init__(self, target, level = 6):
        super(DeflateCompressionStream, self).__init__(target)
        self.zipper = zlib.compressobj(level)
        
    def write(self, b):
        self.target.write(self.zipper.compress(b))
        
    def flush(self, closing = False):
        self.target.write(self.zipper.flush(zlib.Z_FINISH if closing else zlib.Z_SYNC_FLUSH))
        
    def close(self):
        super(DeflateCompressionStream, self).close()
        self.flush(True)
        return self.target

class CompressionSelector(object):
    def __init__(self, resource, level = 6):
        self.level = 6
        self.resource = resource
    
    def disableCompression(self):
        self.compressionEnabled = False
        if isinstance(self.trans.content, CompressionStream):
            self.trans.content = self.trans.content.close()
            self.trans.content.seek(0)
            self.trans.content.truncate(0)
        
    def respond(self, trans):
        self.trans = trans
        self.compressionEnabled = True
        trans.disableCompression = self.disableCompression
        accepted = [s.lstrip().rstrip() for s in (", ".join(trans.get_header_values("Accept-Encoding"))).split(",")]
        exc = None
        try:
            retval = self.resource.respond(trans)
        except EndOfResponse as e:
            exc = e
        if "deflate" in accepted and self.compressionEnabled:
            trans.set_header_value("Content-Encoding", "deflate")
            tmp = trans.content.getvalue()
            trans.content.truncate(0)
            compressor = DeflateCompressionStream(trans.content)
            compressor.write(tmp)
            compressor.close()
            
        if exc is not None:
            raise exc
        
