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

## HTMLMaker

Create an HTML tree and to serialize into a page.

### Description

HTMLMaker is a minimalist web framework that can be used to serve HTML
content from Python applications. It does not support templating engines
for generating HTML. Actually, this is a minimalistic system to work with
an HTML Tree and to serialize it into an HTML page. The HTML content is
then created **fully dynamically**.

>Notice that neither the integrity of the tree nor the compliance with HTML standard are verified.

### Typical usage example

>>> # Create a tree. By default, it contains a head node and a body.
>>> # The body is made of several children:
>>> #   body_header, body_nav, body_main, body_footer, body_script
>>> tree = HTMLTree("Home Page")
>>> # Add a title node to the main of the body with the generic method 'element'
>>> tree.element("h1")
>>> # Add a paragraph node to the main of the body
>>> p_node = HTMLNode(tree.body_main.identifier, "my_p_id", 'p', value="This is a paragraph.")
>>> tree.body_main.append_child(p_node)
>>> # Serialize the HTML tree into a string
>>> html_content = tree.serialize()
>>> # Serialize the HTML tree into a file
>>> tree.serialize("/path/to/my/file.html")
