# WhakerPy 0.4

## Package `whakerpy.httpd`

### Class `BaseResponseRecipe`

#### Description

*Base class to create an HTML response content.*




#### Constructor

##### __init__

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
    shead = self._htree.head.serialize()
    if 'notify_event' not in shead:
        js = HTMLNode(self._htree.head.identifier, None, 'script', value=JS_NOTIFY_EVENT)
        self._htree.head.append_child(js)
    if 'request.js' not in shead:
        self._htree.head.script(src=os.path.join('whakerpy', 'request.js'), script_type='text/javascript')
    self.create()
```

*Create a new ResponseRecipe instance with a default response.*





#### Public functions

##### page

```python
@staticmethod
def page() -> str:
    """Return the HTML page name. To be overridden."""
    return 'undefined.html'
```

*Return the HTML page name. To be overridden.*

##### get_json_data

```python
def get_json_data(self) -> str:
    """Gets the current data to send to the client following this request.

        :return: (str) The json data in the string format

        """
    return json.dumps(self._data)
```

*Gets the current data to send to the client following this request.*

###### Returns

- (*str*) The json data in the string format

##### name

```python
@property
def name(self) -> str:
    return self._name
```



##### status

```python
@property
def status(self) -> HTTPDStatus:
    return self._status
```



##### comment

```python
def comment(self, content: str) -> HTMLComment:
    """Add a comment to the body->main.

        :param content: (str) The comment content
        :return: (HTMLComment) the created node

        """
    return self._htree.comment(content)
```

*Add a comment to the body->main.*

###### Parameters

- **content**: (*str*) The comment content


###### Returns

- (HTMLComment) the created node

##### element

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

###### Parameters

- **tag**: (*str*) HTML element name
- **ident**: (*str*) Identifier of the element
- **class_name**: (*str*) Value of the class attribute


###### Returns

- (HTMLNode) The created node

##### create

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

##### bake

```python
def bake(self, events) -> str:
    """Return the HTML response after processing the events.

        Processing the events may change the response status. This method is
        invoked by the HTTPD server to construct the response. Given events
        are the information the handler received (commonly with POST).

        :param events: (dict) The requested events to be processed

        """
    dirty = self._process_events(events)
    if dirty is True:
        self._invalidate()
        self._bake()
    return self._htree.serialize()
```

*Return the HTML response after processing the events.*

Processing the events may change the response status. This method is
invoked by the HTTPD server to construct the response. Given events
are the information the handler received (commonly with POST).

###### Parameters

- **events**: (*dict*) The requested events to be processed



#### Private functions

##### _process_events

```python
def _process_events(self, events) -> bool:
    """Process the given events.

        The given event name must match a function of the event's manager.
        Processing an event may change the content of the tree. In that case,
        the `dirty` method must be turned into True: it will invalidate the
        deprecated content (_invalidate) and re-generate a new one (_bake).

        :param events (dict): key=event_name, value=event_value
        :return: None

        """
    self._status.code = 200
    return False
```

*Process the given events.*

The given event name must match a function of the event's manager.
Processing an event may change the content of the tree. In that case,
the `dirty` method must be turned into True: it will invalidate the
deprecated content (_invalidate) and re-generate a new one (_bake).

###### Parameters

- **events (dict)**: key=event_name, value=event_value


###### Returns

- None

##### _invalidate

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

##### _bake

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



### Class `HTTPDStatus`

#### Description

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


#### Constructor

##### __init__

```python
def __init__(self):
    """Create the private member for the status code.

    Default status code is 200 for an "OK" httpd response.

    """
    self.__scode = 200
```

*Create the private member for the status code.*

Default status code is 200 for an "OK" httpd response.



#### Public functions

##### check

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

###### Parameters

- **value**: (*int*) A response status.


###### Raises

sppasHTTPDValueError


###### Returns

- (*int*) value

##### get

```python
def get(self):
    """Return the status code value (int)."""
    return self.__scode
```

*Return the status code value (int).*

##### set

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

###### Parameters

- **value**: (*int*) HTTPD status code value.


###### Raises

sppasHTTPDValueError



#### Overloads

##### __str__

```python
def __str__(self):
    return str(self.__scode)
```



##### __repr__

```python
def __repr__(self):
    return '{:d}: {:s}'.format(self.__scode, HTTPDStatus.HTTPD_STATUS[self.__scode])
```



##### __eq__

```python
def __eq__(self, other):
    return self.__scode == other
