# whakerpy.httpd module

## List of classes

## Class `UnixPermissions`

### Description

*Class to handle Unix file permission roles (owner, group, others).*

##### Example

    >>> permissions = UnixPermissions()
    >>> "owner" in permissions
    > True


### Public functions

#### is_valid_role

```python
@classmethod
def is_valid_role(cls, role: str) -> bool:
    """Check if the provided role is valid.

        :param role: (str) The role to check among the valid roles.

        """
    return role in cls.__VALID_ROLES
```

*Check if the provided role is valid.*

##### Parameters

- **role**: (*str*) The role to check among the valid roles.

#### owner

```python
@property
def owner(self):
    """Return the 'owner' role."""
    return 'owner'
```

*Return the 'owner' role.*

#### group

```python
@property
def group(self):
    """Return the 'group' role."""
    return 'group'
```

*Return the 'group' role.*

#### others

```python
@property
def others(self):
    """Return the 'others' role."""
    return 'others'
```

*Return the 'others' role.*



### Overloads

#### __iter__

```python
def __iter__(self):
    """Allow iteration over VALID_ROLES."""
    return iter(self.__VALID_ROLES)
```

*Allow iteration over VALID_ROLES.*

#### __enter__

```python
def __enter__(self):
    """Enter the context: Initialize or lock resources if needed."""
    return self
```

*Enter the context: Initialize or lock resources if needed.*

#### __exit__

```python
def __exit__(self, exc_type, exc_value, traceback):
    """Exit the context: Clean up resources or handle exceptions.

        """
    return False
```

*Exit the context: Clean up resources or handle exceptions.*





## Class `FileAccessChecker`

### Description

*Specialized class for checking file permissions on a specified file.*

This class provides methods to check if a user, group, or owner has specific
access rights to a given file, such as read permissions.

Available only for UNIX-based platforms. Instantiating the class on another
platform raises an EnvironmentError.

##### Example

    >>> checker = FileAccessChecker('/path/to/file')
    >>> checker.read_allowed(who='owner')
    > True
    >>> checker.read_allowed(who='group')
    > False


### Constructor

#### __init__

```python
def __init__(self, filename: str):
    """Initialize the FileAccessChecker with a specific file.

    The initialization ensures that the system supports group-related
    functionalities by checking for the availability of the 'grp' module.

    :param filename: (str) Path to the file to check.
    :raises: EnvironmentError: If 'grp' module is not available (invalid platform)
    :raises: FileNotFoundError: If the file does not exist.

    """
    if grp is None:
        raise EnvironmentError("The 'grp' module is not available on this platform.")
    self.__filename = filename
    if os.path.exists(self.__filename) is False:
        raise FileNotFoundError(f'File not found: {self.__filename}')
    self.__file_stat = os.stat(self.__filename)
```

*Initialize the FileAccessChecker with a specific file.*

The initialization ensures that the system supports group-related
functionalities by checking for the availability of the 'grp' module.

##### Parameters

- **filename**: (*str*) Path to the file to check.


##### Raises

- *EnvironmentError*: If 'grp' module is not available (invalid platform)
- *FileNotFoundError*: If the file does not exist.



### Public functions

#### get_filename

```python
def get_filename(self):
    """Return the examined filename."""
    return self.__filename
```

*Return the examined filename.*

#### read_allowed

```python
def read_allowed(self, who: str='others') -> bool:
    """Check if the given persons have read permission on the file.

        "who" is one of the UnixPermission() or a comibation with '&' or '|'
        (but not both). For example 'group&others' checks if both group
        and others have read access; 'owner|group' checks if either owner
        or group has read access; 'owner&group&others' checks if all have
        read access. Forbidden combination is for example:
        'owner&group|others'

        :param who: (str) Can be 'others', 'group', or 'owner', or a combination.
        :return: (bool) True if read permission is granted, False otherwise.
        :raises: ValueError: If 'who' contains invalid roles or syntax.

        """
    with UnixPermissions() as permissions:
        valid_roles = list(permissions)
        role_pattern = '|'.join((re.escape(role) for role in valid_roles))
        expression_pattern = f'^\\s*({role_pattern})(\\s*[\\&\\|]\\s*({role_pattern}))*\\s*$'
        if not re.match(expression_pattern, who):
            raise ValueError(f"Invalid 'who' value or syntax: {who}. Must contain only {valid_roles} with '&' or '|'.")
    if '&' in who and '|' in who:
        raise ValueError("Combination of '&' and '|' is forbidden in the 'who' parameter.")
    or_conditions = who.split('|')
    for or_condition in or_conditions:
        and_roles = or_condition.split('&')
        if all((self.__check_permission_for_role(role.strip()) for role in and_roles)):
            return True
    return False
```

*Check if the given persons have read permission on the file.*

"who" is one of the UnixPermission() or a comibation with '&' or '|'
(but not both). For example 'group&others' checks if both group
and others have read access; 'owner|group' checks if either owner
or group has read access; 'owner&group&others' checks if all have
read access. Forbidden combination is for example:
'owner&group|others'

##### Parameters

- **who**: (*str*) Can be 'others', 'group', or 'owner', or a combination.


##### Returns

- (*bool*) True if read permission is granted, False otherwise.


##### Raises

- *ValueError*: If 'who' contains invalid roles or syntax.



### Protected functions

#### __check_permission_for_role

```python
def __check_permission_for_role(self, role: str) -> bool:
    """Helper function to check permissions for a single role.

        :param role: (str) Who to check permissions for: 'others', 'group', or 'owner'.

        """
    current_uid = os.geteuid()
    current_gid = os.getegid()
    mode = self.__file_stat.st_mode
    owner_uid = self.__file_stat.st_uid
    group_gid = self.__file_stat.st_gid
    if role == 'owner' and current_uid == owner_uid:
        return bool(mode & stat.S_IRUSR)
    elif role == 'group' and current_gid == group_gid:
        return bool(mode & stat.S_IRGRP)
    elif role == 'others':
        return bool(mode & stat.S_IROTH)
    return False
```

