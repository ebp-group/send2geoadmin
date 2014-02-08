import os
import datetime

def log(txt):
    """Logs fatal errors to a log file if WSGI_LOG env var is defined"""
    log_file = os.environ.get('WSGI_LOG')
    if log_file:
        f = file(log_file, 'a+')
        try:
            f.write(str(datetime.datetime.now()))
            f.write(': ')
            f.write(txt)
        finally:
          f.close()

def get_wsgi_handler(handler_name):
      if not handler_name:
          raise Exception('WSGI_ALT_VIRTUALENV_HANDLER env var must be set')
    
      module, _, callable = handler_name.rpartition('.')
      if not module:
          raise Exception('WSGI_ALT_VIRTUALENV_HANDLER must be set to module_name.wsgi_handler, got %s' % handler_name)
    
      if isinstance(callable, unicode):
          callable = callable.encode('ascii')

      if callable.endswith('()'):
          callable = callable.rstrip('()')
          handler = getattr(__import__(module, fromlist=[callable]), callable)()
      else:
          handler = getattr(__import__(module, fromlist=[callable]), callable)
    
      if handler is None:
          raise Exception('WSGI_ALT_VIRTUALENV_HANDLER "' + handler_name + '" was set to None')
            
      return handler
      
activate_this = os.getenv('WSGI_ALT_VIRTUALENV_ACTIVATE_THIS')
if activate_this is None:
    raise Exception('WSGI_ALT_VIRTUALENV_ACTIVATE_THIS is not set')

log('doing activation' + '\n')
execfile(activate_this, dict(__file__=activate_this))
log('getting handler ' + os.getenv('WSGI_ALT_VIRTUALENV_HANDLER') + '\n')
handler = get_wsgi_handler(os.getenv('WSGI_ALT_VIRTUALENV_HANDLER'))
log('got handler ' + repr(handler))