```





### Class `HTTPDValueError`

#### Description

*:ERROR 0377:.*

Invalid HTTPD status code value '{!s:s}'.


#### Constructor

##### __init__

```python
def __init__(self, value):
    self._status = 377
    self.parameter = error(self._status) + error(self._status).format(value)
```





#### Public functions

##### get_status

```python
def get_status(self):
    return self._status
```





#### Overloads

##### __str__

```python
def __str__(self):
    return repr(self.parameter)
```





### Class `HTTPDHandler`

#### Description

*Web-based application HTTPD handler.*

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


#### Constructor

##### __init__

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





#### Public functions

##### do_HEAD

```python
def do_HEAD(self) -> None:
    """Prepare the response to a HEAD request."""
    logging.debug('HEAD -- requested: {}'.format(self.path))
    self._set_headers(200)
```

*Prepare the response to a HEAD request.*

##### do_GET

```python
def do_GET(self) -> None:
    """Prepare the response to a GET request.

        """
    logging.debug('GET -- requested: {}'.format(self.path))
    if self.path == '/':
        try:
            self.path += self.server.default()
        except AttributeError:
            self.path += 'index.html'
    if '?' in self.path:
        self.path = self.path[:self.path.index('?')]
    if self.path.endswith('html') is True:
        content, status = self._html(dict())
    else:
        content, status = self._static_content(self.path[1:])
    self._response(content, status.code)
```

*Prepare the response to a GET request.*



##### do_POST

```python
def do_POST(self) -> None:
    """Prepare the response to a POST request.

        """
    logging.debug('POST -- requested: {}'.format(self.path))
    if self.path == '/':
        try:
            self.path += self.server.default()
        except AttributeError:
            self.path += 'index.html'
    events = dict()
    content_len = int(self.headers.get('Content-Length'))
    data = self.rfile.read(content_len).decode('utf-8')
    if 'application/json' in self.headers.get('Content-Type'):
        try:
            events = json.loads(data)
        except json.JSONDecodeError:
            logging.error("Can't decode JSON POSTED data : {}".format(data))
    else:
        logging.debug('POST -- data: {}'.format(data))
        for dinput in data.split('&'):
            new_event = dinput.split('=')
            if len(new_event) == 2:
                events[new_event[0]] = new_event[1]
            else:
                logging.error("Can't understand POSTED data: {}".format(dinput))
    if 'application/json' in self.headers.get('Accept'):
        content, status = self._json_data(events)
    else:
        content, status = self._html(events)
    self._response(content, status.code)
```

*Prepare the response to a POST request.*



##### log_request

```python
def log_request(self, code='-', size='-') -> None:
    """Override. For a quiet handler pls!!!."""
    pass
```

*Override. For a quiet handler pls!!!.*



#### Private functions

##### _set_headers

```python
def _set_headers(self, status: int) -> None:
    """Set the HTTPD response headers.

        :param status: (int) A response status.
        :raises: sppasHTTPDValueError

        """
    status = HTTPDStatus.check(status)
    self.send_response(status)
    self.end_headers()
```

*Set the HTTPD response headers.*

###### Parameters

- **status**: (*int*) A response status.


###### Raises

sppasHTTPDValueError

##### _static_content

```python
def _static_content(self, filename: str) -> tuple:
    """Return the file content and the corresponding status.

        :param filename: (str)
        :return: tuple(bytes, HTTPDStatus)

        """
    if os.path.exists(filename) is True:
        if os.path.isfile(filename) is True:
            content = open(filename, 'rb').read()
            return (content, HTTPDStatus())
        else:
            content = bytes("<html><body>Error 403: Forbidden.The client can't have access to the requested {:s}.</body></html>".format(filename), 'utf-8')
            status = HTTPDStatus()
            status.code = 403
            return (content, status)
    content = bytes('<html><body>Error 404: Not found.The server does not have the requested {:s}.</body></html>'.format(filename), 'utf-8')
    status = HTTPDStatus()
    status.code = 404
    return (content, status)
```

*Return the file content and the corresponding status.*

###### Parameters

- **filename**: (*str*)


###### Returns

- tuple(*bytes*, HTTPDStatus)

##### _json_data

```python
def _json_data(self, events: dict) -> tuple:
    """Process the events and return the data and the status.

        :param events: (dict) The dictionary that contains all events posted
        by the client request.

        :return: (tuple) First element - The content of the response (json data).
                         Second element - The status of the server.

        """
    if hasattr(self.server, 'page_bakery') is False:
        return self._static_content(self.path[1:])
    page_name = os.path.basename(self.path)
    content, status = self.server.page_bakery(page_name, events, True)
    if status == 404:
        content, status = self._static_content(self.path[1:])
    return (content, status)
