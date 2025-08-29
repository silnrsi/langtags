
import time, shutil, site
import urllib.request as urlreq
from pathlib import Path
from gzip import GzipFile

class _DefaultErrorHandler(urlreq.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, hdrs):
        result = urlreq.HTTPError(req.get_full_url(), code, msg, hdrs, fp)
        # result.status = code
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
        data = GzipFile(fileobj=response)
    elif ce == 'deflate' or ce is None:
        data = response
    else:
        data = None

    if data is not None and target is not None:
        with open(target, "wb") as target:
            shutil.copyfileobj(data, target)
    return data is not None

class CachedFile:
    def __init__(self, filename, srcpath=None, url=None, prefix=None, stale_period=24*3600):
        self.url = url
        self.filename = filename
        self.srcpath = srcpath
        self.stale = stale_period
        prefix = prefix or "python-cachingurl"
        upath = Path(site.getuserbase()) / prefix
        upath.mkdir(exist_ok=True, parents=True)
        self.cname = upath / filename

    def open(self, *a, **kw):
        fname = self.get_latest()
        return fname.open(*a, **kw)

    def __get_best_local_copy(self):
        try:
            return self.cname, self.cname.stat().st_mtime
        except OSError:
            return self.srcpath, self.srcpath.stat().st_mtime if self.srcpath else 0 

    def get_latest(self):
        cpath, ctime = self.__get_best_local_copy()
        if cpath is None or time.time() - ctime > self.stale:
            if self.url and get_newurl(self.url, ctime, self.cname):
                cpath = self.cname
            else:
                cpath = self.srcpath or self.cname
        return cpath
