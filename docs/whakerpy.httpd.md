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
def __init__(self, name='Undefined', tree=None, **kwargs):
    """Create a new ResponseRecipe instance with a default response.

    :param name: (str) Filename of the body main content or name of the page.
    :param tree: (HTMLTree|None)

    Optional arguments:
        - title: (str) The title of the page
        - description: (str) The description of the page (160 characters max)

    """
    self._name = name
    if name is not None:
        self._page_name = os.path.basename(name)
    else:
        self._name = 'undefined'
        self._page_name = ''
    self._status = HTTPDStatus()
    self._data = dict()
    self._title = ''
    self._description = ''
    if 'title' in kwargs:
        self._title = kwargs['title']
    if 'description' in kwargs:
        self._description = kwargs['description']
    if tree is not None and isinstance(tree, HTMLTree):
        self._htree = tree
    else:
        self._htree = HTMLTree(self._name.replace(' ', '_'))
    self.create()
```

*Create a new ResponseRecipe instance with a default response.*

##### Parameters

- **name**: (*str*) Filename of the body main content or name of the page.
- **tree**: (HTMLTree|None)

Optional arguments:
- title: (str) The title of the page
- description: (str) The description of the page (160 characters max)



### Public functions

#### page

```python
@classmethod
def page(cls):
    """Return the current HTML body->main filename or an empty string."""
    return cls._name
```

*Return the current HTML body->main filename or an empty string.*

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

#### get_pagename

```python
def get_pagename(self) -> str:
    """Return the name of the HTML page as seen in the URL."""
    return self._page_name
```

*Return the name of the HTML page as seen in the URL.*

#### set_pagename

```python
def set_pagename(self, page_name: str):
    """Set the name of this page as seen in the url.

        :param page_name: (str) Name of the HTML page.

        """
    if type(page_name) is not str:
        raise TypeError('Page name must be a string.')
    self._page_name = page_name
```

*Set the name of this page as seen in the url.*

##### Parameters

- **page_name**: (*str*) Name of the HTML page.

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
- 404: Not Found -- also used for "expired"
- 410: Gone
- 418: I'm a teapot


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

        This method:
        - extracts the query string (before path normalization),
        - applies blacklist (if enabled),
        - applies signed URL verification (if enabled),
        - serves static files or generated HTML pages.

        """
    logging.debug(' ---- DO GET -- requested: {}'.format(self.path))
    raw_path = self.path
    query_string = ''
    if '?' in raw_path:
        query_string = raw_path.split('?', 1)[1]
    handler_utils = HTTPDHandlerUtils(self.headers, raw_path, self.get_default_page())
    self.path = handler_utils.get_path()
    mime_type = HTTPDHandlerUtils.get_mime_type(self.path)
    allowed = True
    if hasattr(self.server, 'policy_check') is True:
        allowed, content, status, mime = self.server.policy_check(self.path, query_string, self.headers)
    if allowed is True:
        if os.path.exists(handler_utils.get_path()) or os.path.exists(handler_utils.get_path()[1:]):
            content, status = handler_utils.static_content(self.path[1:])
        elif mime_type == 'text/html':
            content, status = self._bakery(handler_utils, dict(), mime_type)
        else:
            content, status = handler_utils.static_content(self.path[1:])
    else:
        mime_type = mime
    self._response(content, status.code, mime_type)
```

*Prepare the response to a GET request.*

This method:
- extracts the query string (before path normalization),
- applies blacklist (if enabled),
- applies signed URL verification (if enabled),
- serves static files or generated HTML pages.

#### do_POST

```python
def do_POST(self) -> None:
    """Prepare the response to a POST request.

        This method:
        - extracts the query string (before path normalization),
        - applies blacklist (if enabled),
        - applies signed URL verification (if enabled),
        - reads POST body and generates the HTML response.

        """
    logging.debug(' ----- DO POST -- requested: {}'.format(self.path))
    raw_path = self.path
    query_string = ''
    if '?' in raw_path:
        query_string = raw_path.split('?', 1)[1]
    handler_utils = HTTPDHandlerUtils(self.headers, raw_path, self.get_default_page())
    self.path = handler_utils.get_path()
    allowed = True
    if hasattr(self.server, 'policy_check') is True:
        allowed, content, status, mime = self.server.policy_check(self.path, query_string, self.headers)
    if allowed is True:
        events, accept = handler_utils.process_post(self.rfile)
        content, status = self._bakery(handler_utils, events, accept)
    self._response(content, status.code, 'text/html')
```

*Prepare the response to a POST request.*

This method:
- extracts the query string (before path normalization),
- applies blacklist (if enabled),
- applies signed URL verification (if enabled),
- reads POST body and generates the HTML response.

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

