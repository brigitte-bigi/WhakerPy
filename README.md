
```
-----------------------------------------------------------------------------                                                           

 ██╗    ██╗ ██╗  ██╗  █████╗  ██╗  ██╗ ███████╗ ██████╗  ██████╗ ██╗   ██╗
 ██║    ██║ ██║  ██║ ██╔══██╗ ██║ ██╔╝ ██╔════╝ ██╔══██╗ ██╔══██╗╚██╗ ██╔╝
 ██║ █╗ ██║ ███████║ ███████║ █████╔╝  █████╗   ██████╔╝ ██████╔╝ ╚████╔╝ 
 ██║███╗██║ ██╔══██║ ██╔══██║ ██╔═██╗  ██╔══╝   ██╔══██╗ ██╔═══╝   ╚██╔╝  
 ╚███╔███╔╝ ██║  ██║ ██║  ██║ ██║  ██╗ ███████╗ ██║  ██║ ██║        ██║   
  ╚══╝╚══╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝        ╚═╝   
       
   a Python library to create dynamic HTML content and web applications

              Copyright (C) 2023-2026 Brigitte Bigi, CNRS
         Laboratoire Parole et Langage, Aix-en-Provence, France
         
-----------------------------------------------------------------------------                                                              
```

# WhakerPy

## Overview

### Uses cases

You want your users to reach dynamic web pages from a browser, without adopting a full templating stack. WhakerPy is a Python library to build and serve that content.

Django and Flask both render a template file against a model. WhakerPy has no views, no templates and no models: a page is an HTML tree, built and serialized directly in Python.

WhakerPy is your solution if:
- you want a relatively simple web app with a few static or semi-dynamic pages;
- you want full, programmatic control over the generated HTML, without a template language to learn;
- **you want to build and secure a web app with nothing but Python and its standard library**.


### Features

WhakerPy is a free, open-source, self-hosted Python library — not a framework — to build dynamic HTML content and web applications. It stays out of the way: no views, no templates, no models, no third-party dependency for the core library.

* Build an HTML page as a tree of Python objects (`HTMLTree`, `HTMLNode`), then serialize it to a string or to a static file
* Serve pages dynamically with a "bakery" response system that re-renders only what changed
* Deploy the same application three ways, unchanged: as static files, behind the built-in HTTPD dev server, or behind a production WSGI server (Apache, nginx, gunicorn, ...)
* Parse GET query strings, POST bodies (JSON, url-encoded forms) and multipart file uploads yourself — hand-written against the standard library, no `python-multipart`, and no dependency on the `cgi` module removed from Python 3.13
* Protect pages and endpoints with a built-in HTTP security policy, shared by the HTTPD server and the WSGI application:
  - a configurable blacklist rejecting requests by URL path or User-Agent
  - HMAC-SHA256 signed, time-limited URLs (tokens) to share ephemeral links without sessions, cookies or server-side storage — no `itsdangerous`, no `PyJWT`
* Serve static files only after checking Unix read permissions (owner/group/others), so a misconfigured file is never served by accident


### Main advantages

>Build, secure and serve dynamic HTML web applications with nothing but the power of Python!

* easy to learn: one consistent, explicit syntax, from the HTML tag tree to the HTTP response
* a single dependency-free package: HTML generation, HTTPD/WSGI serving, security policy and upload parsing all ship in the Python Standard Library only
* open-source and easily customizable: pure-Python, Object-Oriented, no compiled extension
* portable: runs anywhere Python runs, from a local script to a production WSGI deployment


## How it works

WhakerPy is not Flask, not Django, and does not try to be. There is no template engine and nothing to render: 
a page **is** a tree of Python objects.

### No templates — an HTML tree, in Python

Flask and Django keep a page as a text file (Jinja2 / Django templates) with placeholders (`{% if %}`, `{% for %}`, `{{ variable }}`) filled from a context dictionary at render time. 
That file is not Python: it has its own syntax, its own scoping rules, and its own way of drifting out of sync with the code that feeds it.