*Helper function to check permissions for a single role.*

##### Parameters

- **role**: (*str*) Who to check permissions for: 'others', 'group', or 'owner'.



## Class `BaseResponseRecipe`

### Description

*Base class to create an HTML response content.*




### Constructor

#### __init__

```python
def __init__(self, name='Undefined', tree=None):
    """Create a new ResponseRecipe instance with a default response.

    """
    self._name = name
    self._status = HTTPDStatus()
    self._data = dict()
    if tree is not None and isinstance(tree, HTMLTree):
        self._htree = tree
    else:
        self._htree = HTMLTree(self._name.replace(' ', '_'))
    self.create()
```

*Create a new ResponseRecipe instance with a default response.*





### Public functions

#### page

```python
@staticmethod
def page() -> str:
    """Return the HTML page name. To be overridden."""
    return 'undefined.html'
```

*Return the HTML page name. To be overridden.*

#### get_data

```python
def get_data(self) -> str | bytes:
    """Gets the current data to send to the client following this request.

        :return: (str) The data in the string format or json depending on the type.

        """
    if isinstance(self._data, dict):
        return json.dumps(self._data)
    elif isinstance(self._data, bytes) or isinstance(self._data, bytearray) or isinstance(self._data, str):
        return self._data
    else:
        raise ValueError(f'Unexpected data type to response to the client : {type(self._data)}')
```

*Gets the current data to send to the client following this request.*

##### Returns

- (*str*) The data in the string format or json depending on the type.

#### reset_data

```python
def reset_data(self) -> None:
    """Clear json data of the response.
        This function has to be called after each response send to the client to avoid overflow problems.

        """
    self._data = dict()
```

*Clear json data of the response.*
This function has to be called after each response send to the client to avoid overflow problems.

#### name

```python
@property
def name(self) -> str:
    return self._name
```



#### status

```python
@property
def status(self) -> HTTPDStatus:
    return self._status
```



#### comment

```python
def comment(self, content: str) -> HTMLComment:
    """Add a comment to the body->main.

        :param content: (str) The comment content
        :return: (HTMLComment) the created node

        """
    return self._htree.comment(content)
```

*Add a comment to the body->main.*

##### Parameters

- **content**: (*str*) The comment content


##### Returns

- (HTMLComment) the created node

#### element

```python
def element(self, tag: str='div', ident=None, class_name=None) -> HTMLNode:
    """Add an element node to the body->main.

        :param tag: (str) HTML element name
        :param ident: (str) Identifier of the element
        :param class_name: (str) Value of the class attribute
        :return: (HTMLNode) The created node

        """
    return self._htree.element(tag, ident, class_name)
```

*Add an element node to the body->main.*

##### Parameters

- **tag**: (*str*) HTML element name
- **ident**: (*str*) Identifier of the element
- **class_name**: (*str*) Value of the class attribute


##### Returns

- (HTMLNode) The created node

#### create

```python
def create(self) -> None:
    """Create the fixed page content in HTML. Intended to be overridden.

        This method is intended to be used to create the parts of the tree
        that won't be invalidated when baking.

        """
    pass
```

*Create the fixed page content in HTML. Intended to be overridden.*

This method is intended to be used to create the parts of the tree
that won't be invalidated when baking.

#### bake

```python
def bake(self, events: dict, headers: dict=None) -> str:
    """Return the HTML response after processing the events.

        Processing the events may change the response status. This method is
        invoked by the HTTPD server to construct the response. Given events
        are the information the handler received (commonly with POST).

        :param events: (dict) The requested events to be processed
        :param headers: (dict) The headers of the http request received

        """
    dirty = self._process_events(events, headers=headers)
    if dirty is True:
        self._invalidate()
        self._bake()
    return self._htree.serialize()
```

*Return the HTML response after processing the events.*

Processing the events may change the response status. This method is
invoked by the HTTPD server to construct the response. Given events
are the information the handler received (commonly with POST).

##### Parameters

- **events**: (*dict*) The requested events to be processed
- **headers**: (*dict*) The headers of the http request received



### Private functions

#### _process_events

```python
def _process_events(self, events: dict, **kwargs) -> bool:
    """Process the given events.

        The given event name must match a function of the event's manager.
        Processing an event may change the content of the tree. In that case,
        the `dirty` method must be turned into True: it will invalidate the
        deprecated content (_invalidate) and re-generate a new one (_bake).

        :param events (dict): key=event_name, value=event_value
        :return: (bool)

        """
    self._status.code = 200
    return False
```

*Process the given events.*

The given event name must match a function of the event's manager.
Processing an event may change the content of the tree. In that case,
the `dirty` method must be turned into True: it will invalidate the
deprecated content (_invalidate) and re-generate a new one (_bake).

##### Parameters

- **events (dict)**: key=event_name, value=event_value


##### Returns

- (*bool*)

#### _invalidate

```python
def _invalidate(self):
    """Remove children nodes of the tree. Intended to be overridden.

        Remove the dynamic content of the tree, which will be re-introduced
        when baking.

        If the tree has no dynamic content, this method is un-used.

        """
    pass
```

*Remove children nodes of the tree. Intended to be overridden.*

Remove the dynamic content of the tree, which will be re-introduced
when baking.

If the tree has no dynamic content, this method is un-used.

#### _bake

```python
def _bake(self) -> None:
    """Fill in the HTML page generator. Intended to be overridden.

        If the tree has no dynamic content, this method is un-used.

        This method is baking the "dynamic" content of the page, i.e. it
        should not change the content created by the method create().

        """
    pass
```

*Fill in the HTML page generator. Intended to be overridden.*

If the tree has no dynamic content, this method is un-used.

This method is baking the "dynamic" content of the page, i.e. it
should not change the content created by the method create().