#### blacklisted_page_answer

```python
@staticmethod
def blacklisted_page_answer() -> tuple:
    """Create the response with 418 (forbidden) status code.

        :return: (tuple) Response content and status to send back to the client

        """
    status = HTTPDStatus(418)
    content = status.to_html(encode=True, msg_error="I'm a Teapot. If you are not a robot, send an e-mail to the administrator.")
    return (content, status)
```

*Create the response with 418 (forbidden) status code.*

##### Returns

- (*tuple*) Response content and status to send back to the client

#### signed_url_page_answer

```python
@staticmethod
def signed_url_page_answer() -> tuple:
    """Create the response with 404 status code for an expired signed URL.

        :return: (tuple) Response content and status to send back to the client

        """
    status = HTTPDStatus(404)
    content = status.to_html(encode=True, msg_error='This page URL is invalid or has expired.')
    return (content, status)
```

*Create the response with 404 status code for an expired signed URL.*

##### Returns

- (*tuple*) Response content and status to send back to the client

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
    >>> s.configure(app="AppName", blacklist=["SomeBot"])

This server stores:
- dynamic pages ("_pages") used by the bakery system,
- the default page name ("_default"),
- an optional HTTP policy with:
1. a persistent blacklist of URL paths used by HTTPDHandler
to reject abusive requests as early as possible.
2. a set of signed URLs


### Constructor

#### __init__

```python
def __init__(self, *args, **kwargs):
    """Create the server instance and add custom members.

    """
    super(BaseHTTPDServer, self).__init__(*args, **kwargs)
    self._pages = dict()
    self._default = 'index.html'
    self._policy = HTTPDPolicy()
```

*Create the server instance and add custom members.*





### Public functions

#### configure

```python
def configure(self, **kwargs) -> None:
    """Configure the server.

        1. Configure policy....
        2. Add bakeries for dynamic HTML pages : The created pages are instances
        of the BaseResponseRecipe class.

        Optional keys in config dict:
            - "app": application name
            - "blacklist": list of blacklisted URL paths
            - "signed_url": signed URL path

        :param kwargs: (dict) Configuration dictionary.

        """
    self._policy.configure({'blacklist': kwargs.get('blacklist', None), 'signed_url': kwargs.get('signed_url', None)})
    self._create_pages(**kwargs)
```

*Configure the server.*

1. Configure policy....
2. Add bakeries for dynamic HTML pages : The created pages are instances
of the BaseResponseRecipe class.

Optional keys in config dict:
- "app": application name
- "blacklist": list of blacklisted URL paths
- "signed_url": signed URL path

##### Parameters

- **kwargs**: (*dict*) Configuration dictionary.

#### policy_check

```python
def policy_check(self, path: str, query_string: str, headers) -> tuple:
    """Check the request against policies and return decision and response.

        Returned values are:
            - allowed: (bool) True if request is accepted
            - content: (bytes|None) HTML bytes if rejected, otherwise None
            - status: (HTTPDStatus|None) Status if rejected, otherwise None
            - mime_type: (str|None) Mime if rejected, otherwise None

        :param path: (str) Normalized URL path (without query).
        :param query_string: (str) Raw query string (without '?').
        :param headers: (Any) Request headers or environ. Must support ".get(...)".
        :return: (tuple) (allowed, content, status, mime_type)

        """
    return self._policy.check(path, query_string, headers)
```

*Check the request against policies and return decision and response.*

Returned values are:
- allowed: (bool) True if request is accepted
- content: (bytes|None) HTML bytes if rejected, otherwise None
- status: (HTTPDStatus|None) Status if rejected, otherwise None
- mime_type: (str|None) Mime if rejected, otherwise None

##### Parameters

- **path**: (*str*) Normalized URL path (without query).
- **query_string**: (*str*) Raw query string (without '?').
- **headers**: (Any) Request headers or environ. Must support ".get(...)".


##### Returns

- (*tuple*) (allowed, content, status, mime_type)

#### default

```python
def default(self):
    """Return the default page name, used when a URL ends with '/'."""
    return self._default
```

*Return the default page name, used when a URL ends with '/'.*

#### page_bakery

```python
def page_bakery(self, page_name: str, headers: dict, events: dict, has_to_return_data: bool=False) -> tuple:
    """Return the page content and response status.

        This method bakes a page and optionally finalizes outgoing HTML.

        :param page_name: (str) Requested page name.
        :param headers: (dict) HTTP request headers.
        :param events: (dict) Event values (POST).
        :param has_to_return_data: (bool) True if returning data, False if returning HTML.
        :return: (tuple) (content, status)

        """
    content, status = HTTPDHandlerUtils.bakery(self._pages, page_name, headers, events, has_to_return_data)
    if has_to_return_data is False:
        content = self._policy.finalize_html(content)
    return (content, status)
```

