# whakerpy.webapp module

## List of classes

## Class `WebSiteData`

### Description

*Storage class for a web application configuration extracted from a JSON file.*

This class supports the creation of semi-dynamic HTML pages. Each page entry in the JSON
is rendered using the same ResponseReceipe instance, with only the 'body->main' content
loaded from a static file.

For each semi-dynamic page, this class stores:
- the page name (used in the URL),
- the page title,
- the local filename of the main body content.

Example entry in the JSON file:
"index.html": {
"title": "Home",
"main": "index.htm",
"header": true,
"footer": true
}

The 'bake_response' method can return a ResponseReceipe for any page—either semi-dynamic
or fully dynamic. Note that '__contains__' only checks semi-dynamic pages, while 'is_page'
identifies any page that can be baked.


### Constructor

#### __init__

```python
def __init__(self, json_filename: str | None=None):
    """Create a WebSiteData instance.

    :param json_filename: (str) Configuration filename.

    """
    self._main_path = ''
    self._default = ''
    self._pages = dict()
    if json_filename is not None:
        section = self.__get_json_whakerpy_section(json_filename)
        for (raw_name, info) in section.items():
            name = raw_name.lower()
            if name == 'pagespath':
                continue
            self._pages[name] = info
            if self._default == '':
                self._default = name
```

*Create a WebSiteData instance.*

##### Parameters

- **json_filename**: (*str*) Configuration filename.



### Public functions

#### description

```python
@staticmethod
def description() -> str:
    """To be overridden. Return a short description of the website."""
    return 'No description provided.'
```

*To be overridden. Return a short description of the website.*

#### icon

```python
@staticmethod
def icon() -> str:
    """To be overridden. Return the path of the favicon of the website."""
    return ''
```

*To be overridden. Return the path of the favicon of the website.*

#### name

```python
@staticmethod
def name() -> str:
    """To be overridden. Return a short name of the application."""
    return 'NoName'
```

*To be overridden. Return a short name of the application.*

#### get_default_page

```python
def get_default_page(self) -> str:
    """Return the name of the default page."""
    return self._default
```

*Return the name of the default page.*

#### is_page

```python
def is_page(self, page_name: str) -> bool:
    """To be overridden. Return true if the given page name can be baked.

        :param page_name: The name of the page to check.
        :return: (bool) True if the given page name can be baked.

        """
    if page_name in self._pages:
        return True
    return False
```

*To be overridden. Return true if the given page name can be baked.*

##### Parameters

- **page_name**: The name of the page to check.


##### Returns

- (*bool*) True if the given page name can be baked.

#### filename

```python
def filename(self, page: str) -> str:
    """Return the filename of a given page.

        :param page: (str) Name of an HTML page
        :return: (str)

        """
    if page in self._pages:
        main_name = self._pages[page]['main']
        return os.path.join(self._main_path, main_name)
    return ''
```

*Return the filename of a given page.*

##### Parameters

- **page**: (*str*) Name of an HTML page


##### Returns

- (*str*)

#### title

```python
def title(self, page: str) -> str:
    """Return the title of a given page.

        :param page: (str) Name of an HTML page
        :return: (str)

        """
    if page in self._pages:
        if 'title' in self._pages[page]:
            return self._pages[page]['title']
    return ''
```

*Return the title of a given page.*

##### Parameters

- **page**: (*str*) Name of an HTML page


##### Returns

- (*str*)

#### has_header

```python
def has_header(self, page: str) -> bool:
    """Return True if the given page should have the header.

        :param page: (str) Name of an HTML page
        :return: (bool)

        """
    if page in self._pages:
        if 'header' in self._pages[page].keys():
            return self._pages[page]['header']
    return False
```

*Return True if the given page should have the header.*

##### Parameters

- **page**: (*str*) Name of an HTML page


##### Returns

- (*bool*)

#### has_footer

```python
def has_footer(self, page: str) -> bool:
    """Return True if the given page should have the footer.

        :param page: (str) Name of an HTML page
        :return: (bool)

        """
    if page in self._pages:
        if 'footer' in self._pages[page]:
            return self._pages[page]['footer']
    return False
```

*Return True if the given page should have the footer.*

##### Parameters

- **page**: (*str*) Name of an HTML page


##### Returns

- (*bool*)

#### create_pages