```

*Process the events and return the data and the status.*

###### Parameters

- **events**: (*dict*) The dictionary that contains all events posted by the client request.

###### Returns

- (*tuple*) First element - The content of the response (json data). Second element - The status of the server.

##### _html

```python
def _html(self, events: dict) -> tuple:
    """Process the events and return the html page content and status.

        :param events: (dict) key=event name, value=event value
        :return: tuple(bytes, HTTPDStatus)

        """
    if hasattr(self.server, 'page_bakery') is False:
        return self._static_content(self.path[1:])
    page_name = os.path.basename(self.path)
    content, status = self.server.page_bakery(page_name, events)
    if status == 404:
        content, status = self._static_content(self.path[1:])
    return (content, status)
```

*Process the events and return the html page content and status.*

###### Parameters

- **events**: (*dict*) key=event name, value=event value


###### Returns

- tuple(*bytes*, HTTPDStatus)

##### _response

```python
def _response(self, content: bytes, status: int) -> None:
    """Make the appropriate HTTPD response.

        :param content: (bytes) The HTML response content
        :param status: (int) The HTTPD status code of the response

        """
    if status == 418:
        self._set_headers(418)
    elif status == 205:
        self._set_headers(205)
    else:
        self._set_headers(status)
        self.wfile.write(content)
        if status == 410:
            self.server.shutdown()
```

*Make the appropriate HTTPD response.*

###### Parameters

- **content**: (*bytes*) The HTML response content
- **status**: (*int*) The HTTPD status code of the response



### Class `BaseHTTPDServer`

#### Description

*A base class for any custom HTTPD server.*

It adds a dictionary of the HTML page's bakery this server can handle
and the name of the default page.

###### Example

    >>> s = BaseHTTPDServer(server_address, app_handler)
    >>> s.create_pages()


#### Constructor

##### __init__

```python
def __init__(self, *args, **kwargs):
    """Create the server instance and add custom members.

    """
    super(BaseHTTPDServer, self).__init__(*args, **kwargs)
    self._pages = dict()
    self._default = 'index.html'
```

*Create the server instance and add custom members.*





#### Public functions

##### default

```python
def default(self):
    return self._default
```



##### create_pages

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

###### Example

    > if app == "main":
    > self._pages["index.html"] = BaseResponseRecipe("index.html", HTMLTree("Index"))
    > self._pages["foo.html"] = WebResponseRecipe("foo.html", HTMLTree("Foo"))
    > elif app == "test":
    > self._pages["test.html"] = BaseResponseRecipe("test.html", HTMLTree("test"))

###### Parameters

- **app**: (*str*) Any string definition for custom use

##### page_bakery

```python
def page_bakery(self, page_name: str, events: dict, is_json_data_to_return: bool=False) -> tuple:
    """Return the page content and response status.

        This method should be invoked after a POST request in order to
        take the events into account when baking the HTML page content.

        :param page_name: (str) Requested page name
        :param events: (dict) key=event name, value=event value
        :param is_json_data_to_return: (bool) False by default - Boolean
        value to know if the server return json data or html page

        :return: tuple(bytes, HTTPDStatus)

        """
    if page_name in self._pages:
        if isinstance(self._pages[page_name], BaseResponseRecipe) is True:
            bakery = self._pages[page_name]
            content = bytes(bakery.bake(events), 'utf-8')
            if is_json_data_to_return:
                content = bytes(bakery.get_json_data(), 'utf-8')
            return (content, bakery.status)
    status = HTTPDStatus()
    status.code = 404
    return (bytes(' ', 'utf-8'), status)
```

*Return the page content and response status.*

This method should be invoked after a POST request in order to
take the events into account when baking the HTML page content.

###### Parameters

- **page_name**: (*str*) Requested page name
- **events**: (*dict*) key=event name, value=event value
- **is_json_data_to_return**: (*bool*) False by default - Boolean value to know if the server return json data or html page

###### Returns

- tuple(*bytes*, HTTPDStatus)





~ Created using [Clamming](https://clamming.sf.net) version 1.5 ~