*Return the page content and response status.*

This method bakes a page and optionally finalizes outgoing HTML.

##### Parameters

- **page_name**: (*str*) Requested page name.
- **headers**: (*dict*) HTTP request headers.
- **events**: (*dict*) Event values (POST).
- **has_to_return_data**: (*bool*) True if returning data, False if returning HTML.


##### Returns

- (*tuple*) (content, status)



### Private functions

#### _create_pages

```python
def _create_pages(self, **kwargs):
    """To be overridden. Add bakeries for dynamic HTML pages.

        The created pages are instances of the BaseResponseRecipe class.
        Below is an example on how to override this method:

        :example:
        if app == "main":
            self._pages["index.html"] = BaseResponseRecipe("index.html", HTMLTree("Index"))
            self._pages["foo.html"] = WebResponseRecipe("foo.html", HTMLTree("Foo"))
        elif app == "test":
            self._pages["test.html"] = BaseResponseRecipe("test.html", HTMLTree("test"))

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



## Class `Blacklist`

### Description

*Manager of a list of blacklisted websites.*

A blacklist is a set of URL paths that can be blacklisted by a website,
managed as a persistent set of URL paths to be rejected.

The blacklist stores URL paths as strings, for example:
- /bot.html
- /admin/
- /foo/bar

A match can be:
- exact match
- parent-path match

Example:
If '/admin' is in the blacklist, then '/admin', '/admin/', and
'/admin/page.html' are considered blacklisted.


### Constructor

#### __init__

```python
def __init__(self) -> None:
    """Create an empty blacklist."""
    self.__blacklist = set()
```

*Create an empty blacklist.*



### Public functions

#### configure

```python
def configure(self, config: dict, json_key: str='blacklist') -> int:
    """Configure the blacklist.

        :param config: (dict) Configuration dictionary.
        :param json_key: (str) Key of the blacklist list in JSON files.
        :return: (int) Number of blacklisted URLs.

        """
    items = config.get(json_key, [])
    if isinstance(items, list) is False:
        raise TypeError(f"JSON key '{json_key}' must be a list.")
    out: set[str] = set()
    for it in items:
        if isinstance(it, str) is True and len(it) > 0:
            out.add(it)
            logging.info("Blacklisted entry '" + it + "'")
    self.__blacklist = out
    return len(out)
```

*Configure the blacklist.*

##### Parameters

- **config**: (*dict*) Configuration dictionary.
- **json_key**: (*str*) Key of the blacklist list in JSON files.


##### Returns

- (*int*) Number of blacklisted URLs.

#### match

```python
def match(self, value: str) -> bool:
    """Return True if a blacklist entry is found inside the given string.

        This method is intended for headers like User-Agent.
        Each blacklist entry is a plain string token.
        Matching rule: substring search.

        :param value: (str) A string to test (example: a User-Agent header).
        :return: (bool) True if blacklisted, False otherwise.

        """
    if type(value) is not str:
        raise TypeError('Value must be a string.')
    for entry in self.__blacklist:
        if entry in value:
            return True
    return False
```

*Return True if a blacklist entry is found inside the given string.*

This method is intended for headers like User-Agent.
Each blacklist entry is a plain string token.
Matching rule: substring search.

##### Parameters

- **value**: (*str*) A string to test (example: a User-Agent header).


##### Returns

- (*bool*) True if blacklisted, False otherwise.

#### load

```python
def load(self, filepath: str, json_key: str='blacklist') -> int:
    """Load blacklist entries from a file.

        If filepath ends with '.json', entries are loaded from the given json_key.
        Otherwise, entries are loaded from a text file (one entry per line).

        :param filepath: (str) Path of the file.
        :param json_key: (str) Key of the blacklist list in JSON files.
        :raises: TypeError: filepath is not a string.
        :raises: IOError: file does not exist.
        :raises: ValueError: JSON content is invalid, or json_key is not a list.
        :return: (int) Number of loaded entries.

        """
    if type(filepath) is not str:
        raise TypeError('Blacklist filepath must be a string.')
    if os.path.exists(filepath) is False:
        raise IOError(f'Blacklist file {filepath} does not exist.')
    if filepath.lower().endswith('.json'):
        return self.__load_json(filepath, json_key)
    return self.__load_text(filepath)