## Class `HTTPDStatus`

### Description

*A status code value of an HTTPD server.*

HTTPD status codes are issued by a server in response to a client's
request made to the server. All HTTP response status codes are
separated into five classes or categories. The first digit of the
status code defines the class of response, while the last two digits
do not have any classifying or categorization role. There are five
classes defined by the standard:

- 1xx informational response – the request was received, continuing process
- 2xx successful – the request was successfully received, understood, and accepted
- 3xx redirection – further action needs to be taken in order to complete the request
- 4xx client error – the request contains bad syntax or cannot be fulfilled
- 5xx server error – the server failed to fulfil an apparently valid request


### Constructor

#### __init__

```python
def __init__(self, code: int=200):
    """Create the private member for the status code.

    Default status code is 200 for an "OK" httpd response.

    """
    self.__scode = self.check(code)
```

*Create the private member for the status code.*

Default status code is 200 for an "OK" httpd response.



### Public functions

#### check

```python
@staticmethod
def check(value):
    """Raise an exception if given status value is invalid.

        :param value: (int) A response status.
        :raises: sppasHTTPDValueError
        :return: (int) value

        """
    try:
        value = int(value)
    except ValueError:
        raise HTTPDValueError(value)
    if value not in HTTPDStatus.HTTPD_STATUS.keys():
        raise HTTPDValueError(value)
    return value
```

*Raise an exception if given status value is invalid.*

##### Parameters

- **value**: (*int*) A response status.


##### Raises

sppasHTTPDValueError


##### Returns

- (*int*) value

#### get

```python
def get(self):
    """Return the status code value (int)."""
    return self.__scode
```

*Return the status code value (int).*

#### set

```python
def set(self, value):
    """Set a new value to the status code.

        :param value: (int) HTTPD status code value.
        :raises: sppasHTTPDValueError

        """
    value = self.check(value)
    self.__scode = value
```

*Set a new value to the status code.*

##### Parameters

- **value**: (*int*) HTTPD status code value.


##### Raises

sppasHTTPDValueError

#### to_html

```python
def to_html(self, encode: bool=False, msg_error: str=None) -> HTMLTreeError | bytes:
    """Create an error HTML page for the instance of status error and return the tree instance (or serialize).

        :param encode: (bool) Optional, False by default, Boolean to know if we serialize the return or not
        :param msg_error: (str) Optional, an error message for more information for the user

        :return: (HTMLTreeError | bytes) the tree error generated, encoded in bytes for response or object instance

        """
    tree = HTMLTreeError(self, msg_error)
    if encode is True:
        return tree.serialize().encode('utf-8')
    else:
        return tree
```

*Create an error HTML page for the instance of status error and return the tree instance (or serialize).*

##### Parameters

- **encode**: (*bool*) Optional, False by default, Boolean to know if we serialize the return or not
- **msg_error**: (*str*) Optional, an error message for more information for the user

##### Returns

- (HTMLTreeError | *bytes*) the tree error generated, encoded in bytes for response or object instance



### Overloads

#### __str__

```python
def __str__(self):
    return str(self.__scode)
```



#### __repr__

```python
def __repr__(self):
    return '{:d} {:s}'.format(self.__scode, HTTPDStatus.HTTPD_STATUS[self.__scode])
```



#### __eq__

```python
def __eq__(self, other):
    return self.__scode == other
```





## Class `HTTPDValueError`

### Description

*:ERROR 0377:.*

Invalid HTTPD status code value '{!s:s}'.


### Constructor

#### __init__

```python
def __init__(self, value):
    self._status = 377
    self.parameter = error(self._status) + error(self._status).format(value)
```





### Public functions

#### get_status

```python
def get_status(self):
    return self._status
```





### Overloads

#### __str__

```python
def __str__(self):
    return repr(self.parameter)
```





## Class `HTTPDHandler`

### Description

*Web-based application HTTPD handler.*

This class is used to handle the HTTP requests that arrive at the server.

This class is instantiated by the server each time a request is received
and then a response is created. This is an HTTPD handler for any Web-based
application server. It parses the request and the headers, then call a
specific method depending on the request type.

In this handler, HTML pages are supposed to not be static. Instead,
they are serialized from an HTMLTree instance -- so not read from disk.
The server contains the page's bakery, the handler is then asking the
server page's bakery to get the html content and response status.

The parent server is supposed to have all the pages as members in a
dictionary, i.e. it's a sppasBaseHTTPDServer. Each page has a bakery
to create the response content. However, this handler can also be used
with any other http.server.ThreadingHTTPServer.

The currently supported HTTPD responses status are:

- 200: OK
- 205: Reset Content
- 403: Forbidden
- 404: Not Found
- 410: Gone
- 418: I'm not a teapot


### Constructor

#### __init__

```python
def __init__(self, request, client_address, server):
    self.request = request
    self.client_address = client_address
    self.server = server
    self.setup()
    try:
        self.handle()
    finally:
        self.finish()
```





### Public functions

#### get_default_page

```python
def get_default_page(self, default: str='index.html') -> str:
    """Retrieve the server default page name.

        This method first checks if the server has a callable 'default' method
        to determine the default page name. If not, it falls back to the
        provided default value.

        :param default: (str) The fallback default page name, if no server-specific
                               method is found. Defaults to "index.html".
        :return: (str) The name of the default page.

        """
    if hasattr(self.server, 'default') and callable(self.server.default):
        return self.server.default()
    return default
```

*Retrieve the server default page name.*

This method first checks if the server has a callable 'default' method
to determine the default page name. If not, it falls back to the
provided default value.

##### Parameters

- **default**: (*str*) The fallback default page name, if no server-specific method is found. Defaults to "index.html".


##### Returns

- (*str*) The name of the default page.

#### do_HEAD

```python
def do_HEAD(self) -> None:
    """Prepare the response to a HEAD request.

        """
    logging.debug('HEAD -- requested: {}'.format(self.path))
    self._set_headers(200)
```

