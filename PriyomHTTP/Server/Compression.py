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
        
    def respond(self, trans):
        accepted = [s.lstrip().rstrip() for s in (", ".join(trans.get_header_values("Accept-Encoding"))).split(",")]
        if "deflate" in accepted:
            trans.content = DeflateCompressionStream(trans.content)
            trans.set_header_value("Content-Encoding", "deflate")
        exc = None
        try:
            retval = self.resource.respond(trans)
        except EndOfResponse as e:
            exc = e
        # it is possible that a rollback has been made inbetween;
        # our stream will get killed in that case
        if issubclass(type(trans.content), CompressionStream):
            trans.content = trans.content.close()
        if exc is not None:
            raise exc
        