WhakerPy has no such file. An `HTMLTree` is a tree of `HTMLNode` objects — `<head>`, `<body>` and every element inside are Python instances, built and traversed with ordinary Python: `if`, `for`, functions, classes. 
To change what gets rendered, write Python; there is no second language to learn:

```python
>>> if user.is_admin:
...     htree.body_main.append_child(HTMLNode(main_id, None, "p", value="Admin panel"))
```

That is the whole of "the WhakerPy templating language".

### One page class, three ways to serve it

A page is a subclass of `BaseResponseRecipe`. `create()` builds the parts of the tree that never change; `bake(events)` runs on every request, decides from the incoming `events` (query string or POST data) whether anything changed, and only rebuilds the dynamic part when it did — a static page is never re-serialized for nothing.

The same recipe instances can then be exposed three ways, without touching the page code:
- `tree.serialize_to_file(...)` — dumped once to a static `.html` file;
- `BaseHTTPDServer` / `HTTPDHandler` — the stdlib `http.server`, for local development or a small deployment with zero extra process;
- `WSGIApplication` — the same recipes, the same bakery, behind any production WSGI server (Apache, nginx + gunicorn/uWSGI, ...).

### Security is a policy, not a decorator

`HTTPDPolicy` sits in front of both servers and is configured once: a blacklist of paths/User-Agents, and a set of HMAC-signed, time-limited URLs. 
It applies identically whether a request comes through the dev HTTPD server or through WSGI in production — one place to configure it, not one per route.

### Minimalism as a security stance