*Prepare the response to a HEAD request.*



#### do_GET

```python
def do_GET(self) -> None:
    """Prepare the response to a GET request.

        """
    logging.debug(' ---- DO GET -- requested: {}'.format(self.path))
    handler_utils = HTTPDHandlerUtils(self.headers, self.path, self.get_default_page())
    self.path = handler_utils.get_path()
    mime_type = HTTPDHandlerUtils.get_mime_type(self.path)
    if os.path.exists(handler_utils.get_path()) or os.path.exists(handler_utils.get_path()[1:]):
        content, status = handler_utils.static_content(self.path[1:])
    elif mime_type == 'text/html':
        content, status = self._bakery(handler_utils, dict(), mime_type)
    else:
        content, status = handler_utils.static_content(self.path[1:])
    self._response(content, status.code, mime_type)
```

*Prepare the response to a GET request.*



#### do_POST

```python
def do_POST(self) -> None:
    """Prepare the response to a POST request.

        """
    logging.debug(' ----- DO POST -- requested: {}'.format(self.path))
    handler_utils = HTTPDHandlerUtils(self.headers, self.path, self.get_default_page())
    self.path = handler_utils.get_path()
    events, accept = handler_utils.process_post(self.rfile)
    content, status = self._bakery(handler_utils, events, accept)
    self._response(content, status.code, accept)
```

*Prepare the response to a POST request.*



#### log_request

```python
def log_request(self, code='-', size='-') -> None:
    """Override. For a quiet handler pls!!!."""
    pass
```

*Override. For a quiet handler pls!!!.*



### Private functions

#### _set_headers

```python
def _set_headers(self, status: int, mime_type: str=None) -> None:
    """Set the HTTPD response headers.

        :param status: (int) A response status.
        :param mime_type: (str) The mime type of the file response
        :raises: sppasHTTPDValueError

        """
    status = HTTPDStatus.check(status)
    self.send_response(status)
    if mime_type is not None:
        self.send_header('Content-Type', mime_type)
    self.end_headers()
```

*Set the HTTPD response headers.*

##### Parameters

- **status**: (*int*) A response status.
- **mime_type**: (*str*) The mime type of the file response


##### Raises

sppasHTTPDValueError

#### _response

```python
def _response(self, content, status: int, mime_type: str=None) -> None:
    """Make the appropriate HTTPD response.

        :param content: (bytes|iterator) The HTML response content or an iterator
                        yielding chunks of bytes.
        :param status: (int) The HTTPD status code of the response.
        :param mime_type: (str) The mime type of the file response.

        """
    self._set_headers(status, mime_type)
    if isinstance(content, types.GeneratorType) is True:
        for chunk in content:
            self.wfile.write(chunk)
    else:
        self.wfile.write(content)
    if status == 410:
        self.server.shutdown()
```

*Make the appropriate HTTPD response.*

##### Parameters

- **content**: (*bytes*|iterator) The HTML response content or an iterator yielding chunks of bytes.
- **status**: (*int*) The HTTPD status code of the response.
- **mime_type**: (*str*) The mime type of the file response.

#### _bakery

```python
def _bakery(self, handler_utils: HTTPDHandlerUtils, events: dict, mime_type: str) -> tuple:
    """Process the events and return the html page content or json data and status.

        :param handler_utils: (HTTPDhandlerUtils)
        :param events: (dict) key=event name, value=event value
        :param mime_type: (str) The mime type of the file response
        :return: tuple(bytes, HTTPDStatus) the content of the response the httpd status

        """
    if hasattr(self.server, 'page_bakery') is False:
        return handler_utils.static_content(self.path[1:])
    content, status = self.server.page_bakery(handler_utils.get_page_name(), self.headers, events, handler_utils.has_to_return_data(mime_type))
    return (content, status)
```

*Process the events and return the html page content or json data and status.*

##### Parameters

- **handler_utils**: (HTTPDhandlerUtils)
- **events**: (*dict*) key=event name, value=event value
- **mime_type**: (*str*) The mime type of the file response


##### Returns

- tuple(*bytes*, HTTPDStatus) the content of the response the httpd status



## Class `HTTPDHandlerUtils`

### Constructor

#### __init__

```python
def __init__(self, headers: HTTPMessage | dict, path: str, default_page: str='index.html'):
    """Instantiate class, filter the path for getters method and get the headers data

    :param headers: (HTTPMessage|dict) the headers of the request
    :param path: (str) the brut path get by the request
    :param default_page: (str) optional parameter, default page when the page doesn't specify it

    """
    self.__path, self.__page_name = HTTPDHandlerUtils.filter_path(path, default_page)
    self.__headers = dict()
    if isinstance(headers, HTTPMessage) is True or isinstance(headers, dict) is True:
        self.__headers = headers
    else:
        raise TypeError('The headers parameter has to be a dictionary or HTTPMessage class!')
```

Instantiate class, filter the path for getters method and get the headers data

##### Parameters

- **headers**: (HTTPMessage|*dict*) the headers of the request
- **path**: (*str*) the brut path get by the request
- **default_page**: (*str*) optional parameter, default page when the page doesn't specify it



### Public functions

#### get_path

```python
def get_path(self) -> str:
    """Get the path of the request after filtered true path in constructor.

        :return: (str) the path

        """
    return self.__path
```

*Get the path of the request after filtered true path in constructor.*

##### Returns

- (*str*) the path

#### get_page_name

```python
def get_page_name(self) -> str:
    """Get the name of the page after filtered path in constructor.

        :return: (str) the page name ask by the request

        """
    return self.__page_name
```

*Get the name of the page after filtered path in constructor.*

##### Returns

- (*str*) the page name ask by the request

#### static_content