```

*Load blacklist entries from a file.*

If filepath ends with '.json', entries are loaded from the given json_key.
Otherwise, entries are loaded from a text file (one entry per line).

##### Parameters

- **filepath**: (*str*) Path of the file.
- **json_key**: (*str*) Key of the blacklist list in JSON files.


##### Raises

- *TypeError*: filepath is not a string.
- *IOError*: file does not exist.
- *ValueError*: JSON content is invalid, or json_key is not a list.


##### Returns

- (*int*) Number of loaded entries.



### Protected functions

#### __load_text

```python
def __load_text(self, filepath: str) -> int:
    items: set[str] = set()
    with open(filepath, 'r', encoding='utf-8') as fp:
        for line in fp:
            s = line.strip()
            if len(s) == 0 or s.startswith('#'):
                continue
            items.add(s)
    self.__blacklist = items
    return len(items)
```



#### __load_json

```python
def __load_json(self, filepath: str, json_key: str) -> int:
    with open(filepath, 'r', encoding='utf-8') as fp:
        try:
            _full_data = json.load(fp)
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON file: {filepath}') from e
    if 'WhakerPy' not in _full_data:
        raise KeyError(f"{filepath!r} is missing the required 'WhakerPy' section.")
    _section = _full_data['WhakerPy']
    if isinstance(_section, dict) is False:
        raise TypeError("JSON key 'WhakerPy' must be a dict.")
    return self.configure(_section)
```





### Overloads

#### __contains__

```python
def __contains__(self, item):
    """Return True if the given URL path exists in the blacklist."""
    return item in self.__blacklist
```

*Return True if the given URL path exists in the blacklist.*

#### __str__

```python
def __str__(self):
    return str(self.__blacklist)
```



#### __repr__

```python
def __repr__(self):
    return 'Blacklist: ' + str(self.__blacklist)
```





## Class `SignedURL`

### Description

*Sign and verify ephemeral URLs.*

A signed URL is:
<path>?<ts_key>=<unix_ts>&<sig_key>=<signature>

The signature is HMAC-SHA256 on:
path + "\n" + unix_ts

No cookie. No server-side storage. Python standard library only.

##### Example

    >>> signer = SignedURL(secret='YOUR_PRIVATE_SECRET')
    >>> url = signer.sign('/text_12345.html', ttl_seconds=120)
    >>> ok = signer.verify('/text_12345.html', query_string, ttl_seconds=120)


### Constructor

#### __init__

```python
def __init__(self):
    """Create the SignedURL helper.

    """
    self.__secret = None
    self.__ts_key = ''
    self.__sig_key = ''
```

*Create the SignedURL helper.*





### Public functions

#### configure

```python
def configure(self, config: dict, json_key: str='signed_url') -> dict:
    """Configure the signed URLs.

        :param config: (dict) Configuration dictionary.
        :param json_key: (str) Key of the signed URLs list in dict.
        :raises: TypeError: invalid argument type.
        :raises: ValueError: dict content is invalid, or json_key is not a str.
        :return: (dict) Loaded settings: {"ttl": int, "protect": list}.

        """
    _cfg = config.get(json_key, None)
    if _cfg is None:
        self.__secret = None
        self.__ts_key = ''
        self.__sig_key = ''
        return {'ttl': None, 'protect': []}
    if isinstance(_cfg, dict) is False:
        raise TypeError(f"JSON key '{json_key}' must be a dict.")
    _secret = _cfg.get('secret', '')
    self.check_non_empty_string(_secret)
    _ttl_seconds = _cfg.get('ttl')
    self.check_ttl_seconds(_ttl_seconds)
    _protect = _cfg.get('protect')
    if isinstance(_protect, (list, tuple)) is False:
        raise ValueError('signed_url.protect must be a list.')
    _query_keys = _cfg.get('query_keys', {})
    if isinstance(_query_keys, dict) is False:
        raise ValueError('signed_url.query_keys must be a dict.')
    ts_key = _query_keys.get('ts', self.__ts_key)
    self.check_non_empty_string(ts_key)
    sig_key = _query_keys.get('sig', self.__sig_key)
    self.check_non_empty_string(sig_key)
    self.__secret = _secret.encode('utf-8')
    self.__ts_key = ts_key
    self.__sig_key = sig_key
    return {'ttl': _ttl_seconds, 'protect': _protect}