WhakerPy is deliberately small: code that is not written cannot be exploited. The handlers only emit the status codes their own logic actually needs — 200 (OK), 205 (Reset Content, an unhandled GET is still served), 403 (Forbidden), 404 (Not Found, including an expired signed URL), 410 (Gone, shuts the server down), 418 (I'm a Teapot, a blacklisted request), 500 (Internal Server Error) — which covers the large majority of real needs, instead of a generic status-code framework bolted onto every route.

`HTTPDStatus` still validates against the full IANA status registry, so any `BaseResponseRecipe` is free to return whichever code its page actually needs. If the built-in handlers should react to more of them, that is what contributions are for.


## Get and install WhakerPy

Get it from its repository <https://github.com/brigitte-bigi/WhakerPy> or from Pypi <https://pypi.org/project/whakerpy/>, and get documentation <https://whakerpy.sourceforge.io>.

### Install from pypi.org:

```bash
> python -m pip install WhakerPy
```

### Install from its wheel package:

Download the wheel file (WhakerPy-xxx.whl) from it's web page and install it in your python environment with:

```bash
> python -m pip install dist/<WhakerPy-xxx.whl>
```

### From its repo:

Download the latest ".zip" from it's web page and unpack it, or clone the repository with `git`. WhakerPy package includes the following folders and files:

1. "whakerpy": the source code package
2. "docs": the documentation of `whakerpy` library in HTML and Markdown
3. "tests": the tests of the source code
4. "sample": a web application sample 

```bash
> unzip WhakerPy-2.2.zip 
> git clone https://github.com/brigitte-bigi/WhakerPy.git whakerpy-code
> python -m pip install .
```


## Quick Start

### Create a dynamic HTML tree

Open a Python interpreter and type or paste the following:

```python
>>> from whakerpy.htmlmaker import HTMLTree
>>> from whakerpy.htmlmaker import HTMLNode
>>> htree = HTMLTree("index")
>>> node = HTMLNode(htree.body_main.identifier, None, "h1", value="this is a title")
>>> htree.body_main.append_child(node)
```

Render and print the HTML:

```python
>>> print(htree.serialize())
```

and the result is:

```html
<!DOCTYPE html>

<html>
   <head>    </head>
<body>
 <main>
     <h1>
         this is a title
     </h1>
 </main>

</body>
</html>
```

Add some styling and others:

```python
>>> htree.head.title("WhakerPy")
>>> htree.head.meta({"charset": "utf-8"})
>>> htree.head.link(rel="icon", href="/static/favicon.ico")
>>> htree.head.link(rel="stylesheet", href="nice.css", link_type="text/css")
```

Add page copyright in the footer:

```python
>>> copyreg = HTMLNode(htree.body_footer.identifier, "copyright", "p",
>>>                    attributes={"class": "copyright", "role": "none"},
>>>                    value="Copyright &copy; 2023 My Self")
>>> htree.body_footer.append_child(copyreg)
```

Let's view the result in your favorite web browser:

```python
>>> import webbrowser
>>> file_whakerpy = htree.serialize_to_file('file.html')
>>> webbrowser.open_new_tab(file_whakerpy)
```

### Create a web application frontend with dynamic HTML content

For a quick start, see the file `sample.py` in the repo. It shows a very simple 
solution to create a server that can handle dynamic content. This content is 
created from a custom `BaseResponseRecipe()` object, available in the file 
`sample/response.py`. The response is the interface between a local back-end 
python application and the web front-end.


## Projects using WhakerPy

- the website <https://auto-cuedspeech.org>
- the website <https://sppas.org>
- the SPPAS graphical user interface
- the intranet of the Laboratoire Parole et Langage
- *contact the author if your project is based on WhakerPy* and you want it to be included in this list.



# The developer's corner

## Create a wheel

WhakerPy is no system dependent. Information to build its wheel are stored into the file `pyproject.toml`.
The universal wheel is created with: `python -m build`


## Make the documentation

The documentation requires Whakerexa-2.1 <https://whakerexa.sourceforge.io>. 
Download and unzip it into the "docs" folder.

To generate the documentation locally, install the required external program, 
then launch the doc generator:
```bash
>python -m pip install ".[docs]"
>python makedoc.py
```


## Test/Analyze source code

Install the optional dependencies with:

```bash
> python -m pip install ".[tests]"
```

Code coverage can be analyzed with unittest and coverage. 
Install them with the command: `python -m pip install ".[tests]"`.
Then, perform the following steps:

1. `coverage run`
2. `coverage report` to see a summary report into the terminal,
or use this command to get the result in XML format: `coverage xml`

The whakerpy package can be analyzed with SonarQube by following these steps:

1. Download and install Docker
2. Download and install SonarQube: `docker pull sonarqube:latest`
3. Start the SonarQube server: 
   `docker run --stop-timeout 3600 -d --name sonarqube -p 9000:9000 sonarqube:latest`
   Log in to http://localhost:9000. Both login and password are "admin".  
   Add the python plugin and restart server.
4. Click "Add project" with name "WhakerPy", and provide it a token
5. Download sonar-scanner client. On macOS its: `brew install sonar-scanner`.
6. Launch: `sonar-scanner -Dsonar.token="paste the token here"`
7. See results in the opened URL. You may not forget that it's an *automatic* code analyzer, 
   not an *intelligent* one.


## Help / How to contribute

If you want to report a bug, please send an e-mail to the author.
Any and all constructive comments are welcome.

If you plan to contribute to the code, please read carefully and agree both the 
code of conduct and the code style guide.
If you are contributing code or documentation to the WhakerPy project, you are 
agreeing to the DCO certificate <http://developercertificate.org>. 
Copy/paste the DCO, then you just add a line saying:
```
Signed-off-by: Random J Developer <random@developer.example.org>
```
Send this file by e-mail to the author.


# License/Copyright

See the accompanying `LICENSE` and `AUTHORS.md` files for the full list of contributors.

Copyright (C) 2023-2026 [Brigitte Bigi](https://sppas.org/bigi/) - <contact@sppas.org>, CNRS,
Laboratoire Parole et Langage, Aix-en-Provence, France

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.


## How to cite WhakerPy

By using WhakerPy, you are encouraged to mention it in your publications 
or products, in accordance with the best practices of the AGPL license.

Use the following reference to cite WhakerPy:

> Brigitte Bigi. WhakerPy, a Python library to create dynamic HTML content and
> web applications. Version 2.2. 2026. <https://hal.science/hal-04743687>