```python
def static_content(self, filepath: str) -> tuple:
    """Return the content of a static file and update the corresponding status.

        This method checks the existence of the file and its permissions before
        returning its content. If the file does not exist or is a directory,
        an appropriate HTTP status and message will be logged.

        :param filepath: (str) The path of the file to return.
        :return: (tuple[bytes|iterator, HTTPDStatus]) A tuple containing the file content
                 in bytes and the corresponding HTTP status.

        """
    if os.path.exists(filepath) is False:
        return self.__log_and_status(404, filepath, 'File not found')
    if os.path.isfile(filepath) is False:
        return self.__log_and_status(403, filepath, 'Folder access is not granted')
    try:
        p = UnixPermissions()
        checker = FileAccessChecker(filepath)
        if checker.read_allowed(who=f'{p.group}&{p.others}') is False:
            return self.__log_and_status(403, filepath, 'Attempted access to non-allowed file')
    except EnvironmentError:
        pass
    try:
        content = self.__open_file_to_binary(filepath)
        return (content, HTTPDStatus(200))
    except Exception as e:
        status = HTTPDStatus(500)
        return (status.to_html(encode=True, msg_error=str(e)), status)
```

*Return the content of a static file and update the corresponding status.*

This method checks the existence of the file and its permissions before
returning its content. If the file does not exist or is a directory,
an appropriate HTTP status and message will be logged.

##### Parameters

- **filepath**: (*str*) The path of the file to return.


##### Returns

- (*tuple*[*bytes*|iterator, HTTPDStatus]) A tuple containing the file content in bytes and the corresponding HTTP status.

#### process_post

```python
def process_post(self, body: BufferedReader) -> tuple[dict, str]:
    """Process the request body to return events and accept mime type.

        :param body: (BufferedReader) The body buffer of the request (rfile)
        :return: (dict, str) the body and accept mime type

        """
    html_mime = 'text/html'
    events = dict()
    accept_type = html_mime
    if self.__headers.get('REQUEST_METHOD', 'POST').upper() == 'POST':
        events = self.__extract_body_content(body)
        accept_type = self.__get_headers_value('Accept', 'text/html')
        if html_mime in accept_type:
            accept_type = html_mime
        token = self.__get_headers_value('X-Auth-Token')
        if token is not None:
            events['token'] = token.replace('Bearer ', '')
    return (events, accept_type)
```

*Process the request body to return events and accept mime type.*

##### Parameters

- **body**: (BufferedReader) The body buffer of the request (rfile)


##### Returns

- (*dict*, *str*) the body and accept mime type

#### get_mime_type

```python
@staticmethod
def get_mime_type(filename: str) -> str:
    """Return the mime type of given file name or path.

        :param filename: (str) The name or path of the file
        :return: (str) The mime type of the file or 'unknown' if we can't find the type

        """
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type is None:
        return 'unknown'
    else:
        return mime_type
```

*Return the mime type of given file name or path.*

##### Parameters

- **filename**: (*str*) The name or path of the file


##### Returns

- (*str*) The mime type of the file or 'unknown' if we can't find the type

#### filter_path

```python
@staticmethod
def filter_path(path: str, default_path: str='index.html') -> tuple[str, str]:
    """Parse the path to return the correct filename and page name.

        :param path: (str) The path obtain from the request or environ
        :param default_path: (str) The default path to add if the path ends with '/'
        :return: (tuple[str, str]) the requested filename and the requested page name

        """
    path = unquote(path)
    if '?' in path:
        path = path[:path.index('?')]
    if len(path) == 0:
        return (f'/{default_path}', default_path)
    filepath = path
    page_name = os.path.basename(path)
    _, extension = os.path.splitext(path)
    if len(page_name) == 0 or len(extension) == 0:
        page_name = default_path
        if filepath.endswith('/'):
            filepath += default_path
    return (filepath, page_name)
```

*Parse the path to return the correct filename and page name.*

##### Parameters

- **path**: (*str*) The path obtain from the request or environ
- **default_path**: (*str*) The default path to add if the path ends with '/'


##### Returns

- (*tuple*[*str*, *str*]) the requested filename and the requested page name

#### has_to_return_data

```python
@staticmethod
def has_to_return_data(accept_type: str) -> bool:
    """Determine the type of the server return: True for data.

        Determine if the server should return data (e.g., JSON, image, video,
        etc.) instead of an HTML page based on the 'Accept' header's MIME type.

        :param accept_type: (str) The MIME type of the 'Accept' header request
        :return: (bool) True if the server should return data, False if HTML content is expected

        """
    data_types = ['application/json', 'image/', 'video/', 'audio/', 'application/ogg']
    for d in data_types:
        if accept_type.startswith(d) is True:
            return True
    return False
```

*Determine the type of the server return: True for data.*

Determine if the server should return data (e.g., JSON, image, video,
etc.) instead of an HTML page based on the 'Accept' header's MIME type.

##### Parameters

- **accept_type**: (*str*) The MIME type of the 'Accept' header request


##### Returns

- (*bool*) True if the server should return data, False if HTML content is expected

#### bakery

```python
@staticmethod
def bakery(pages: dict, page_name: str, headers: dict, events: dict, has_to_return_data: bool=False) -> tuple[bytes, HTTPDStatus]:
    """Process received events and bake the given page.

        :param pages: (dict) A dictionary with key=page_name and value=ResponseRecipe
        :param page_name: (str) The current page name
        :param headers: (dict) The headers of the http request
        :param events: (dict) The events extract from the request (only for POST request, send empty dict for GET)
        :param has_to_return_data: (bool) False by default, Boolean to know if we have to return the html page or data
        :return: (tuple[bytes, HTTPDStatus]) The content to answer to the client and the status of the response

        """
    response = pages.get(page_name)
    if response is None:
        status = HTTPDStatus(404)
        return (status.to_html(encode=True, msg_error=f'Page not found: {page_name}'), status)
    content = bytes(response.bake(events, headers=headers), 'utf-8')
    if has_to_return_data is True:
        content = response.get_data()
        if isinstance(content, (bytes, bytearray)) is False:
            content = bytes(content, 'utf-8')
        response.reset_data()
    status = response.status
    if isinstance(status, int):
        status = HTTPDStatus(status)
    elif hasattr(status, 'code') is False:
        raise TypeError(f'The status has to be an instance of HTTPDStatus or int.Got {status} instead.')
    return (content, status)
```

