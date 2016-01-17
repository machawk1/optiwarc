"""Base classes for ARC and WARC files.
"""
from cStringIO import StringIO
import gzip2

class BaseRecord:
    def write_to(self, f):
        """Writes this record to the given file.
        
        All the subclasses must implement this method.
        """
        raise NotImplementedError

    def __str__(self):
        """Converts this record into string.
        """
        f = StringIO()
        self.write_to(f)
        return f.getvalue()

class BaseFile:
    """Base class for ARCFile and WARCFile.
    
    This class takes care of details of gzip file or regular file etc.
    The subclasses should implement the following methods.
    
        * read_header
        * read_footer
        * make_record
    """
    def __init__(self, filename=None, mode=None, fileobj=None, compress=None):
        if fileobj is None:
            fileobj = __builtin__.open(filename, mode or "rb")
            mode = fileobj.mode
        # initiaize compress based on filename, if not already specified
        if compress is None and filename and filename.endswith(".gz"):
            compress = True
        
        if compress:
            fileobj = gzip2.GzipFile(fileobj=fileobj, mode=mode)
        
        self.fileobj = fileobj
        
    def read_header(self, f):
        """Reads record header from the given file.

        This is called by read_record method. All the subclasses must implement 
        this method.
        """
        raise NotImplementedError()
        
    def read_footer(self, f):
        """Reads and verifies the record footer from the given file.
        
        Records typically end with one or more CR LF characters, which are not 
        part of the record. Those characters are considers as footer.
        """
        raise NotImplementedError()
        
    def make_record(self, header, payload):
        """Creates and returns a record object from header and payload.
        
        This is called by read_record method. All the subclasses must implement 
        this method.
        """
        raise NotImplementedError()
        
    def _finish_reading_current_record(self):
        # consume the footer from the previous record
        if self._current_payload:
            # consume all data from the current_payload before moving to next record
            self._current_payload.read()
            self.read_footer(self._current_payload.fileobj)
            self._current_payload = None

    def read_record(self):
        pass
        
    def __iter__(self):
        record = self.read_record()
        while record is not None:
            yield record
            record = self.read_record()
        
    def write_record(self, record):
        record.write_to(self.fileobj)
        # Each warc record is written as separate member in the gzip file
        # so that each record can be read independetly.
        if isinstance(self.fileobj, gzip2.GzipFile):
            self.fileobj.close_member()
        
    def browse(self):
        """Utility to browse through the records in the warc file.
        
        This returns an iterator over (record, offset, size) for each record in 
        the file. If the file is gzip compressed, the offset and size will 
        corresponds to the compressed file. 
        
        The payload of each record is limited to 1MB to keep memory consumption 
        under control.
        """
        offset = 0
        for record in self:
            # Just read the first 1MB of the payload.
            # This will make sure memory consuption is under control and it 
            # is possible to look at the first MB of the payload, which is 
            # typically sufficient to read http headers in the payload.
            record.payload = StringIO(record.payload.read(1024*1024))
            self._finish_reading_current_record()
            next_offset = self.tell()
            yield record, offset, next_offset-offset
            offset = next_offset

    def tell(self):
        """Returns the file offset. If this is a compressed file, then the 
        offset in the compressed file is returned.
        """
        if isinstance(self.fileobj, gzip2.GzipFile):
            return self.fileobj.fileobj.tell()
        else:
            return self.fileobj.tell()            
