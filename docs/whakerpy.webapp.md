# WhakerPy 0.6

## Package `whakerpy.webapp`

### Class `WebSiteData`

#### Description

*Storage class of a webapp configuration, extracted from a JSON file.*

For each dynamic page of a webapp, this class contains the filename of
the page - the one of the URL, its title and the local filename of its
body->main content.

Below is an example of a page description in the JSON parsed file:
"index.html": {
"title": "Home",
"main": "index.htm",
"header": true,
"footer": true
}


#### Constructor

##### __init__

```python
def __init__(self, json_filename=DEFAULT_CONFIG_FILE):
    """Create a WebSiteData instance.

    :param json_filename: (str) Configuration filename.

    """
    self._main_path = ''
    self._default = ''
    self._pages = dict()
    with codecs.open(json_filename, 'r', 'utf-8') as json_file:
        data = json.load(json_file)
        self._main_path = data['pagespath']
        for key in data:
            if key != 'pagespath':
                self._pages[key] = data[key]
                if len(self._default) == 0:
                    self._default = key
```

*Create a WebSiteData instance.*

###### Parameters

- **json_filename**: (*str*) Configuration filename.



#### Public functions

##### get_default_page

```python
def get_default_page(self) -> str:
    """Return the name of the default page."""
    return self._default
```

*Return the name of the default page.*

##### filename

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

###### Parameters

- **page**: (*str*) Name of an HTML page


###### Returns

- (*str*)

##### title

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

###### Parameters

- **page**: (*str*) Name of an HTML page


###### Returns

- (*str*)

##### has_header

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

###### Parameters

- **page**: (*str*) Name of an HTML page


###### Returns

- (*bool*)

##### has_footer

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

###### Parameters

- **page**: (*str*) Name of an HTML page


###### Returns

- (*bool*)



#### Overloads

##### __format__

```python
def __format__(self, fmt):
    return str(self).__format__(fmt)
```



##### __iter__

```python
def __iter__(self):
    for a in self._pages:
        yield a
```



##### __len__

```python
def __len__(self):
    return len(self._pages)
```



##### __contains__

```python
def __contains__(self, value):
    """Value is a page name."""
    return value in self._pages
```

*Value is a page name.*



### Class `WebSiteResponse`

#### Description

*Create an HTML response content.*

Can be used when all pages of a webapp are sharing the same header, nav
and footer. Then, **only one tree** is created for all pages, and its
body->main is changed depending on the requested page.


#### Constructor

##### __init__

```python
def __init__(self, name='index.html', tree=None):
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

###### Parameters

- **name**: (*str*) Filename of the body main content.



#### Public functions

##### page

```python
def page(self) -> str:
    """Override. Return the current HTML page name.

        :return: (str) Name of the file containing the body->main.

        """
    return self._name
```

*Override. Return the current HTML page name.*

###### Returns

- (*str*) Name of the file containing the body->main.



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

###### Parameters

- **events (dict)**: key=event_name, value=event_value


###### Returns

- (*bool*)

##### _invalidate

```python
def _invalidate(self) -> None:
    """Remove all children nodes of the body "main".

        Delete the body main content and nothing else.

        """
    node = self._htree.body_main
    for i in reversed(range(node.children_size())):
        node.pop_child(i)
```

*Remove all children nodes of the body "main".*

Delete the body main content and nothing else.

##### _bake

```python
def _bake(self) -> None:
    """Create the dynamic page content in HTML.

        Load the body->main content from a file and add it to the tree.

        """
    logging.debug(' -> Set {:s} content to the body->main'.format(self._name))
    with codecs.open(self._name, 'r', 'utf-8') as fp:
        lines = fp.readlines()
        self._htree.body_main.set_value(' '.join(lines))
```

*Create the dynamic page content in HTML.*

Load the body->main content from a file and add it to the tree.



### Class `WebSiteApplication`

#### Description

*Create and run a webapp applications.*

Allows to create a server and a response system in order to use HTTPD
like a communication system between a web-browser and a Python API.

The localhost port is randomly assigned.


#### Constructor

##### __init__

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



#### Public functions

##### client_url

```python
def client_url(self) -> str:
    """Return the client URL of this server."""
    return 'http://{:s}:{:d}/'.format(self.__location, self.__port)
```

*Return the client URL of this server.*

##### run

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

###### Returns

- (*int*) Exit status (0=normal)





~ Created using [Clamming](https://clamming.sf.net) version 1.7 ~