```

*Configure the signed URLs.*

##### Parameters

- **config**: (*dict*) Configuration dictionary.
- **json_key**: (*str*) Key of the signed URLs list in dict.


##### Raises

- *TypeError*: invalid argument type.
- *ValueError*: dict content is invalid, or json_key is not a str.


##### Returns

- **(dict) Loaded settings**: {"ttl": int, "protect": list}.

#### load

```python
def load(self, filepath: str, json_key: str='signed_url') -> dict:
    """Load signed URL configuration entries from a file.

        Entries are loaded from the given json_key.

        :param filepath: (str) Path of the file.
        :param json_key: (str) Key of the signed URLs dict in JSON files.
        :raises: TypeError: invalid argument type.
        :raises: IOError: file does not exist.
        :raises: ValueError: JSON content is invalid, or json_key is not a str.
        :return: (dict) Loaded settings: {"ttl": int, "protect": list}.

        """
    self.check_non_empty_string(filepath)
    self.check_non_empty_string(json_key)
    if os.path.exists(filepath) is False:
        raise IOError(f'SignedURL configuration file {filepath} does not exist.')
    return self.__load_json(filepath, json_key)
```

*Load signed URL configuration entries from a file.*

Entries are loaded from the given json_key.

##### Parameters

- **filepath**: (*str*) Path of the file.
- **json_key**: (*str*) Key of the signed URLs dict in JSON files.


##### Raises

- *TypeError*: invalid argument type.
- *IOError*: file does not exist.
- *ValueError*: JSON content is invalid, or json_key is not a str.


##### Returns

- **(dict) Loaded settings**: {"ttl": int, "protect": list}.

#### match_protect

```python
def match_protect(self, path: str, protect: list) -> bool:
    """Return True if the given path must be protected by a signed URL.

        Protection rules are defined as a list of dict:
            {"prefix": "...", "suffix": "..."}

        :param path: (str) URL path (with or without leading slash).
        :param protect: (list) Protection rules.
        :return: (bool)

        """
    if type(path) is not str:
        raise TypeError('SignedURL path must be a string.')
    if isinstance(protect, (list, tuple)) is False:
        raise TypeError('SignedURL protect must be a list.')
    normalized_path = self.__normalize_path(path)
    for rule in protect:
        if isinstance(rule, dict) is False:
            continue
        prefix = rule.get('prefix', '')
        suffix = rule.get('suffix', '')
        if type(prefix) is not str or type(suffix) is not str:
            continue
        if normalized_path.startswith(prefix) and normalized_path.endswith(suffix):
            return True
    return False
```

*Return True if the given path must be protected by a signed URL.*

Protection rules are defined as a list of dict:
{"prefix": "...", "suffix": "..."}

##### Parameters

- **path**: (*str*) URL path (with or without leading slash).
- **protect**: (*list*) Protection rules.


##### Returns

- (*bool*)

#### sign

```python
def sign(self, path: str, ttl_seconds: int) -> str:
    """Return a signed URL for the given path.

        :param path: (str) URL path (example: 'text_123.html').
        :param ttl_seconds: (int) Lifetime in seconds. The timestamp is "now".
        :raises: TypeError: invalid argument type.
        :raises: ValueError: invalid argument value.
        :return: (str) Signed URL (path + query).

        """
    if self.__secret is None:
        raise ValueError('SignedURL is not configured (secret is missing).')
    self.check_non_empty_string(path)
    self.check_ttl_seconds(ttl_seconds)
    normalized_path = self.__normalize_path(path)
    now_ts = int(time.time())
    signature = self.__hmac_signature(normalized_path, now_ts)
    return '{:s}?{:s}={:d}&{:s}={:s}'.format(normalized_path, self.__ts_key, now_ts, self.__sig_key, signature)
```

*Return a signed URL for the given path.*

##### Parameters

- **path**: (*str*) URL path (example: 'text_123.html').
- **ttl_seconds**: (*int*) Lifetime in seconds. The timestamp is "now".


##### Raises

- *TypeError*: invalid argument type.
- *ValueError*: invalid argument value.


##### Returns

- (*str*) Signed URL (path + query).

#### verify

```python
def verify(self, path: str, query_string: str, ttl_seconds: int) -> bool:
    """Verify that (path, query_string) contains a valid signature.

        :param path: (str) URL path without query (example: '/text_123.html').
        :param query_string: (str) Raw query string (example: 'ts=...&sig=...').
        :param ttl_seconds: (int) Accepted lifetime in seconds.
        :return: (bool) True if valid, False otherwise.

        """
    if self.__secret is None:
        raise ValueError('SignedURL is not configured (secret is missing).')
    if type(path) is not str:
        raise TypeError('SignedURL path must be a string.')
    if type(query_string) is not str:
        raise TypeError('SignedURL query_string must be a string.')
    self.check_ttl_seconds(ttl_seconds)
    normalized_path = self.__normalize_path(path)
    ts_value, sig_value = self.__extract_ts_sig(query_string)
    if ts_value is None or sig_value is None:
        return False
    now_ts = int(time.time())
    if ts_value > now_ts:
        return False
    if now_ts - ts_value > ttl_seconds:
        return False
    expected_sig = self.__hmac_signature(normalized_path, ts_value)
    return hmac.compare_digest(expected_sig, sig_value)
