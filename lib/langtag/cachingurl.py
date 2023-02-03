
import time, os, shutil, site
try:
    import urllib.request as urlreq
except ImportError:
    import urllib2 as urlreq

try:
    from gzip import decompress
except ImportError:
    from gzip import GzipFile
    from StringIO import StringIO

    def decompress(dat):
        inf = StringIO(dat)
        return GzipFile(fileobj=inf).read()

class _DefaultErrorHandler(urlreq.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, hdrs):
        result = urlreq.HTTPError(req.get_full_url(), code, msg, hdrs, fp)
        result.status = code
        return result

def get_newurl(url, gmsec, target):
    gmtime = time.gmtime(gmsec)
    hdr = { "If-Modified-Since": time.strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime),
            "Accept-Encoding": "deflate,gzip,identity",
            "Accept": "*/*",
            "User-agent": ""
          }
    r = urlreq.Request(url, headers=hdr)
    opener = urlreq.build_opener(_DefaultErrorHandler())
    response = opener.open(r)
    
    if response.getcode() == 304:
        return True
    if response.getcode() != 200:
        return False
    ce = response.info().get('Content-Encoding')
    if ce == 'gzip':
        data = decompress(response.read())
    elif ce == 'deflate' or ce == 'identity':
        data = response.read()
    else:
        data = None

    if data is not None and target is not None:
        with open(target, "wb") as outf:
            outf.write(data)
    return True

class CachedFile:
    def __init__(self, filename, srcdir=None, url=None, prefix=None):
        self.url = url
        self.filename = filename
        self.srcdir = srcdir
        udir = site.getuserbase()
        self.prefix = prefix if prefix is not None else "python-cachingurl"
        upath = os.path.join(udir, self.prefix)
        if not os.path.exists(upath):
            os.makedirs(upath)
        self.cname = os.path.join(upath, filename)

    def open(self, *a, **kw):
        fname = self.get_latest()
        return open(fname, *a, **kw)

    def _get_ctime(self):
        try:
            ctime = os.path.getmtime(self.cname)
        except OSError:
            ctime = 0
        if ctime == 0 and self.srcdir is not None:
            srcfile = os.path.join(self.srcdir, self.filename)
            if os.path.exists(srcfile):
                shutil.copy2(srcfile, self.cname)
                ctime = os.path.getmtime(self.cname)
        return ctime

    def get_latest(self):
        ctime = self._get_ctime()
        srcfile = os.path.join(self.srcdir, self.filename)
        if self.url and get_newurl(self.url, ctime, self.cname):
            pass
        elif self.srcdir and os.path.exists(srcfile) and os.path.getmtime(srcfile) > ctime:
            shutil.copy2(srcfile, self.cname)
        return self.cname

if __name__ == '__main__':
#    t = time.mktime(time.strptime("2019-01-01", "%Y-%m-%d"))
#    get_newurl('https://ldml.api.sil.org/?query=langtags&ext=json', t, "test.json")
    myfile = CachedFile('langtags.json', url='https://ldml.api.sil.org/?query=langtags&ext=json', prefix="python-cachingurl-test")
    print(myfile.get_latest())