*Process received events and bake the given page.*

##### Parameters

- **pages**: (*dict*) A dictionary with key=page_name and value=ResponseRecipe
- **page_name**: (*str*) The current page name
- **headers**: (*dict*) The headers of the http request
- **events**: (*dict*) The events extract from the request (only for POST request, send empty dict for GET)
- **has_to_return_data**: (*bool*) False by default, Boolean to know if we have to return the html page or data


##### Returns

- (*tuple*[*bytes*, HTTPDStatus]) The content to answer to the client and the status of the response

#### build_default_headers

```python
@staticmethod
def build_default_headers(filepath: str, content=None, browser_cache=False, varnish=False) -> list:
    """Build HTTP response headers for the requested file.

        This method generates the HTTP headers necessary for serving a file,
        including its MIME type and cache-control directives.

        :param filepath: (str) The absolute or relative path to the requested static file.
        :param content: (bytes|iterator|None) The content of the requested file.
        :param browser_cache: (bool) Whether the browser cache is enabled or not.
                        If False, browser caching is explicitly disabled.
        :param varnish: (bool) Indicates whether the server should enable Varnish cache.
                        If False, server caching is explicitly disabled.
        :return: (list) A list of tuples representing the HTTP response headers.

        """
    cache = list()
    if browser_cache is False:
        cache.append('no-cache')
        cache.append('no-store')
        cache.append('must-revalidate')
    if varnish is False:
        cache.append('max-age=0')
    headers = [('Content-Type', HTTPDHandlerUtils.get_mime_type(filepath))]
    if len(cache) > 0:
        headers.append(('Cache-Control', ','.join(cache)))
        headers.append(('Pragma', 'no-cache'))
        headers.append(('Expires', '0'))
    if isinstance(content, types.GeneratorType) is True:
        content_length, content = HTTPDHandlerUtils.getsize_from_iterator(content)
        headers.append(('Content-Length', str(content_length)))
    return headers
```

*Build HTTP response headers for the requested file.*

This method generates the HTTP headers necessary for serving a file,
including its MIME type and cache-control directives.

##### Parameters

- **filepath**: (*str*) The absolute or relative path to the requested static file.
- **content**: (*bytes*|iterator|None) The content of the requested file.
- **browser_cache**: (*bool*) Whether the browser cache is enabled or not. If False, browser caching is explicitly disabled.
- **varnish**: (*bool*) Indicates whether the server should enable Varnish cache. If False, server caching is explicitly disabled.


##### Returns

- (*list*) A list of tuples representing the HTTP response headers.

#### getsize_from_iterator

```python
@staticmethod
def getsize_from_iterator(iterator):
    """Calculate the total size of data from an iterator.

        :param iterator: (iterable) The iterator to calculate the size of.

        :return: (tuple)
                - total_size (int): The total size in bytes.
                - new_iterator (generator): A new iterator with the same content.
        """
    chunks = list(iterator)
    total_size = sum((len(chunk) for chunk in chunks))

    def recreate_iterator():
        for chunk in chunks:
            yield chunk
    return (total_size, recreate_iterator())
```

*Calculate the total size of data from an iterator.*

##### Parameters

- **iterator**: (iterable) The iterator to calculate the size of.

##### Returns

- (*tuple*) - total_size (int): The total size in bytes. - new_iterator (generator): A new iterator with the same content.

#### recreate_iterator

```python
def recreate_iterator():
    for chunk in chunks:
        yield chunk
```



#### file_iterator

```python
def file_iterator():
    with open(filepath, 'rb') as fp:
        chunk = fp.read(8192)
        while chunk:
            yield chunk
            chunk = fp.read(8192)
```





### Protected functions

#### __log_and_status

```python
def __log_and_status(self, code: int, filepath: str, msg: str) -> tuple[bytes, HTTPDStatus]:
    """Log the error message and return the corresponding HTTP status.

        This method logs the provided message along with the file path and
        returns an HTML error message with the appropriate HTTP status.

        :param code: (int) The HTTP status code to return.
        :param filepath: (str) The path of the file related to the error.
        :param msg: (str) The message to log regarding the error.
        :return: (tuple[str, HTTPDStatus]) A tuple containing the HTML error
                 message and the corresponding HTTP status.

        """
    status = HTTPDStatus(code)
    logging.error(f'{msg}: {filepath}')
    msg = f'{msg}: {os.path.basename(filepath)}'
    return (status.to_html(encode=True, msg_error=msg), status)
```

*Log the error message and return the corresponding HTTP status.*

This method logs the provided message along with the file path and
returns an HTML error message with the appropriate HTTP status.

##### Parameters

- **code**: (*int*) The HTTP status code to return.
- **filepath**: (*str*) The path of the file related to the error.
- **msg**: (*str*) The message to log regarding the error.


##### Returns

- (*tuple*[*str*, HTTPDStatus]) A tuple containing the HTML error message and the corresponding HTTP status.

#### __get_headers_value

```python
def __get_headers_value(self, key: str, default_value: object=None) -> object:
    """Get headers value for a given key, try different keys format depending on server (httpd or wsgi).

        :param key: (str) the header key
        :param default_value: (object) optional parameter, value returned if the header doesn't contain the key
        :return: (object) the value in the header or the default value

        """
    value = self.__headers.get(key)
    if value is None:
        new_key = key.upper().replace('-', '_')
        value = self.__headers.get(new_key)
        if value is None:
            new_key = 'HTTP_' + new_key
            value = self.__headers.get(new_key)
            if value is None:
                return default_value
    return value
```