```

*Verify that (path, query_string) contains a valid signature.*

##### Parameters

- **path**: (*str*) URL path without query (example: '/text_123.html').
- **query_string**: (*str*) Raw query string (example: 'ts=...&sig=...').
- **ttl_seconds**: (*int*) Accepted lifetime in seconds.


##### Returns

- (*bool*) True if valid, False otherwise.

#### check_ttl_seconds

```python
@staticmethod
def check_ttl_seconds(value: int):
    if type(value) is not int:
        raise TypeError('SignedURL ttl_seconds must be an int.')
    if value <= 0:
        raise ValueError('SignedURL ttl_seconds must be > 0.')
```



#### check_non_empty_string

```python
@staticmethod
def check_non_empty_string(value: str):
    if type(value) is not str:
        raise TypeError(f"Given '{value}' must be a string.")
    if len(value) == 0:
        raise ValueError(f"Given '{value}' must be non-empty.")
```





### Protected functions

#### __normalize_path

```python
def __normalize_path(self, path: str) -> str:
    p = path
    if '?' in p:
        p = p.split('?', 1)[0]
    if p.startswith('/') is False:
        p = '/' + p
    while '//' in p:
        p = p.replace('//', '/')
    return p
```



#### __hmac_signature

```python
def __hmac_signature(self, path: str, unix_ts: int) -> str:
    payload = '{:s}\n{:d}'.format(path, unix_ts).encode('utf-8')
    digest = hmac.new(self.__secret, payload, hashlib.sha256).hexdigest()
    return digest
```



#### __extract_ts_sig

```python
def __extract_ts_sig(self, query_string: str) -> tuple[int | None, str | None]:
    if len(query_string) == 0:
        return (None, None)
    qs = parse_qs(query_string, keep_blank_values=True)
    if self.__ts_key not in qs:
        return (None, None)
    if self.__sig_key not in qs:
        return (None, None)
    ts_list = qs.get(self.__ts_key, [])
    sig_list = qs.get(self.__sig_key, [])
    if len(ts_list) != 1 or len(sig_list) != 1:
        return (None, None)
    ts_raw = ts_list[0]
    sig_raw = sig_list[0]
    try:
        ts_value = int(ts_raw)
    except ValueError:
        return (None, None)
    if type(sig_raw) is not str:
        return (None, None)
    if len(sig_raw) == 0:
        return (None, None)
    return (ts_value, sig_raw)
```



#### __load_json

```python
def __load_json(self, filepath: str, json_key: str) -> dict:
    """Load signed URL configuration from a JSON file.

        It reads config values and updates this instance fields.
        Expected JSON structure:
            {
                "WhakerPy": {
                    "signed_url": {
                        "secret": "...",
                        "ttl": 3600,
                        "protect": [...],
                        "query_keys": {"ts": "ts", "sig": "sig"}
                    }
                }
            }

        :param filepath:
        :param json_key:
        :raises: ValueError:
        :raises: KeyError:
        :raises: TypeError:
        :return: (dict)   {"ttl": <int>, "protect": <list>}

        """
    with open(filepath, 'r', encoding='utf-8') as fp:
        try:
            _full_data = json.load(fp)
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON file: {filepath}') from e
    if 'WhakerPy' not in _full_data:
        raise KeyError(f"{filepath!r} is missing the required 'WhakerPy' section.")
    _section = _full_data['WhakerPy']
    if isinstance(_section, dict) is False:
        raise TypeError("JSON key 'WhakerPy' must be a dict.")
    return self.configure(_section)
```

*Load signed URL configuration from a JSON file.*

It reads config values and updates this instance fields.
Expected JSON structure:
{
"WhakerPy": {
"signed_url": {
"secret": "...",
"ttl": 3600,
"protect": [...],
"query_keys": {"ts": "ts", "sig": "sig"}
}
}
}

##### Parameters

- **filepath**
- **json_key**


##### Raises

- *ValueError*
- *KeyError*
- *TypeError*


##### Returns

- **(dict)   {"ttl"**: <int>, "protect": <list>}



## Class `HTTPDPolicy`

### Description

*Apply HTTP security policies consistently in HTTPD and WSGI.*

This class centralizes the decision to accept or reject a request,
based on:
- blacklist (User-Agent and/or path)
- signed URL verification (missing/invalid/expired)

It must be instantiated once and configured once.


### Constructor

#### __init__

```python
def __init__(self):
    """Create the policy with default (disabled) configuration.

    """
    self.__blacklist = Blacklist()
    self.__signed_url = SignedURL()
    self.__blacklist_enabled = False
    self.__signed_url_cfg = {'ttl': None, 'protect': []}