```python
def create_pages(self, web_response=WebSiteResponse, default_path: str='') -> dict:
    """Instantiate all pages response from the json.

        :param web_response: (BaseResponseRecipe) the class to used to create the pages,
                            WebSiteResponse class used by default
        :param default_path: (str) None by default, the default path for all pages

        :return: (dict) a dictionary with key = page name and value = the response object

        """
    pages = dict()
    tree = HTMLTree('sample')
    for page_name in self._pages:
        page_path = os.path.join(default_path, self.filename(page_name))
        pages[page_name] = web_response(page_path, tree)
    return pages
```

*Instantiate all pages response from the json.*

##### Parameters

- **web_response**: (BaseResponseRecipe) the class to used to create the pages, WebSiteResponse class used by default
- **default_path**: (*str*) None by default, the default path for all pages

##### Returns

- (*dict*) a dictionary with key = page name and value = the response object

#### bake_response

```python
def bake_response(self, page_name: str, default: str='') -> BaseResponseRecipe | None:
    """Return the bakery system to create the page dynamically.

        To be overridden by subclasses.

        :param page_name: (str) Name of an HTML page
        :param default: (str) The default path
        :return: (BaseResponseRecipe)

        """
    raise NotImplementedError
```

*Return the bakery system to create the page dynamically.*

To be overridden by subclasses.

##### Parameters

- **page_name**: (*str*) Name of an HTML page
- **default**: (*str*) The default path


##### Returns

- (BaseResponseRecipe)



### Protected functions

#### __get_json_whakerpy_section

```python
def __get_json_whakerpy_section(self, filename):
    """Return the configuration section related to WhakerPy.

        - Look for a top‐level "WhakerPy" key (new format).
        - Otherwise use the full JSON (old format) and issue a deprecation warning.

        :param filename: path to JSON configuration file
        :return: dict with keys "pagespath", "<page>.html", …
        :raises: FileNotFoundError: if the file cannot be opened
        :raises: OSError: on other I/O errors reading the file
        :raises: json.JSONDecodeError: if the file is not valid JSON
        :raises: ValueError: if the required "pagespath" key is missing

        """
    with codecs.open(filename, 'r', 'utf-8') as f:
        _full_data = json.load(f)
    if 'WhakerPy' in _full_data:
        _section = _full_data['WhakerPy']
    else:
        logging.warning("DeprecationWarning: starting with WhakerPy 1.2 you must wrap your config in a top-level 'WhakerPy' key.")
        _section = _full_data
    if 'pagespath' not in _section:
        raise ValueError(f"{filename!r} missing required 'pagespath' in WhakerPy section")
    return _section
```

*Return the configuration section related to WhakerPy.*

- Look for a top‐level "WhakerPy" key (new format).
- Otherwise use the full JSON (old format) and issue a deprecation warning.

##### Parameters

- **filename**: path to JSON configuration file


##### Returns

- dict with keys "pagespath", "<page>.html", …


##### Raises

- *FileNotFoundError*: if the file cannot be opened
- *OSError*: on other I/O errors reading the file
- *json.JSONDecodeError*: if the file is not valid JSON
- *ValueError*: if the required "pagespath" key is missing



### Overloads

#### __format__

```python
def __format__(self, fmt):
    return str(self).__format__(fmt)
```



#### __iter__

```python
def __iter__(self):
    for a in self._pages:
        yield a
```



#### __len__

```python
def __len__(self):
    return len(self._pages)
```



#### __contains__

```python
def __contains__(self, value):
    """Value is a page name."""
    return value in self._pages
```

*Value is a page name.*



## Class `WebSiteResponse`

### Description

*Create an HTML response content.*

Can be used when all pages of a webapp are sharing the same header, nav
and footer. Then, **only one tree** is created for all pages, and its
body->main is changed depending on the requested page.


### Constructor

#### __init__

```python
def __init__(self, name='index.html', tree=None, **kwargs):
    """Create a HTTPD Response instance with a default response.

    Useful when creating dynamically the HTML Tree for a webapp.
    The "main" part of the body is re-created every time bake() is invoked.
    Here, it's loaded from a static file.

    :param name: (str) Filename of the body main content.

    """
    self._name = name
    super(WebSiteResponse, self).__init__(name, tree)
    self._status = HTTPDStatus()
    self._bake()
```

*Create a HTTPD Response instance with a default response.*

Useful when creating dynamically the HTML Tree for a webapp.
The "main" part of the body is re-created every time bake() is invoked.
Here, it's loaded from a static file.

##### Parameters