*Get headers value for a given key, try different keys format depending on server (httpd or wsgi).*

##### Parameters

- **key**: (*str*) the header key
- **default_value**: (*object*) optional parameter, value returned if the header doesn't contain the key


##### Returns

- (*object*) the value in the header or the default value

#### __open_file_to_binary

```python
def __open_file_to_binary(self, filepath: str) -> bytes:
    """Open and read the given file and transform the content to bytes value.

        :param filepath: (str) The path of the file to read
        :return: (bytes|iterator) the file content in bytes format

        """
    if self.__get_headers_value('Content-Type') is None:
        file_type = HTTPDHandlerUtils.get_mime_type(filepath)
    else:
        file_type = self.__get_headers_value('Content-Type')
    if file_type is not None and (file_type.startswith('text/') or file_type == 'application/javascript' or file_type == 'application/json'):
        with codecs.open(filepath, 'r', 'utf-8') as fp:
            content = bytes('', 'utf-8')
            for line in fp.readlines():
                content += bytes(line, 'utf-8')
            return content
    sz = os.path.getsize(filepath)
    if sz < 100 * 1024 * 1024:
        return open(filepath, 'rb').read()

    def file_iterator():
        with open(filepath, 'rb') as fp:
            chunk = fp.read(8192)
            while chunk:
                yield chunk
                chunk = fp.read(8192)
    return file_iterator()
```

*Open and read the given file and transform the content to bytes value.*

##### Parameters

- **filepath**: (*str*) The path of the file to read


##### Returns

- (*bytes*|iterator) the file content in bytes format

#### __extract_body_content

```python
def __extract_body_content(self, content) -> dict:
    """Read and parse the body content of a POST request.

        :param content: (Binary object) the body of the POST request
        :return: (dict) the dictionary that contains the events to process,
                        or an empty dictionary if there is an error.

        """
    content_type = self.__get_headers_value('Content-Type')
    content_length = self.__get_headers_value('Content-Length', '0')
    try:
        content_length = int(content_length)
    except (TypeError, ValueError):
        content_length = 0
    data = content.read(content_length)
    try:
        data = data.decode('utf-8')
    except UnicodeError:
        logging.debug('Not an utf-8 content.')
        pass
    if content_type is None or content_length == 0:
        data = dict()
    elif 'application/json' in content_type:
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            logging.error(f"Can't decode JSON posted data : {data}")
    elif 'multipart/form-data; boundary=' in content_type:
        if isinstance(data, bytes) is True:
            filename, mime_type, content = HTTPDHandlerUtils.__extract_binary_form_data_file(content_type, data)
        else:
            filename, mime_type, content = HTTPDHandlerUtils.__extract_form_data_file(content_type, data)
        data = {'upload_file': {'filename': filename, 'mime_type': mime_type, 'file_content': content}}
    else:
        data = dict(parse_qsl(data, keep_blank_values=True, strict_parsing=False))
    if 'upload_file' in data:
        logging.debug(f' -- upload_file[{data['upload_file']['filename']}]')
    return data
```

*Read and parse the body content of a POST request.*

##### Parameters

- **content**: (Binary *object*) the body of the POST request


##### Returns

- (*dict*) the dictionary that contains the events to process, or an empty dictionary if there is an error.

#### __extract_form_data_file

```python
@staticmethod
def __extract_form_data_file(content_type: str, data: str) -> tuple[str, str, str]:
    """Extract the body of a "formdata request" to upload a file.

        Use this function with an utf-8 file content.

        :param content_type: (str) The content type in the header of the request
        :param data: (str | bytes) the body of the request in bytes or string format
        :return: (tuple[str, str, str]) the data extracted : filename, fime mime type and file content

        """
    filename, end_index_filename = HTTPDHandlerUtils.__extract_form_data_filename(data)
    data = data[end_index_filename:]
    mimetype, end_index_type = HTTPDHandlerUtils.__extract_form_data_mimetype(data)
    data = data[end_index_type + 1:]
    boundary = HTTPDHandlerUtils.__extract_form_data_boundary(content_type)
    start_content = data.index('\n') + 1
    end_content = data[start_content:].index(boundary)
    content = data[start_content:end_content]
    content = content.replace('\r', '')
    return (filename, mimetype, content)
```

*Extract the body of a "formdata request" to upload a file.*

Use this function with an utf-8 file content.

##### Parameters

- **content_type**: (*str*) The content type in the header of the request
- **data**: (*str* | *bytes*) the body of the request in bytes or string format


##### Returns

- **(tuple[str, str, str]) the data extracted**: filename, fime mime type and file content

#### __extract_binary_form_data_file

```python
@staticmethod
def __extract_binary_form_data_file(content_type: str, data: bytes) -> tuple:
    """Extract the body of a "formdata request" to upload a file.

        Use this function with a binary file content.

        :param content_type: (str) The content type in the header of the request
        :param data: (str | bytes) the body of the request in bytes or string format
        :return: (tuple[str, str, str]) the data extracted : filename, fime mime type and file content

        """
    file_content_begin = None
    content_type_pass = False
    prefix = ''
    for i in range(len(data)):
        if data[i] <= 127:
            prefix += chr(data[i])
        else:
            file_content_begin = i
            break
        if content_type_pass is True:
            index = prefix.index('Content-Type')
            if '\n\n' in prefix[index:] or '\r\n\r\n' in prefix[index:]:
                file_content_begin = i + 1
                break
        if content_type_pass is False and 'Content-Type' in prefix:
            content_type_pass = True
    reversed_boundary = HTTPDHandlerUtils.__extract_form_data_boundary(content_type)[::-1]
    file_content_end = None
    postfix = ''
    for i in range(len(data) - 1, file_content_begin, -1):
        if reversed_boundary not in postfix:
            postfix += chr(data[i])
        else:
            file_content_end = i
            break
    content = data[file_content_begin:file_content_end + 1]
    filename = HTTPDHandlerUtils.__extract_form_data_filename(prefix)[0]
    mimetype = HTTPDHandlerUtils.__extract_form_data_mimetype(prefix)[0]
    return (filename, mimetype, content)
```