```

*Create the policy with default (disabled) configuration.*





### Public functions

#### configure

```python
def configure(self, config: dict) -> None:
    """Configure the policy from a configuration dict.

        Expected keys:
        - "blacklist": optional (filepath or json dict, depending on Blacklist.load)
        - "signed_url": optional (filepath or json dict, depending on SignedURL.load)

        If a key is missing, the corresponding policy is disabled.

        :param config: (dict) The configuration data.

        """
    if type(config) is not dict:
        raise TypeError('HTTPDPolicy.configure: config must be a dict.')
    self.__blacklist_enabled = False
    if 'blacklist' in config and config['blacklist'] is not None:
        self.__blacklist.configure(config, 'blacklist')
        self.__blacklist_enabled = True
    self.__signed_url_cfg = {'ttl': None, 'protect': []}
    if 'signed_url' in config and config['signed_url'] is not None:
        self.__signed_url_cfg = self.__signed_url.configure(config, 'signed_url')
```

*Configure the policy from a configuration dict.*

Expected keys:
- "blacklist": optional (filepath or json dict, depending on Blacklist.load)
- "signed_url": optional (filepath or json dict, depending on SignedURL.load)

If a key is missing, the corresponding policy is disabled.

##### Parameters

- **config**: (*dict*) The configuration data.

#### check

```python
def check(self, path: str, query_string: str, headers) -> tuple:
    """Check the request against policies and return decision and response.

        Returned values are:
            - allowed: (bool) True if request is accepted
            - content: (bytes|None) HTML bytes if rejected, otherwise None
            - status: (HTTPDStatus|None) Status if rejected, otherwise None
            - mime_type: (str|None) Mime if rejected, otherwise None

        :param path: (str) Normalized URL path (without query).
        :param query_string: (str) Raw query string (without '?').
        :param headers: (Any) Request headers or environ. Must support ".get(...)".
        :return: (tuple) (allowed, content, status, mime_type)

        """
    if type(path) is not str:
        raise TypeError('HTTPDPolicy.check: path must be a string.')
    if type(query_string) is not str:
        raise TypeError('HTTPDPolicy.check: query_string must be a string.')
    user_agent = self._get_user_agent(headers)
    if self.__blacklist_enabled is True:
        if self.__blacklist.match(path) is True or self.__blacklist.match(user_agent) is True:
            content, status = HTTPDHandlerUtils.blacklisted_page_answer()
            return (False, content, status, 'text/html')
    ttl_seconds = self.__signed_url_cfg.get('ttl', None)
    if ttl_seconds is not None:
        protect = self.__signed_url_cfg.get('protect', [])
        if self.__signed_url.match_protect(path, protect) is True:
            if self.__signed_url.verify(path, query_string, ttl_seconds) is False:
                content, status = HTTPDHandlerUtils.signed_url_page_answer()
                return (False, content, status, 'text/html')
    return (True, None, None, None)