- **name**: (*str*) Filename of the body main content.



### Public functions

#### page

```python
def page(self) -> str:
    """Override. Return the current HTML page name.

        :return: (str) Name of the file containing the body->main.

        """
    return self._name
```

*Override. Return the current HTML page name.*

##### Returns

- (*str*) Name of the file containing the body->main.



### Private functions

#### _process_events

```python
def _process_events(self, events, **kwargs) -> bool:
    """Process the given events.

        The given event name must match a function of the event's manager.
        Processing an event may change the content of the tree. In that case,
        the `dirty` method must be turned into True: it will invalidate the
        deprecated content (_invalidate) and re-generate a new one (_bake).

        :param events (dict): key=event_name, value=event_value
        :return: (bool)

        """
    self._status.code = 200
    return True
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
def _invalidate(self) -> None:
    """Remove all children nodes of the body "main".

        Delete the body main content and nothing else.

        """
    node = self._htree.body_main
    node.clear_children()
```

*Remove all children nodes of the body "main".*

Delete the body main content and nothing else.

#### _bake

```python
def _bake(self) -> None:
    """Create the dynamic page content in HTML.

        Load the body->main content from a file and add it to the tree.

        """
    logging.debug(' -> Set {:s} content to the body->main'.format(self._name))
    with codecs.open(self._name, 'r', 'utf-8') as fp:
        lines = fp.readlines()
        if self._htree.get_body_main() is not None:
            self._htree.body_main.set_value(' '.join(lines))
```

*Create the dynamic page content in HTML.*

Load the body->main content from a file and add it to the tree.



## Class `WebSiteApplication`

### Description

*Create and run a webapp applications.*

Allows to create a server and a response system in order to use HTTPD
like a communication system between a web-browser and a Python API.

The localhost port is randomly assigned.


### Constructor

#### __init__

```python
def __init__(self, server_cls):
    """HTTPD Server initialization.

    Create the application for a Web Front-End based on HTTPD protocol.

    """
    self.__location = 'localhost'
    httpd_port = random.randrange(80, 99)
    self.__port = httpd_port + httpd_port * 100
    self.__server = None
    server_address = (self.__location, self.__port)
    self.__server = server_cls(server_address, HTTPDHandler)
    self.__server.create_pages()
```

*HTTPD Server initialization.*

Create the application for a Web Front-End based on HTTPD protocol.



### Public functions

#### client_url

```python
def client_url(self) -> str:
    """Return the client URL of this server."""
    return 'http://{:s}:{:d}/'.format(self.__location, self.__port)
```

*Return the client URL of this server.*

#### run

```python
def run(self) -> int:
    """Run the application with a main loop.

        :return: (int) Exit status (0=normal)

        """
    try:
        self.__server.serve_forever()
    except KeyboardInterrupt:
        self.__server.shutdown()
    return 0
```

*Run the application with a main loop.*

##### Returns

- (*int*) Exit status (0=normal)



## Class `WSGIApplication`

### Description

*Create the default application for an UWSGI server.*

WSGI response is created from given "environ" parameters and communicated
with start_response.


### Constructor

#### __init__

```python
def __init__(self, default_path: str='', default_filename: str='index.html', web_page_maker=WebSiteResponse, default_web_json: str=None):
    """Initialize the WSGIApplication instance.

    :param default_path: (str) Default root path for static or dynamic pages
    :param default_filename: (str) Default filename to serve if none is provided
    :param web_page_maker: (callable) A callable used to generate dynamic pages
    :param default_web_json: (str) Path to the JSON file for dynamic page definitions

    """
    self.__default_path = default_path
    self.__default_file = default_filename
    self.__dynamic_pages = (web_page_maker, os.path.join(self.__default_path, default_web_json))
    self._pages = dict()
```

*Initialize the WSGIApplication instance.*

##### Parameters

- **default_path**: (*str*) Default root path for static or dynamic pages
- **default_filename**: (*str*) Default filename to serve if none is provided
- **web_page_maker**: (callable) A callable used to generate dynamic pages
- **default_web_json**: (*str*) Path to the JSON file for dynamic page definitions



### Public functions

#### add_page

```python
def add_page(self, page_name: str, response: BaseResponseRecipe) -> bool:
    """Add a page to the list of available pages.

        False is returned if the page already exists or the response has a wrong type.

        :param page_name: (str) the name of the page
        :param response: (BaseResponseRecipe) the response object of the page (has to inherited of BaseResponseRecipe)
        :return: (bool) True if we successfully added the page

        """
    if page_name in self._pages.keys():
        return False
    if isinstance(response, BaseResponseRecipe) is False:
        return False
    self._pages[page_name] = response
    return True
```

