# WhakerPy - a Web HTML maker in Python

```
-----------------------------------------------------------------------------                                                           

 ██╗    ██╗ ██╗  ██╗  █████╗  ██╗  ██╗ ███████╗ ██████╗  ██████╗ ██╗   ██╗
 ██║    ██║ ██║  ██║ ██╔══██╗ ██║ ██╔╝ ██╔════╝ ██╔══██╗ ██╔══██╗╚██╗ ██╔╝
 ██║ █╗ ██║ ███████║ ███████║ █████╔╝  █████╗   ██████╔╝ ██████╔╝ ╚████╔╝ 
 ██║███╗██║ ██╔══██║ ██╔══██║ ██╔═██╗  ██╔══╝   ██╔══██╗ ██╔═══╝   ╚██╔╝  
 ╚███╔███╔╝ ██║  ██║ ██║  ██║ ██║  ██╗ ███████╗ ██║  ██║ ██║        ██║   
  ╚══╝╚══╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝        ╚═╝   
       
   a Python library to create dynamic HTML content and web applications

 Copyright (C) 2024 Laboratoire Parole et Langage, Aix-en-Provence, France
-----------------------------------------------------------------------------                                                              
```

## Overview

### Use case

You want all users to get access to dynamic web pages via web browser. You then need to create a web application allowing creating HTML pages and communicating via HTTPD.
WhakerPy is a Python library of such a tool.

In fact, you may have already heard of Django — high-level, full-stack framework, anf Flash — a micro-framework. Both of them generate output in the form of content from the model presented and formatted based on a template file.
The "WhakerPy" library does not offer views, templates or models! On the contrary, it offers a 100% pure-Python solution by creating HTML pages entirely dynamically, or with a static content. 

WhakerPy is your solution if:
- you're looking to design a relatively simple web app with a few static pages; 
- and/or you want a full control on dynamic HTML creation content;
- **you want to build a web app with nothing but Python**.


### Features

WhakerPy is a Python, free, open source, self-hosted library to create dynamic HTML content and web applications. It offers more flexibility than a framework: it's a library!
WhakerPy is then a collection of packages and modules that help developers to create static or dynamic web content without having to worry about the details involved. 

* Build powerful web apps with all the flexibility of Python: building a web app with WhakerPy is as simple as coding with Python 
* Create HTML pages dynamically: create a tree with nodes and serialize the tree into a string
* Can save as static HTML files
* Create a web-frontend with its HTTPD response "bakery" system
* Run locally with its HTTPD server
* Run locally or remotely with its WSGI application


### Main advantages

>Creating and manipulating HTML from the power of Python!

* Easy to learn, consistent, simple syntax
* Flexible and easy usage
* open-source: easily add new features and functionalities 
* easily customizable: it's a pure python library in Object-Oriented Programming
* portable: can be hosted on any web server - as soon as python is available, or used locally
* it is distributed as a single file module and has no dependencies other than the Python Standard Library.

## Install WhakerPy

### From pypi.org:

```bash
> python -m pip install WhakerPy
```

### From its wheel package:

Download the wheel file (WhakerPy-xxx.whl) and install it in your python environment with:

```bash
> python -m pip install dist/<WhakerPy-xxx.whl>
```

### From its repo:

Download the latest ".zip" and unpack it, or clone the repository with `git`. WhakerPy package includes the following folders and files:

1. "whakerpy": the source code package
2. "docs": the documentation of `whakerpy` library in HTML and Markdown
3. "sample": a web application sample 
4. "tests": the tests of the source code

```bash
> unzip WhakerPy-0.6.zip 
> git clone https://git.code.sf.net/p/whakerpy/code whakerpy-code
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

For a quick start, see the file `sample.py` in the repo. It shows a very simple solution to create a server that can handle dynamic content. This content is created from a custom `BaseResponseRecipe()` object, available in the file `samples/response.py`. The response is the interface between a local back-end python application and the web front-end.

For a more complex example of an already in-used application web frontend, see: <https://sourceforge.net/p/sppas/code/ci/master/tree/sppas/ui/swapp/app_setup/setupmaker.py>.


## Projects using WhakerPy

WhakerPy was initially developed within SPPAS <https://sppas.org>. It was extracted from its original software by the author to lead its own life as standalone package. The "setup" of SPPAS is entirely based on `whakerpy` API.

Other projects: 

- the website <https://auto-cuedspeech.org> is entirely based on WhakerPy.
- the website <https://sppas.org> is entirely based on WhakerPy.
- *contact the author if your project is using WhakerPy*


# The developer's corner

## Create a wheel

WhakerPy is no system dependent. Information to build its wheel are stored into the file `pyproject.toml`.
The universal wheel is created with: `python -m build`


## Make the documentation

The API documentation is available in the `docs` folder. Click the file `index.html` to browse throw the documented classes.
The documentation requires Whakerexa <https://whakerexa.sf.net>, which is already available into the "docs" folder of the distributed ".zip" archive of WhakerPy. If not, download and unzip it into the "docs" folder.

To re-generate the documentation, install the required external program, then launch the doc generator:
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

1. `coverage run -m unittest`
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

If you plan to contribute to the code or to report a bug, please send an e-mail to the author.
Any and all constructive comments are welcome.


## License/Copyright

See the accompanying LICENSE and AUTHORS.md files for the full list of contributors.

Copyright (C) 2023-2024 [Brigitte Bigi](https://sppas.org/bigi/) - <contact@sppas.org>
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
