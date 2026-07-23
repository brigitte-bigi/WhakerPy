# HTMLMaker package

## Scope

The `htmlmaker` package implements the **HTML layer** of WhakerPy.

It builds an HTML page as a tree of nodes and serializes it into a string
or a file. There is no templating engine: the HTML content is created
**fully dynamically** from Python.

> Neither the integrity of the tree nor the compliance with the HTML
> standard are verified.

This package has **no dependency** on the `httpd` or `webapp` packages.


## Node hierarchy

Every element of a page is a node. All nodes derive from `BaseNode`:

```
BaseNode
├── Doctype                 (leaf, no attribute)
├── HTMLComment             (leaf, no attribute)
├── HTMLTree                (the page: a Doctype and an <html> node)
│   └── HTMLTreeError       (a tree serializing an HTTP error page)
└── BaseTagNode             (a tag with attributes)
    ├── EmptyNode           (a self-closing tag, no child)
    │   ├── HTMLInputText
    │   ├── HTMLImage
    │   ├── HTMLHr
    │   └── HTMLBr
    └── TagNode             (a tag with children)
        └── HTMLNode
            ├── HTMLRadioBox
            ├── HTMLButtonNode
            ├── HTMLHeadNode
            ├── HTMLHeaderNode
            ├── HTMLNavNode
            ├── HTMLMainNode
            ├── HTMLFooterNode
            └── HTMLScriptNode
```

## Modules

| Module | Content |
|--------|---------|
| `basenodes/` | `BaseNode`, `Doctype`, `HTMLComment` |
| `emptynodes/` | `BaseTagNode`, `EmptyNode` and the self-closing tags |
| `htmnodes/` | `TagNode`, `HTMLNode`, `HTMLRadioBox`, `HTMLButtonNode` |
| `treeelts.py` | the body sections: head, header, nav, main, footer, script |
| `treenode.py` | `HTMLTree`, the page assembling all the nodes |
| `treeerror.py` | `HTMLTreeError`, a tree for HTTP error pages |
| `hconsts.py` | the known HTML tags and the self-closing (empty) tags |
| `hexc.py` | the node exceptions (`NodeTagError`, `NodeKeyError`, ...) |


## Typical usage example

```python
>>> # Create a tree. By default, it contains a head node and a body.
>>> # The body is made of several children:
>>> #   body_header, body_nav, body_main, body_footer, body_script
>>> tree = HTMLTree("Home Page")
>>> # Add a title node to the main of the body with the generic method 'element'
>>> tree.element("h1")
>>> # Add a paragraph node to the main of the body. The generic method
>>> # 'element' creates the node and appends it as a child in a single call.
>>> p_node = tree.body_main.element("p", value="This is a paragraph.")
>>> # Serialize the HTML tree into a string
>>> html_content = tree.serialize()
>>> # Serialize the HTML tree into a file
>>> tree.serialize_to_file("/path/to/my/file.html")
```