*Extract the body of a "formdata request" to upload a file.*

Use this function with a binary file content.

##### Parameters

- **content_type**: (*str*) The content type in the header of the request
- **data**: (*str* | *bytes*) the body of the request in bytes or string format


##### Returns

- **(tuple[str, str, str]) the data extracted**: filename, fime mime type and file content

#### __extract_form_data_filename

```python
@staticmethod
def __extract_form_data_filename(text: str) -> tuple[str, int]:
    """Extract the filename from the form data uploaded file.

        :param text: (str) the body or a part received from the request.
        :return: (tuple[str, str, str]) the filename and the index where the filename value ends.

        """
    start_index_filename = text.index('filename="') + len('filename="')
    end_index_filename = start_index_filename + text[start_index_filename:].index('"')
    return (text[start_index_filename:end_index_filename], end_index_filename)
```

*Extract the filename from the form data uploaded file.*

##### Parameters

- **text**: (*str*) the body or a part received from the request.


##### Returns

- (*tuple*[*str*, *str*, *str*]) the filename and the index where the filename value ends.

#### __extract_form_data_mimetype

```python
@staticmethod
def __extract_form_data_mimetype(text: str) -> tuple[str, int]:
    """Extract the mimetype from the form data uploaded file.

        :param text: (str) the body or a part received from the request.
        :return: (tuple[str, str, str]) the mimetype and the index where the mimetype value ends.

        """
    start_index_type = text.index('Content-Type: ') + len('Content-Type: ')
    end_index_type = start_index_type + text[start_index_type:].index('\n')
    mimetype = text[start_index_type:end_index_type]
    mimetype = mimetype.replace('\r', '')
    return (mimetype, end_index_type)
```

*Extract the mimetype from the form data uploaded file.*

##### Parameters

- **text**: (*str*) the body or a part received from the request.


##### Returns

- (*tuple*[*str*, *str*, *str*]) the mimetype and the index where the mimetype value ends.

#### __extract_form_data_boundary

```python
@staticmethod
def __extract_form_data_boundary(content_type: str) -> str:
    """Extract the boundary from the form data content type which delimited the uploaded file content.

        :param content_type: (str) the content type in the header of the received request.
        :return: (tuple[str, str, str]) the boundary.

        """
    start_boundary = content_type.index('boundary=') + len('boundary=')
    boundary = '--' + content_type[start_boundary:] + '--'
    return boundary
```

*Extract the boundary from the form data content type which delimited the uploaded file content.*

##### Parameters

- **content_type**: (*str*) the content type in the header of the received request.


##### Returns

- (*tuple*[*str*, *str*, *str*]) the boundary.



## Class `BaseHTTPDServer`

### Description

*A base class for any custom HTTPD server.*

It adds a dictionary of the HTML page's bakery this server can handle
and the name of the default page.

##### Example

    >>> s = BaseHTTPDServer(server_address, app_handler)
    >>> s.create_pages()


### Constructor

#### __init__

```python
def __init__(self, *args, **kwargs):
    """Create the server instance and add custom members.

    """
    super(BaseHTTPDServer, self).__init__(*args, **kwargs)
    self._pages = dict()
    self._default = 'index.html'
```

*Create the server instance and add custom members.*





### Public functions

#### default

```python
def default(self):
    return self._default
```



#### create_pages

```python
def create_pages(self, app: str='app'):
    """To be overridden. Add bakeries for dynamic HTML pages.

        The created pages are instances of the BaseResponseRecipe class.
        Below is an example on how to override this method:

        :example:
        if app == "main":
            self._pages["index.html"] = BaseResponseRecipe("index.html", HTMLTree("Index"))
            self._pages["foo.html"] = WebResponseRecipe("foo.html", HTMLTree("Foo"))
        elif app == "test":
            self._pages["test.html"] = BaseResponseRecipe("test.html", HTMLTree("test"))

        :param app: (str) Any string definition for custom use

        """
    raise NotImplementedError
```

*To be overridden. Add bakeries for dynamic HTML pages.*

The created pages are instances of the BaseResponseRecipe class.
Below is an example on how to override this method:

##### Example

    > if app == "main":
    > self._pages["index.html"] = BaseResponseRecipe("index.html", HTMLTree("Index"))
    > self._pages["foo.html"] = WebResponseRecipe("foo.html", HTMLTree("Foo"))
    > elif app == "test":
    > self._pages["test.html"] = BaseResponseRecipe("test.html", HTMLTree("test"))

##### Parameters

- **app**: (*str*) Any string definition for custom use

#### page_bakery

```python
def page_bakery(self, page_name: str, headers: dict, events: dict, has_to_return_data: bool=False) -> tuple:
    """Return the page content and response status.

        This method should be invoked after a POST request in order to
        take the events into account when baking the HTML page content.

        :param page_name: (str) Requested page name
        :param headers: (dict) The headers ot the http request
        :param events: (dict) key=event name, value=event value
        :param has_to_return_data: (bool) False by default - Boolean to know if the server return data or html page

        :return: tuple(bytes, HTTPDStatus)

        """
    return HTTPDHandlerUtils.bakery(self._pages, page_name, headers, events, has_to_return_data)
```

*Return the page content and response status.*

This method should be invoked after a POST request in order to
take the events into account when baking the HTML page content.

##### Parameters

- **page_name**: (*str*) Requested page name
- **headers**: (*dict*) The headers ot the http request
- **events**: (*dict*) key=event name, value=event value
- **has_to_return_data**: (*bool*) False by default - Boolean to know if the server return data or html page

##### Returns

- tuple(*bytes*, HTTPDStatus)





~ Created using [Clamming](https://clamming.sf.net) version 1.9 ~
