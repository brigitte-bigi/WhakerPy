# WhakerPy - a Web HTML maker in Python


## Overview

WhakerPy is an open source library to create dynamic HTML content; it's a light web application framework.

Create and manipulate HTML from the power of Python:

* Easy to learn, consistent, simple syntax.
* Flexible and easy usage.
* Create HTML pages dynamically.
* Can save as static files, and/or
* Run locally with its HTTPD server and response "bakery" system.


## License

WhakerPy is under the terms of the GNU General Public License version 3.


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

Download the repository and unpack it, or clone with `git`. Optionally, it can be installed with:

```bash
> python -m pip install .
```

Install all the optional dependencies with:

```bash
> python -m pip install ".[doc, dev, test]"
```

WhakerPy package includes the following folders and files:

1. "whakerpy": the source code package
2. "doc": the documentation of whakerpy library in HTML and Markdown
3. "sample": a webapp sample
4. "tests": the tests of the source code


## Quick Start

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

## Create a web application frontend with dynamic HTML content

For a quick start, see the file `sample.py` in the repo. It shows a very simple solution to create a server that can handle dynamic content. This content is created from a custom `BaseResponseRecipe()` object, available in the file `samples/response.py`. The response is the interface between a local back-end python application and the web front-end.

For a more complex example of an already in-used web frontend, see: <https://sourceforge.net/p/sppas/code/ci/master/tree/sppas/ui/swapp/app_setup/setupmaker.py>.


## Projects using WhakerPy

WhakerPy was initially developed within SPPAS <https://sppas.org>; it was extracted from its original software by the author to lead its own life as standalone package. The "setup" of SPPAS is entirely based on whakerpy API, and it's website too.

Other projects: 

- the website <https://auto-cuedspeech.org> is entirely based on WhakerPy.
- *contact the author if your project is using whakerpy*


# The developer's corner

## Create a wheel

WhakerPy is no system dependent. Information to build its wheel are stored into the file `pyproject.toml`. 

The universal wheel is created with: `python -m build`


## Make the doc

The API documentation is available in the `doc` folder. Click the file `index.html` to browse throw the documented classes.

To re-generate the doc, install the required external program, then launch the doc generator:
```bash
>python -m pip install ".[doc]"
>python makedoc.py
```


## Test/Analyze source code

Code coverage can be analyzed with unittest and coverage. 
Install them with the command: `python -m pip install ".[test]"`.
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
6. Launch: `sonar-scanner -Dsonar.tokan="paste the token here"`
7. See results in the opened URL. You may not forget that it's an *automatic* code analyzer, 
   not an *intelligent* one.


## How to contribute

If you plan to contribute to the code, please send an e-mail to the author.


## Author/Copyright

Copyright (C) 2023-2024 - Brigitte Bigi - <contact@sppas.org>
Laboratoire Parole et Langage, Aix-en-Provence, France.