```

*Check the request against policies and return decision and response.*

Returned values are:
- allowed: (bool) True if request is accepted
- content: (bytes|None) HTML bytes if rejected, otherwise None
- status: (HTTPDStatus|None) Status if rejected, otherwise None
- mime_type: (str|None) Mime if rejected, otherwise None

##### Parameters

- **path**: (*str*) Normalized URL path (without query).
- **query_string**: (*str*) Raw query string (without '?').
- **headers**: (Any) Request headers or environ. Must support ".get(...)".


##### Returns

- (*tuple*) (allowed, content, status, mime_type)

#### finalize_html

```python
def finalize_html(self, content: bytes) -> bytes:
    """Finalize an outgoing HTML page.

        This method applies outbound policies that must not be implemented
        inside Response classes.

        Current behavior:
        - If signed URLs are enabled, sign protected links found in:
          - href="..."
          - action="..."

        :param content: (bytes) HTML content.
        :return: (bytes) Updated HTML content.

        """
    if isinstance(content, (bytes, bytearray)) is False:
        raise TypeError('HTTPDPolicy.finalize_html: content must be bytes.')
    ttl_seconds = self.__signed_url_cfg.get('ttl', None)
    if ttl_seconds is None:
        return content
    protect = self.__signed_url_cfg.get('protect', [])
    if isinstance(protect, list) is False or len(protect) == 0:
        return content
    html = content.decode('utf-8', errors='replace')

    def _should_skip(value: str) -> bool:
        if len(value) == 0:
            return True
        v = value.lower()
        if v.startswith('#'):
            return True
        if v.startswith('http://') or v.startswith('https://'):
            return True
        if v.startswith('mailto:'):
            return True
        if v.startswith('javascript:'):
            return True
        if v.startswith('data:'):
            return True
        return False

    def _is_already_signed(query: str) -> bool:
        if len(query) == 0:
            return False
        q = ('&' + query).lower()
        return '&ts=' in q and '&sig=' in q

    def _sign_value(value: str) -> str:
        if _should_skip(value) is True:
            return value
        parts = urlsplit(value)
        path = parts.path
        if self.__signed_url.match_protect(path, protect) is False:
            return value
        if _is_already_signed(parts.query) is True:
            return value
        extra_params = []
        if len(parts.query) > 0:
            for k, v in parse_qsl(parts.query, keep_blank_values=True):
                if k in ('ts', 'sig'):
                    continue
                extra_params.append((k, v))
        signed = self.__signed_url.sign(path, ttl_seconds)
        signed_parts = urlsplit(signed)
        final_query = signed_parts.query
        if len(extra_params) > 0:
            extra = urlencode(extra_params, doseq=True)
            if len(final_query) > 0:
                final_query = final_query + '&' + extra
            else:
                final_query = extra
        return urlunsplit((signed_parts.scheme or parts.scheme, signed_parts.netloc or parts.netloc, signed_parts.path, final_query, parts.fragment))

    def _repl(m):
        attr = m.group(1)
        quote = m.group(2)
        val = m.group(3)
        return attr + '=' + quote + _sign_value(val) + quote
    html = re.sub('(href|action)\\s*=\\s*([\\\'"])(.*?)\\2', _repl, html, flags=re.IGNORECASE)
    return html.encode('utf-8')
```

*Finalize an outgoing HTML page.*

This method applies outbound policies that must not be implemented
inside Response classes.

Current behavior:
- If signed URLs are enabled, sign protected links found in:
- href="..."
- action="..."

##### Parameters

- **content**: (*bytes*) HTML content.


##### Returns

- (*bytes*) Updated HTML content.



### Private functions

#### _get_user_agent

```python
def _get_user_agent(self, headers) -> str:
    """Extract User-Agent from headers/environ.

        :param headers: (Any) Object or dict supporting get().
        :return: (str) User-Agent or empty string.

        """
    if headers is None:
        return ''
    try:
        ua = headers.get('User-Agent', '')
        if type(ua) is str and len(ua) > 0:
            return ua
    except:
        pass
    try:
        ua = headers.get('HTTP_USER_AGENT', '')
        if type(ua) is str and len(ua) > 0:
            return ua
    except:
        pass
    return ''
```

*Extract User-Agent from headers/environ.*

##### Parameters

- **headers**: (Any) Object or dict supporting get().


##### Returns

- (*str*) User-Agent or empty string.

#### _should_skip

```python
def _should_skip(value: str) -> bool:
    if len(value) == 0:
        return True
    v = value.lower()
    if v.startswith('#'):
        return True
    if v.startswith('http://') or v.startswith('https://'):
        return True
    if v.startswith('mailto:'):
        return True
    if v.startswith('javascript:'):
        return True
    if v.startswith('data:'):
        return True
    return False
```



#### _is_already_signed

```python
def _is_already_signed(query: str) -> bool:
    if len(query) == 0:
        return False
    q = ('&' + query).lower()
    return '&ts=' in q and '&sig=' in q
```



#### _sign_value

```python
def _sign_value(value: str) -> str:
    if _should_skip(value) is True:
        return value
    parts = urlsplit(value)
    path = parts.path
    if self.__signed_url.match_protect(path, protect) is False:
        return value
    if _is_already_signed(parts.query) is True:
        return value
    extra_params = []
    if len(parts.query) > 0:
        for k, v in parse_qsl(parts.query, keep_blank_values=True):
            if k in ('ts', 'sig'):
                continue
            extra_params.append((k, v))
    signed = self.__signed_url.sign(path, ttl_seconds)
    signed_parts = urlsplit(signed)
    final_query = signed_parts.query
    if len(extra_params) > 0:
        extra = urlencode(extra_params, doseq=True)
        if len(final_query) > 0:
            final_query = final_query + '&' + extra
        else:
            final_query = extra
    return urlunsplit((signed_parts.scheme or parts.scheme, signed_parts.netloc or parts.netloc, signed_parts.path, final_query, parts.fragment))
```



#### _repl

```python
def _repl(m):
    attr = m.group(1)
    quote = m.group(2)
    val = m.group(3)
    return attr + '=' + quote + _sign_value(val) + quote
```







~ Created using [Clamming](https://clamming.sf.net) version 2.1 ~
