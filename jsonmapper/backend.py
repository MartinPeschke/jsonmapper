from httplib2 import Http
import simplejson
import logging


### local imports
from . import Mapping

log = logging.getLogger(__name__)

class DBMessage(Exception):
    def __init__(self, message, result_key = None):
        self.message = message
        self.result_key = result_key
    def __str__(self):
      return "<DBMessage: '{0}'>".format(self.message)
class DBException(Exception):pass


class RemoteProc(object):
  def __init__(self, remote_path, method, root_key = None, result_cls = None, result_list = False):
    self.remote_path = remote_path
    self.method      = method
    self.root_key    = root_key
    self.result_cls  = result_cls
    self.result_list = result_list
  def __call__(self, backend, data = None, headers = {}):
      return self.call(backend, data, headers)
  def call(self, backend, data = None, headers = {}):
      if isinstance(data, Mapping): data = data.unwrap(sparse = True)
      result = backend.query(url=self.remote_path, method=self.method, data=data, headers=headers)
      if self.root_key:
          result = result.get(self.root_key)
          if not self.result_cls:
            return result
          elif self.result_list:
            return map(self.result_cls.wrap, result) if result else []
          else:
            return self.result_cls.wrap(result)
      else:
        if not self.result_cls:
          return result
        else:
          return self.result_cls.wrap(result)

class AuthenticatedRemoteProc(RemoteProc):
    def __init__(self, remote_path, method, auth_extractor, root_key = None, result_cls = None, result_list = False):
        super(AuthenticatedRemoteProc, self).__init__(remote_path, method, root_key, result_cls, result_list)
        self.auth_extractor = auth_extractor
    def __call__(self, request, data = None):
        backend = request.backend
        return self.call(backend, data, headers = self.auth_extractor(request))






class Backend(object):
  standard_headers = {'Content-Type': 'application/json'}
  def __init__(self, location, http_options = {}):
    self.location = location
    self.http_options = http_options

  def get_full_path(self, path):
    return path
  
  def get_endpoint_url(self, path):
    return "{}{}".format(self.location, path)
  
  def query(self, **options):
    h = Http(**self.http_options)
    method = options.get("method", "GET")
    headers = self.standard_headers.copy()
    headers.update(options.get('headers', {}))
    endpoint = self.get_endpoint_url(options['url'])
    log.debug("Endpoint: %s, Method: %s, Headers: %s", endpoint, method, headers)
    if method == "POST":
      data = simplejson.dumps(options['data'])
      log.debug("DATA: %s", data)
      resp, content = h.request(endpoint, method=method, body = data, headers=headers)
    else:
      resp, content = h.request(endpoint, method=method )
    log.debug("RESULT: %s", content[:5000])
    try:
        result = simplejson.loads(content)
    except simplejson.JSONDecodeError, e:
        raise DBException("Network Error: API has gone away")
    if result['status'] != 0:
        raise DBException("Status: {status} Reason: {errorMessage}".format(**result))
    elif result.get('dbMessage') or result.get('db_message'):
        raise DBMessage(result.get('dbMessage', result.get('db_message')), result)
    else: 
      return result

      
class VersionedBackend(Backend):
  def __init__(self, location, version, http_options = {}):
    self.location = location
    self.version = version
    self.http_options = http_options
  def get_endpoint_url(self, path):
    return "{}/{}{}".format(self.location, self.version, path)
  def get_full_path(self, path):
    return "/api/{}{}".format(self.version, path) # in template javascript, this needs to get past reverse proxy and it is configured to reroute /api/