*Add a page to the list of available pages.*

False is returned if the page already exists or the response has a wrong type.

##### Parameters

- **page_name**: (*str*) the name of the page
- **response**: (BaseResponseRecipe) the response object of the page (has to inherited of BaseResponseRecipe)


##### Returns

- (*bool*) True if we successfully added the page



### Protected functions

#### __create_dynamic_page

```python
def __create_dynamic_page(self, page_name: str) -> None:
    """Create page dynamically from the json config file.

        :param page_name: (str) Name of the page to bake

        """
    web_data = self.__dynamic_pages[0]
    if hasattr(web_data, 'bake_response'):
        data = web_data(self.__dynamic_pages[1])
        page = data.bake_response(page_name, default=self.__default_path)
        if page is not None:
            self._pages[page_name] = page
    else:
        data = WebSiteData(self.__dynamic_pages[1])
        if page_name in data:
            self._pages[page_name] = web_data(page_name)
```

*Create page dynamically from the json config file.*

##### Parameters

- **page_name**: (*str*) Name of the page to bake

#### __serve_dynamic_content

```python
def __serve_dynamic_content(self, page_name: str, filepath: str, environ, handler_utils) -> tuple:
    """Handle requests for dynamic content or return a 404 if not found."""
    if self.__dynamic_pages[1] is not None and page_name not in self._pages:
        self.__create_dynamic_page(page_name)
    if page_name not in self._pages or filepath != f'{self.__default_path}/{page_name}':
        status = HTTPDStatus(404)
        content = status.to_html(encode=True, msg_error=f'Page not found : {filepath}')
    else:
        (events, accept) = handler_utils.process_post(environ['wsgi.input'])
        (content, status) = HTTPDHandlerUtils.bakery(self._pages, page_name, environ['PATH_INFO'], events, HTTPDHandlerUtils.has_to_return_data(accept))
    return (content, status)
```

*Handle requests for dynamic content or return a 404 if not found.*



### Overloads

#### __call__

```python
def __call__(self, environ, start_response):
    """Handle WSGI requests.

        Process the incoming "environ" dictionary and respond using the given
        start_response callable.

        :param environ: (dict) WSGI environment dictionary with request data
        :param start_response: (callable) Function to start the HTTP response
        :return: (bytes|iterable) Response content to send back to the client

        """
    if 'HTTP_ACCEPT' in environ:
        environ['Accept'] = environ['HTTP_ACCEPT']
    handler_utils = HTTPDHandlerUtils(environ, environ['PATH_INFO'], self.__default_file)
    filepath = self.__default_path + handler_utils.get_path()
    filepath = filepath.replace('//', '/')
    page_name = handler_utils.get_page_name()
    if os.path.exists(filepath) is True:
        (content, status) = handler_utils.static_content(filepath)
    elif os.path.isfile(handler_utils.get_path()[1:]) is True:
        (content, status) = handler_utils.static_content(handler_utils.get_path()[1:])
    else:
        (content, status) = self.__serve_dynamic_content(page_name, filepath, environ, handler_utils)
    if isinstance(content, types.GeneratorType):
        headers = HTTPDHandlerUtils.build_default_headers(filepath, content, varnish=True)
        start_response(repr(status), headers)
        return [c for c in content]
    headers = HTTPDHandlerUtils.build_default_headers(filepath, content)
    start_response(repr(status), headers)
    return [content]
```

*Handle WSGI requests.*

Process the incoming "environ" dictionary and respond using the given
start_response callable.

##### Parameters

- **environ**: (*dict*) WSGI environment dictionary with request data
- **start_response**: (callable) Function to start the HTTP response


##### Returns

- (*bytes*|iterable) Response content to send back to the client

#### __contains__

```python
def __contains__(self, page_name: str) -> bool:
    """Check if a page name exists in the application.

        :param page_name: (str) Name of the page to check
        :return: (bool) True if the page exists, False otherwise

        """
    return page_name in self._pages
```

*Check if a page name exists in the application.*

##### Parameters

- **page_name**: (*str*) Name of the page to check


##### Returns

- (*bool*) True if the page exists, False otherwise





~ Created using [Clamming](https://clamming.sf.net) version 1.8 ~
