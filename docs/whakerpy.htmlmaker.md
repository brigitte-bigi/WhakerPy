# WhakerPy 0.7

## Package `whakerpy.htmlmaker`

### Class `NodeTypeError`

#### Description

*:ERROR 9110:.*

{!s:s} is not of the expected type 'HTMLNode'.


#### Constructor

##### __init__

```python
def __init__(self, rtype):
    self._status = 9110
    self.parameter = error(self._status) + error(self._status, 'globals').format(rtype)
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





### Class `NodeTagError`

#### Description

*:ERROR 9320:.*

Invalid HTML node tag '{!s:s}'.


#### Constructor

##### __init__

```python
def __init__(self, value):
    self._status = 9320
    self.parameter = error(self._status) + error(self._status, 'globals').format(value)
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





### Class `NodeKeyError`

#### Description

*:ERROR 9400:.*

Invalid node '{!s:s}' for data '{!s:s}'.


#### Constructor

##### __init__

```python
def __init__(self, data_name, value):
    self._status = 9400
    self.parameter = error(self._status) + error(self._status, 'globals').format(value, data_name)
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





### Class `NodeAttributeError`

#### Description

*:ERROR 9330:.*

Invalid HTML node attribute '{!s:s}'.


#### Constructor

##### __init__

```python
def __init__(self, value):
    self._status = 9330
    self.parameter = error(self._status) + error(self._status, 'globals').format(value)
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





### Class `NodeChildTagError`

#### Description

*:ERROR 9325:.*

Invalid HTML child node tag '{!s:s}'.


#### Constructor

##### __init__

```python
def __init__(self, value):
    self._status = 9325
    self.parameter = error(self._status) + error(self._status, 'globals').format(value)
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





### Class `NodeInvalidIdentifierError`

#### Description

*:ERROR 9310:.*

Invalid HTML node identifier '{!s:s}'.


#### Constructor

##### __init__

```python
def __init__(self, value):
    self._status = 9310
    self.parameter = error(self._status) + error(self._status, 'globals').format(value)
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





### Class `NodeIdentifierError`

#### Description

*:ERROR 9410:.*

Expected HTML node identifier {:s}. Got '{!s:s}' instead.


#### Constructor

##### __init__

```python
def __init__(self, expected, value):
    self._status = 9410
    self.parameter = error(self._status) + error(self._status, 'globals').format(expected, value)
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





### Class `NodeParentIdentifierError`

#### Description

*:ERROR 9312:.*

Expected HTML Parent node identifier {:s}. Got '{!s:s}' instead.


#### Constructor

##### __init__

```python
def __init__(self, expected, value):
    self._status = 9312
    self.parameter = error(self._status) + error(self._status, 'globals').format(expected, value)
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





### Class `Doctype`

#### Description

*Represent the HTML doctype of an HTML-5 page.*

###### Example

    >>> d = Doctype()
    >>> d.serialize()
    >>> '<!DOCTYPE html>'

All HTML documents must start with a &lt;!DOCTYPE&gt; declaration.
The declaration is **not** an HTML tag. It is an "information" to the
browser about what document type to expect.

Contrariwise to previous versions, HTML5 does not require any other
information. Then this class does not accept any attribute or value.


#### Constructor

##### __init__

```python
def __init__(self):
    """Create a doctype node with no defined parent."""
    super(Doctype, self).__init__(None, str(uuid.uuid1()))
    self._value = '<!DOCTYPE html>'
```

*Create a doctype node with no defined parent.*



#### Public functions

##### serialize

```python
def serialize(self, nbs: int=4) -> str:
    """Override. Serialize the doctype.

        :param nbs: (int) Number of spaces for the indentation. Un-used.
        :return: (str) Doctype in HTML5.

        """
    return self._value + '\n\n'
```

*Override. Serialize the doctype.*

###### Parameters

- **nbs**: (*int*) Number of spaces for the indentation. Un-used.


###### Returns

- (*str*) Doctype in HTML5.



### Class `HTMLComment`

#### Description

*Represent a comment element.*

The comment tag does not support any standard attributes.


#### Constructor

##### __init__

```python
def __init__(self, parent: str, content: str=' --- '):
    """Create a comment node.

    :param parent: (str) Identifier of the parent node
    :param content: (str) The comment message

    """
    super(HTMLComment, self).__init__(parent, str(uuid.uuid1()))
    self._value = str(content)
```

*Create a comment node.*

###### Parameters

- **parent**: (*str*) Identifier of the parent node
- **content**: (*str*) The comment message



#### Public functions

##### serialize

```python
def serialize(self, nbs: int=4) -> str:
    """Serialize the comment into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
    indent = ' ' * nbs
    html = '\n'
    html += indent + '<!-- '
    r = (70 - len(self._value)) // 2
    if r > 0:
        html += '-' * r
    html += ' ' + self._value + ' '
    if r > 0:
        html += '-' * r
    html += ' -->\n\n'
    return html
```

*Serialize the comment into HTML.*

###### Parameters

- **nbs**: (*int*) Number of spaces for the indentation


###### Returns

- (*str*)



### Class `HTMLImage`

#### Description

*Represent an image element.*

The set_attribute method should be overridden to check if the given key
is in the list of accepted attributes.


#### Constructor

##### __init__

```python
def __init__(self, parent: str, identifier: str, src: str):
    """Create an image leaf node.

    :param parent: (str) Identifier of the parent node
    :param identifier: (str | None) Identifier to assign to the image
    :param src: (str) Image source relative path

    """
    super(HTMLImage, self).__init__(parent, identifier, 'img')
    self.add_attribute('src', src)
    self.add_attribute('alt', '')
```

*Create an image leaf node.*

###### Parameters

- **parent**: (*str*) Identifier of the parent node
- **identifier**: (*str* | None) Identifier to assign to the image
- **src**: (*str*) Image source relative path



### Class `HTMLHr`

#### Description

*Represent a horizontal line with &lt;hr&gt; tag.*

The &lt;hr&gt; tag only supports the Global Attributes in HTML.


#### Constructor

##### __init__

```python
def __init__(self, parent: str):
    """Create a node for &lt;hr&gt; tag.

    """
    super(HTMLHr, self).__init__(parent, None, 'hr')
```

*Create a node for &lt;hr&gt; tag.*





#### Public functions

##### check_attribute

```python
def check_attribute(self, key: str) -> str:
    """Override.

        :return: key (str)
        :raises: NodeAttributeError: if given key can't be converted to string
        :raises: NodeAttributeError: The attribute can't be assigned to this element.

        """
    try:
        key = str(key)
    except Exception:
        raise NodeAttributeError(key)
    if key not in HTML_GLOBAL_ATTR and key.startswith('data-') is False:
        raise NodeAttributeError(key)
    return key
```

*Override.*

###### Returns

- key(*str*)


###### Raises

- *NodeAttributeError*: if given key can't be converted to string
- *NodeAttributeError*: The attribute can't be assigned to this element.



### Class `HTMLBr`

#### Description

*Represent a new line with &lt;br&gt; tag.*

The &lt;br&gt; tag does not support any attribute.


#### Constructor

##### __init__

```python
def __init__(self, parent: str):
    """Create a node for &lt;br&gt; tag.

    """
    super(HTMLBr, self).__init__(parent, None, 'br')
```

*Create a node for &lt;br&gt; tag.*





#### Public functions

##### check_attribute

```python
def check_attribute(self, key: str) -> str:
    """Override. Raise an exception because no attribute is supported.

        :raises: NodeAttributeError: The attribute can't be assigned to this element.

        """
    raise NodeAttributeError(key)
```

*Override. Raise an exception because no attribute is supported.*

###### Raises

- *NodeAttributeError*: The attribute can't be assigned to this element.



### Class `HTMLInputText`

#### Description

*Represent an input text element of a form.*

The set_attribute method should be overridden to check if the given key
is in the list of accepted attributes.


#### Constructor

##### __init__

```python
def __init__(self, parent, identifier):
    """Create an input node. Default type is 'text'. """
    super(HTMLInputText, self).__init__(parent, identifier, 'input')
    self.set_attribute('type', 'text')
    self.set_attribute('id', identifier)
    self.set_attribute('name', identifier)
```

*Create an input node. Default type is 'text'.*



#### Public functions

##### set_name

```python
def set_name(self, name):
    """Set input name attribute, and 'id' too.

        :param name: (str)

        """
    self.set_attribute('id', name)
    self.set_attribute('name', name)
```

*Set input name attribute, and 'id' too.*

###### Parameters

- **name**: (*str*)



### Class `HTMLRadioBox`

#### Description

*Represent a form with one or several input of radio type.*




#### Constructor

##### __init__

```python
def __init__(self, parent, identifier):
    """Create a form node."""
    attributes = dict()
    attributes['method'] = 'POST'
    attributes['name'] = identifier
    attributes['id'] = identifier
    super(HTMLRadioBox, self).__init__(parent, identifier, 'form', attributes=attributes)
```

*Create a form node.*



#### Public functions

##### append_input

```python
def append_input(self, class_name, value, text=None, checked=False):
    """Append a label tag with an input and a span.

        :param class_name: (str) Used for both the CSS class of the label and the name of the input
        :param value: (str) input value
        :param text: (str) span tag content
        :param checked: (bool)

        """
    label_attributes = dict()
    label_attributes['class'] = str(class_name)
    if 'button' not in class_name:
        label_attributes['class'] = 'button ' + class_name
    if checked is True:
        label_attributes['class'] += ' checked'
    label_node = HTMLNode(self.identifier, None, 'label', attributes=label_attributes)
    self.append_child(label_node)
    input_attributes = dict()
    input_attributes['type'] = 'radio'
    input_attributes['name'] = class_name
    input_attributes['value'] = value
    if checked is True:
        input_attributes['checked'] = None
    input_node = BaseTagNode(label_node.identifier, None, 'input', attributes=input_attributes)
    label_node.append_child(input_node)
    if text is not None:
        span_node = HTMLNode(label_node.identifier, None, 'span', value=text)
    else:
        span_node = HTMLNode(label_node.identifier, None, 'span', value=value)
    label_node.append_child(span_node)
```

*Append a label tag with an input and a span.*

###### Parameters

- **class_name**: (*str*) Used for both the CSS class of the label and the name of the input
- **value**: (*str*) input value
- **text**: (*str*) span tag content
- **checked**: (*bool*)



### Class `HTMLButtonNode`

#### Description

*Represent a button element.*

The set_attribute method should be overridden to check if the given key
is in the list of accepted attributes.


#### Constructor

##### __init__

```python
def __init__(self, parent, identifier, attributes=dict()):
    """Create an input node. Default type is 'text'.

    """
    super(HTMLButtonNode, self).__init__(parent, identifier, 'button', attributes=attributes)
    if 'id' not in attributes:
        self.add_attribute('id', self.identifier)
    if 'name' not in attributes:
        self.add_attribute('name', self.identifier)
    if 'type' not in attributes:
        self.add_attribute('type', 'button')
```

*Create an input node. Default type is 'text'.*





#### Public functions

##### set_icon

```python
def set_icon(self, icon, attributes=dict()):
    """Set an icon to the button from its filename.

        :param icon: (str) Name of an icon in the app.
        :param attributes: (dict).

        """
    node = HTMLImage(self.identifier, None, src=icon)
    if len(attributes) > 0:
        for key in attributes:
            node.set_attribute(key, attributes[key])
    self.append_child(node)
    return node
```

*Set an icon to the button from its filename.*

###### Parameters

- **icon**: (*str*) Name of an icon in the app.
- **attributes**: (*dict*).

##### set_text

```python
def set_text(self, ident, text, attributes=dict()):
    """Set a text to the button.

        :param ident: (str) Identifier for the span text.
        :param text: (str) Button text.
        :param attributes: (dict)

        """
    node = HTMLNode(self.identifier, ident, 'span', value=text, attributes=attributes)
    if ident is not None:
        node.set_attribute('id', ident)
    self.append_child(node)
    if ident is not None:
        self.set_attribute('aria-labelledby', node.identifier)
    return node
```

*Set a text to the button.*

###### Parameters

- **ident**: (*str*) Identifier for the span text.
- **text**: (*str*) Button text.
- **attributes**: (*dict*)



### Class `BaseNode`

#### Description

*A base class for any node in an HTML tree.*

An HTML element without content is called an empty node. It has a
start tag but neither a content nor an end tag. It has only attributes.

The BaseNode() class is a base class for any of these HTML elements.
It is intended to be overridden.


#### Constructor

##### __init__

```python
def __init__(self, parent: str=None, identifier: str=None, **kwargs):
    """Create a new base node.

    :param parent: (str) Parent identifier
    :param identifier: (str) This node identifier
    :raises: NodeInvalidIdentifierError: if 'identifier' contains invalid characters or if invalid length

    """
    if identifier is not None:
        ident = BaseNode.validate_identifier(identifier)
        self.__identifier = ident
    else:
        self.__identifier = str(uuid.uuid1())
    self._parent = None
    self.set_parent(parent)
```

*Create a new base node.*

###### Parameters

- **parent**: (*str*) Parent identifier
- **identifier**: (*str*) This node identifier


###### Raises

- *NodeInvalidIdentifierError*: if 'identifier' contains invalid characters or if invalid length



#### Public functions

##### validate_identifier

```python
@staticmethod
def validate_identifier(identifier: str) -> str:
    """Return the given identifier if it matches the requirements.

        An identifier should contain at least 1 character and no whitespace.

        :param identifier: (str) Key to be validated
        :raises: NodeInvalidIdentifierError: if it contains invalid characters
        :raises: NodeInvalidIdentifierError: if invalid length
        :return: (str) Validated identifier

        """
    entry = BaseNode.full_strip(identifier)
    if len(entry) != len(identifier):
        raise NodeInvalidIdentifierError(identifier)
    if len(identifier) == 0:
        raise NodeInvalidIdentifierError(identifier)
    return identifier
```

*Return the given identifier if it matches the requirements.*

An identifier should contain at least 1 character and no whitespace.

###### Parameters

- **identifier**: (*str*) Key to be validated


###### Raises

- *NodeInvalidIdentifierError*: if it contains invalid characters
- *NodeInvalidIdentifierError*: if invalid length


###### Returns

- (*str*) Validated identifier

##### full_strip

```python
@staticmethod
def full_strip(entry):
    """Fully strip the string: multiple whitespace, tab and CR/LF.

        :return: (str) Cleaned string

        """
    e = re.sub('[\\s]+', '', entry)
    e = re.sub('[\t]+', '', e)
    e = re.sub('[\n]+', '', e)
    e = re.sub('[\r]+', '', e)
    if '\ufeff' in e:
        e = re.sub('\ufeff', '', e)
    return e
```

*Fully strip the string: multiple whitespace, tab and CR/LF.*

###### Returns

- (*str*) Cleaned string

##### identifier

```python
@property
def identifier(self) -> str:
    """Return the (supposed-) unique ID of the node within the scope of a tree. """
    return self.__identifier
```

*Return the (supposed-) unique ID of the node within the scope of a tree.*

##### is_leaf

```python
def is_leaf(self) -> bool:
    """Return true if node has no children."""
    return True
```

*Return true if node has no children.*

##### is_root

```python
def is_root(self) -> bool:
    """Return true if node has no parent, i.e. like root."""
    return self._parent is None
```

*Return true if node has no parent, i.e. like root.*

##### get_parent

```python
def get_parent(self) -> str:
    """The parent identifier.

        :return: (str) node identifier

        """
    return self._parent
```

*The parent identifier.*

###### Returns

- (*str*) node identifier

##### set_parent

```python
def set_parent(self, node_id: str) -> None:
    """Set the parent identifier.

        :param node_id: (str) Identifier of the parent

        """
    if self.__identifier == node_id:
        raise NodeKeyError(self.__identifier, node_id)
    self._parent = node_id
```

*Set the parent identifier.*

###### Parameters

- **node_id**: (*str*) Identifier of the parent

##### has_child

```python
def has_child(self, node_id: str) -> bool:
    """To be overriden. Return True if the given node ID is a direct child.

        :param node_id: (str) Identifier of the node
        :return: (bool) True if given identifier is a direct child.

        """
    return not self.is_leaf()
```

*To be overriden. Return True if the given node ID is a direct child.*

###### Parameters

- **node_id**: (*str*) Identifier of the node


###### Returns

- (*bool*) True if given identifier is a direct child.

##### serialize

```python
def serialize(self, nbs: int=4) -> str:
    """To be overriden. Serialize the node into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
    return ''
```

*To be overriden. Serialize the node into HTML.*

###### Parameters

- **nbs**: (*int*) Number of spaces for the indentation


###### Returns

- (*str*)



#### Overloads

##### __repr__

```python
def __repr__(self):
    return self.serialize()
```



##### __str__

```python
def __str__(self):
    return 'Node ({:s})'.format(self.identifier)
```





### Class `BaseTagNode`

#### Description

*A node to represents an HTML element with attributes.*

An HTML element without content is called an empty node. It has a
start tag but neither a content nor an end tag.
Compared to the parent class BaseNode, this class adds 2 members:

1. the required element tag;
2. its optional attributes.

For example, it can deal with elements like:

- &lt;tag /&gt;
- &lt;tag k=v /&gt;
- &lt;tag k1=v2 k2=v2 k3 /&gt;


#### Constructor

##### __init__

```python
def __init__(self, parent: str | None, identifier: str, tag: str, attributes: dict=dict()):
    """Create a new empty node.

    :param parent: (str) Parent identifier
    :param identifier: (str) This node identifier
    :param tag: (str) The element tag. Converted in lower case.
    :param attributes: (dict) key=(str) value=(str or None)
    :raises: NodeInvalidIdentifierError:
    :raises: NodeTagError:
    :raises: TypeError:

    """
    super(BaseTagNode, self).__init__(parent, identifier)
    tag = str(tag)
    self.__tag = tag.lower()
    self._attributes = dict()
    if isinstance(attributes, dict) is False:
        raise TypeError('Expected a dict for the attributes argument of BaseTagNode().')
    for key in attributes:
        value = attributes[key]
        self.add_attribute(key, value)
```

*Create a new empty node.*

###### Parameters

- **parent**: (*str*) Parent identifier
- **identifier**: (*str*) This node identifier
- **tag**: (*str*) The element tag. Converted in lower case.
- **attributes**: (*dict*) key=(str) value=(str or None)


###### Raises

- *NodeInvalidIdentifierError*
- *NodeTagError*
- *TypeError*



#### Public functions

##### tag

```python
@property
def tag(self) -> str:
    """Return the HTML tag. """
    return self.__tag
```

*Return the HTML tag.*

##### check_attribute

```python
def check_attribute(self, key) -> str:
    """Raises NodeAttributeError if key is not a valid attribute.

        :param key: (any) An attribute
        :raises: NodeAttributeError: The attribute can't be assigned to this element.
        :raises: NodeAttributeError: if given key can't be converted to string
        :return: key (str) valid key

        """
    try:
        key = str(key)
        key = key.lower()
    except Exception:
        raise NodeAttributeError(key)
    if key not in HTML_GLOBAL_ATTR and key.startswith('data-') is False and (key not in HTML_VISIBLE_ATTR) and (key not in HTML_TAG_ATTR.keys()) and (key not in ARIA_TAG_ATTR.keys()):
        raise NodeAttributeError(key)
    return key
```

*Raises NodeAttributeError if key is not a valid attribute.*

###### Parameters

- **key**: (any) An attribute


###### Raises

- *NodeAttributeError*: The attribute can't be assigned to this element.
- *NodeAttributeError*: if given key can't be converted to string


###### Returns

- key(*str*) valid key

##### get_attribute_keys

```python
def get_attribute_keys(self) -> list:
    """Return the list of attribute keys. """
    return [k for k in self._attributes.keys()]
```

*Return the list of attribute keys.*

##### set_attribute

```python
def set_attribute(self, key: str, value) -> str:
    """Set a property to the node. Delete the existing one, if any.

        :param key: Key property
        :param value: (str or list)
        :raises: NodeAttributeError: The attribute can't be assigned to this element.
        :raises: NodeAttributeError: if given key can't be converted to string
        :return: key (str) valid assigned key

        """
    key = self.check_attribute(key)
    if isinstance(value, (list, tuple)) is True:
        value = ' '.join(value)
    self._attributes[key] = value
    return key
```

*Set a property to the node. Delete the existing one, if any.*

###### Parameters

- **key**: Key property
- **value**: (*str* or *list*)


###### Raises

- *NodeAttributeError*: The attribute can't be assigned to this element.
- *NodeAttributeError*: if given key can't be converted to string


###### Returns

- key(*str*) valid assigned key

##### add_attribute

```python
def add_attribute(self, key: str, value) -> str:
    """Add a property to the node. Append the value if existing.

        :param key: (str) Key property
        :param value:
        :raises: NodeAttributeError: The attribute can't be assigned to this element.
        :raises: NodeAttributeError: if given key can't be converted to string
        :return: key (str) valid assigned key

        """
    if key not in self._attributes:
        self.set_attribute(key, value)
    elif self._attributes[key] is not None:
        self._attributes[key] += ' ' + value
    else:
        self._attributes[key] = value
    return key
```

*Add a property to the node. Append the value if existing.*

###### Parameters

- **key**: (*str*) Key property
- **value**


###### Raises

- *NodeAttributeError*: The attribute can't be assigned to this element.
- *NodeAttributeError*: if given key can't be converted to string


###### Returns

- key(*str*) valid assigned key

##### get_attribute_value

```python
def get_attribute_value(self, key: str):
    """Return the attribute value if the node has this attribute.

        :param key: (str) Attribute key
        :return: (str | None) Value or None if the attribute does not exist or has no value

        """
    if key in self._attributes:
        return self._attributes[key]
    return None
```

*Return the attribute value if the node has this attribute.*

###### Parameters

- **key**: (*str*) Attribute key


###### Returns

- (*str* | None) Value or None if the attribute does not exist or has no value

##### has_attribute

```python
def has_attribute(self, key: str) -> bool:
    """Return true if the node has the attribute.

        :param key: (str) Attribute key
        :return: (bool)

        """
    return key in self._attributes
```

*Return true if the node has the attribute.*

###### Parameters

- **key**: (*str*) Attribute key


###### Returns

- (*bool*)

##### remove_attribute

```python
def remove_attribute(self, key: str) -> None:
    """Remove the attribute to the node.

        :param key: (str) Attribute key

        """
    if key in self._attributes:
        del self._attributes[key]
```

*Remove the attribute to the node.*

###### Parameters

- **key**: (*str*) Attribute key

##### remove_attribute_value

```python
def remove_attribute_value(self, key: str, value: str) -> None:
    """Remove the value of an attribute of the node.

        :param key: (str) Attribute key
        :param value: (str) Attribute value

        """
    if key in self._attributes:
        values = self._attributes[key].split(' ')
        if value in values:
            values.remove(value)
            if len(values) == 0:
                del self._attributes[key]
            else:
                self.set_attribute(key, ' '.join(values))
```

*Remove the value of an attribute of the node.*

###### Parameters

- **key**: (*str*) Attribute key
- **value**: (*str*) Attribute value

##### nb_attributes

```python
def nb_attributes(self) -> int:
    """Return the number of attributes. """
    return len(self._attributes)
```

*Return the number of attributes.*

##### serialize

```python
def serialize(self, nbs: int=4) -> str:
    """Override. Serialize the node into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
    indent = ' ' * nbs
    html = indent + '<' + self.__tag
    for key in self._attributes:
        html += ' '
        html += key
        value = self._attributes[key]
        if value is not None:
            html += '="'
            html += value
            html += '"'
    html += ' />\n'
    return html
```

*Override. Serialize the node into HTML.*

###### Parameters

- **nbs**: (*int*) Number of spaces for the indentation


###### Returns

- (*str*)



### Class `EmptyNode`

#### Description

*A node to represents an HTML empty element.*

An HTML element without content is called an empty node. It has a
start tag but neither a content nor an end tag.


#### Constructor

##### __init__

```python
def __init__(self, parent: str, identifier: str, tag: str, attributes: dict=dict()):
    """Create a new empty node.

    :param parent: (str) Parent identifier
    :param identifier: (str) This node identifier
    :param tag: (str) The element tag
    :param attributes: (dict) key=(str) value=(str or None)
    :raises: NodeInvalidIdentifierError:
    :raises: NodeTagError:
    :raises: TypeError:

    """
    super(EmptyNode, self).__init__(parent, identifier, tag, attributes)
    if self.tag not in HTML_EMPTY_TAGS.keys():
        raise NodeTagError(tag)
```

*Create a new empty node.*

###### Parameters

- **parent**: (*str*) Parent identifier
- **identifier**: (*str*) This node identifier
- **tag**: (*str*) The element tag
- **attributes**: (*dict*) key=(str) value=(str or None)


###### Raises

- *NodeInvalidIdentifierError*
- *NodeTagError*
- *TypeError*



### Class `HTMLNode`

#### Constructor

##### __init__

```python
def __init__(self, parent: str, identifier: str, tag: str, attributes=dict(), value=None):
    """Create a tag node to represent any HTML element.

    :param parent: (str) Parent identifier
    :param identifier: (str) This node identifier
    :raises: NodeTagError: Invalid tag. Not in the HTML_TAGS list.

    """
    self._children = list()
    super(HTMLNode, self).__init__(parent, identifier, tag, attributes)
    if self.tag not in HTML_TAGS.keys():
        raise NodeTagError(tag)
    self._value = value
```

*Create a tag node to represent any HTML element.*

###### Parameters

- **parent**: (*str*) Parent identifier
- **identifier**: (*str*) This node identifier


###### Raises

- *NodeTagError*: Invalid tag. Not in the HTML_TAGS list.



### Class `HTMLHeadNode`

#### Description

*Convenient class to represent the head node of an HTML tree.*

Children of a "head" node are limited to the ones of HEAD_TAGS list.


#### Constructor

##### __init__

```python
def __init__(self, parent):
    """Create the head node."""
    super(HTMLHeadNode, self).__init__(parent, 'head', 'head')
```

*Create the head node.*



#### Public functions

##### append_child

```python
def append_child(self, node) -> None:
    """Append a child node.

        :param node: (Node)
        :raise: NodeChildTagError: if invalid child tag (not in HEAD_TAGS list)

        """
    if node.tag not in HEAD_TAGS:
        raise NodeChildTagError(node.tag)
    HTMLNode.append_child(self, node)
```

*Append a child node.*

###### Parameters

- **node**: (Node)


###### Raises

- *NodeChildTagError*: if invalid child tag (not in HEAD_TAGS list)

##### insert_child

```python
def insert_child(self, pos, node) -> None:
    """Insert a child node at the given index.

        :param pos: (int) Index position
        :param node: (Node)

        """
    if node.tag not in HEAD_TAGS:
        raise NodeChildTagError(node.tag)
    HTMLNode.insert_child(self, pos, node)
```

*Insert a child node at the given index.*

###### Parameters

- **pos**: (*int*) Index position
- **node**: (Node)

##### title

```python
def title(self, title) -> None:
    """Set the title to the header.

        :param title: (str) The page title (expected short!)

        """
    for child in self._children:
        if child.identifier == 'title':
            child.set_value(title)
            break
```

*Set the title to the header.*

###### Parameters

- **title**: (*str*) The page title (expected short!)

##### meta

```python
def meta(self, metadict) -> None:
    """Append a new meta tag to the header.

        :param metadict: (dict)

        """
    if isinstance(metadict, dict) is False:
        raise TypeError('Expected a dict.')
    child_node = EmptyNode(self.identifier, None, 'meta', attributes=metadict)
    self._children.append(child_node)
```

*Append a new meta tag to the header.*

###### Parameters

- **metadict**: (*dict*)

##### link

```python
def link(self, rel: str, href: str, link_type: str=None) -> None:
    """Add a link tag to the header.

        :param rel: (str)
        :param href: (str) Path and/or name of the link reference
        :param link_type: (str) Mimetype of the link file

        """
    d = dict()
    d['rel'] = rel
    if len(href) > 0 and href[0].isalpha():
        d['href'] = os.sep + href
    else:
        d['href'] = href
    if link_type is not None:
        d['type'] = link_type
    child_node = EmptyNode(self.identifier, None, 'link', attributes=d)
    self._children.append(child_node)
```

*Add a link tag to the header.*

###### Parameters

- **rel**: (*str*)
- **href**: (*str*) Path and/or name of the link reference
- **link_type**: (*str*) Mimetype of the link file

##### script

```python
def script(self, src, script_type) -> None:
    """Add a meta tag to the header.

        :param src: (str) Script source file or Script content
        :param script_type: (str) Script type or None if script content

        """
    if script_type is not None:
        d = dict()
        d['type'] = script_type
        if len(src) > 0 and src[0].isalpha():
            d['src'] = os.sep + src
        else:
            d['src'] = src
        child_node = HTMLNode(self.identifier, None, 'script', attributes=d)
        self._children.append(child_node)
    else:
        child_node = HTMLNode(self.identifier, None, 'script', value=str(src))
        self._children.append(child_node)
```

*Add a meta tag to the header.*

###### Parameters

- **src**: (*str*) Script source file or Script content
- **script_type**: (*str*) Script type or None if script content

##### css

```python
def css(self, css_content) -> None:
    """Append css style content.

        :param script_content: (str) CSS content

        """
    child_node = HTMLNode(self.identifier, None, 'style', value=str(css_content))
    self._children.append(child_node)
```

*Append css style content.*

###### Parameters

- **script_content**: (*str*) CSS content



### Class `HTMLHeaderNode`

#### Description

*Convenient class to represent the header node of an HTML tree.*




#### Constructor

##### __init__

```python
def __init__(self, parent):
    """Create the main node.

    """
    super(HTMLHeaderNode, self).__init__(parent, 'body_header', 'header')
```

*Create the main node.*





### Class `HTMLNavNode`

#### Description

*Convenient class to represent the nav node of an HTML tree.*




#### Constructor

##### __init__

```python
def __init__(self, parent):
    """Create the nav node."""
    super(HTMLNavNode, self).__init__(parent, 'body_nav', 'nav')
```

*Create the nav node.*



### Class `HTMLMainNode`

#### Description

*Convenient class to represent the main node of an HTML tree.*




#### Constructor

##### __init__

```python
def __init__(self, parent):
    """Create the main node."""
    super(HTMLMainNode, self).__init__(parent, 'body_main', 'main')
```

*Create the main node.*



### Class `HTMLFooterNode`

#### Description

*Convenient class to represent the footer node of an HTML tree.*




#### Constructor

##### __init__

```python
def __init__(self, parent):
    """Create the footer node."""
    super(HTMLFooterNode, self).__init__(parent, 'body_footer', 'footer')
```

*Create the footer node.*



### Class `HTMLScriptNode`

#### Description

*Convenient class to represent the scripts node of an HTML tree.*


#### Constructor

##### __init__

```python
def __init__(self, parent):
    """Create the script node."""
    super(HTMLScriptNode, self).__init__(parent, 'body_script', 'script')
```

*Create the script node.*



### Class `HTMLTree`

#### Description

*Root of an HTML tree.*

Since the early days of the World Wide Web, there have been many versions:
[source: <https://www.w3schools.com/html/html_intro.asp>]

-    1989:  Tim Berners-Lee invented www
-    1991:  Tim Berners-Lee invented HTML
-    1993:  Dave Raggett drafted HTML+
-    1995:  HTML Working Group defined HTML 2.0
-    1997:  W3C Recommendation: HTML 3.2
-    1999:  W3C Recommendation: HTML 4.01
-    2000:  W3C Recommendation: XHTML 1.0
-    2008:  WHATWG HTML5 First Public Draft
-    2012:  WHATWG HTML5 Living Standard
-    2014:  W3C Recommendation: HTML5
-    2016:  W3C Candidate Recommendation: HTML 5.1
-    2017:  W3C Recommendation: HTML5.1 2nd Edition
-    2017:  W3C Recommendation: HTML5.2

HTML elements are generally made of a start tag, an optional element
content, and an end tag. However, several elements have only a start
tag, like "br" or "img", and a few elements don't have tag at all,
like comments.

An HTMLTree has two children: a doctype node, and a "html" node.
The "html" tag is the container for all HTML elements of the page.
The following properties allow to access to "html" children nodes:

- head
- body_header
- body_nav
- body_main
- body_footer
- body_script

###### Example

    >>> # Create the tree
    >>> htree = HTMLTree("index")
    >>> htree.add_html_attribute("lang", "en")
    >>> # Fill in the <head> element node with:
    >>> # a title, a meta and a link
    >>> htree.head.title("Purpose")
    >>> htree.head.meta({"charset": "utf-8"})
    >>> htree.head.link(rel="icon", href="/static/favicon.ico")
    >>> # Fill in the <body> element node with:
    >>> # A <nav> tag in the header, a <h1> tag in the body and a <p> tag in the footer
    >>> htree.set_body_attribute("class", "colors_scheme_dark")
    >>> nav = HTMLNode(htree.body_header.identifier, "navmenu", "nav")
    >>> htree.body_header.append_child(nav)
    >>> node = HTMLNode(htree.body_main.identifier, None, "h1", value="this is a title")
    >>> htree.body_main.append_child(node)
    >>> node = HTMLNode(htree.body_footer.identifier, None, "p", value="&copy; me now")
    >>> htree.body_footer.append_child(node)
    >>> # Save into a file
    >>> htree.serialize_to_file("/path/to/file.html")

This class does not support yet the global attributes -- i.e. attributes
that can be used with all HTML elements.
See <https://www.w3schools.com/TAgs/ref_standardattributes.asp>


#### Constructor

##### __init__

```python
def __init__(self, identifier: str):
    """Create the tree root and children nodes.

    The created tree matches the HTML5 recommendations for the document
    structure. The HTML tree has 2 children: a doctype and an HTML element.
    The HTML node has 2 children: the "head" and the "body". The body
    has 5 children: "header", "nav", "main", "footer", "script".
    The empty nodes are not serialized.

    :param identifier: (str) An identifier for the tree node.

    """
    super(HTMLTree, self).__init__(parent=None, identifier=identifier)
    self.__doctype = Doctype()
    self.__html = HTMLNode(identifier, None, 'html')
    self.__html.append_child(HTMLHeadNode(self.__html.identifier))
    body = HTMLNode(self.__html.identifier, 'body', 'body')
    self.__html.append_child(body)
    body.append_child(HTMLHeaderNode(body.identifier))
    body.append_child(HTMLNavNode(body.identifier))
    body.append_child(HTMLMainNode(body.identifier))
    body.append_child(HTMLFooterNode(body.identifier))
    body.append_child(HTMLScriptNode(body.identifier))
```

*Create the tree root and children nodes.*

The created tree matches the HTML5 recommendations for the document
structure. The HTML tree has 2 children: a doctype and an HTML element.
The HTML node has 2 children: the "head" and the "body". The body
has 5 children: "header", "nav", "main", "footer", "script".
The empty nodes are not serialized.

###### Parameters

- **identifier**: (*str*) An identifier for the tree node.



#### Public functions

##### set_parent

```python
def set_parent(self, node_id: str) -> None:
    """Override. Do not set the parent identifier. """
    return None
```

*Override. Do not set the parent identifier.*

##### is_leaf

```python
def is_leaf(self) -> bool:
    """Override. Return False. """
    return False
```

*Override. Return False.*

##### add_html_attribute

```python
def add_html_attribute(self, key: str, value: str) -> None:
    """Add or append a property to the HTML node.

        :param key: (str) Key property of an HTML attribute
        :param value: (str) Value of the attribute

        :Raises: NodeTypeError: if key or value is not a string
        :Raises: NodeAttributeError: if unknown key.

        """
    self.__html.add_attribute(key, value)
```

*Add or append a property to the HTML node.*

###### Parameters

- **key**: (*str*) Key property of an HTML attribute
- **value**: (*str*) Value of the attribute

###### Raises

- *NodeTypeError*: if key or value is not a string
- *NodeAttributeError*: if unknown key.

##### get_body_attribute_value

```python
def get_body_attribute_value(self, key: str) -> str:
    """Get the attribute value of the body element node.

        :param key: (str) Key property of an HTML attribute
        :return: (str) The attribute value of the <body> element

        """
    return self._get_body().get_attribute_value(key)
```

*Get the attribute value of the body element node.*

###### Parameters

- **key**: (*str*) Key property of an HTML attribute


###### Returns

- (*str*) The attribute value of the <body> element

##### add_body_attribute

```python
def add_body_attribute(self, key: str, value: str) -> str:
    """Add an attribute to the body element node.

        :param key: (str) Key property of an HTML attribute
        :param value: (str) Value of the attribute
        :Raises: NodeTypeError: if key or value is not a string
        :raises: NodeAttributeError: if unknown key
        :return: normalized key

        """
    return self._get_body().add_attribute(key, value)
```

*Add an attribute to the body element node.*

###### Parameters

- **key**: (*str*) Key property of an HTML attribute
- **value**: (*str*) Value of the attribute


###### Raises

- *NodeTypeError*: if key or value is not a string
- *NodeAttributeError*: if unknown key


###### Returns

- normalized key

##### set_body_attribute

```python
def set_body_attribute(self, key: str, value: str) -> None:
    """Set an attribute of the body.

        :param key: (str) Key property of an HTML attribute
        :param value: (str) Value of the attribute
        :return: (bool) The attribute is set

        """
    self._get_body().set_attribute(key, value)
```

*Set an attribute of the body.*

###### Parameters

- **key**: (*str*) Key property of an HTML attribute
- **value**: (*str*) Value of the attribute


###### Returns

- (*bool*) The attribute is set

##### get_body_identifier

```python
def get_body_identifier(self) -> str:
    """Return the identifier of the body node.

        :return: (str) the identifier of the body node.

        """
    return self._get_body().identifier
```

*Return the identifier of the body node.*

###### Returns

- (*str*) the identifier of the body node.

##### insert_body_child

```python
def insert_body_child(self, child: HTMLNode, index: int=0) -> None:
    """Insert a html node in the body.

        :param child: (HTMLNode) the node to append in the body
        :param index: (int) Optional, the index where insert the child, by default the index is set to 0

        :raises ValueError: If the index is negative

        """
    if index < 0:
        raise ValueError("The index can't be negative !")
    self._get_body().insert_child(index, child)
```

*Insert a html node in the body.*

###### Parameters

- **child**: (HTMLNode) the node to append in the body
- **index**: (*int*) Optional, the index where insert the child, by default the index is set to 0

###### Raises

- *ValueError*: If the index is negative

##### get_head

```python
def get_head(self) -> HTMLNode:
    """Get the head node element.

        :return: (HTMLNode) Head node element

        """
    return self.__html.get_child('head')
```

*Get the head node element.*

###### Returns

- (HTMLNode) Head node element

##### set_head

```python
def set_head(self, head_node: HTMLNode) -> None:
    """Replace the current head node by the given one.

        :param head_node: (HTMLNode)

        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :raises: NodeIdentifierError: if head_node identifier is not "head"

        """
    if hasattr(head_node, 'identifier') is False:
        raise NodeTypeError(type(head_node))
    if head_node.identifier != 'head':
        raise NodeIdentifierError('head', head_node.identifier)
    head_node.set_parent(self.__html.identifier)
    self.__html.remove_child('head')
    self.__html.insert_child(0, head_node)
```

*Replace the current head node by the given one.*

###### Parameters

- **head_node**: (HTMLNode)

###### Raises

- *NodeTypeError*: if head_node is not an HTMLNode
- *NodeIdentifierError*: if head_node identifier is not "head"

##### get_body_header

```python
def get_body_header(self) -> HTMLNode | None:
    """Get the body->header element node.

        :return: (HTMLNode | None) Body header node element

        """
    return self._get_body().get_child('body_header')
```

*Get the body->header element node.*

###### Returns

- (HTMLNode | None) Body header node element

##### set_body_header

```python
def set_body_header(self, body_node):
    """Replace the current body->header element node by the given one.

        :param body_node: (HTMLNode)

        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :Raises: NodeIdentifierError: if head_node identifier is not "body_header"

        """
    if hasattr(body_node, 'identifier') is False:
        raise NodeTypeError(type(body_node))
    if body_node.identifier != 'body_header':
        raise NodeIdentifierError('body_header', body_node.identifier)
    body_node.set_parent(self._get_body().identifier)
    self._get_body().remove_child('body_header')
    self._get_body().insert_child(0, body_node)
```

*Replace the current body->header element node by the given one.*

###### Parameters

- **body_node**: (HTMLNode)

###### Raises

- *NodeTypeError*: if head_node is not an HTMLNode
- *NodeIdentifierError*: if head_node identifier is not "body_header"

##### get_body_nav

```python
def get_body_nav(self):
    """Get the body->nav element node.

        :return: (HTMLNode) Body nav node element

        """
    return self._get_body().get_child('body_nav')
```

*Get the body->nav element node.*

###### Returns

- (HTMLNode) Body nav node element

##### set_body_nav

```python
def set_body_nav(self, body_node):
    """Replace the current body->nav node by the given one.

        :param body_node: (HTMLNode)

        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :raises: NodeIdentifierError: if head_node identifier is not "body_nav"

        """
    if hasattr(body_node, 'identifier') is False:
        raise NodeTypeError(type(body_node))
    if body_node.identifier != 'body_nav':
        raise NodeIdentifierError('body_nav', body_node.identifier)
    body_node.set_parent(self._get_body().identifier)
    self._get_body().remove_child('body_nav')
    self._get_body().insert_child(1, body_node)
```

*Replace the current body->nav node by the given one.*

###### Parameters

- **body_node**: (HTMLNode)

###### Raises

- *NodeTypeError*: if head_node is not an HTMLNode
- *NodeIdentifierError*: if head_node identifier is not "body_nav"

##### get_body_main

```python
def get_body_main(self):
    """Get the body->main element node.

        :return: (HTMLNode) Body main node element

        """
    return self._get_body().get_child('body_main')
```

*Get the body->main element node.*

###### Returns

- (HTMLNode) Body main node element

##### get_body_footer

```python
def get_body_footer(self):
    """Get the body->footer element node.

        :return: (HTMLNode) Body footer node element

        """
    return self._get_body().get_child('body_footer')
```

*Get the body->footer element node.*

###### Returns

- (HTMLNode) Body footer node element

##### set_body_footer

```python
def set_body_footer(self, body_node):
    """Replace the current body->footer node by the given one.

        :param body_node: (HTMLNode)
        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :Raises: NodeIdentifierError: if head_node identifier is not "body_footer"

        """
    if hasattr(body_node, 'identifier') is False:
        raise NodeTypeError(type(body_node))
    if body_node.identifier != 'body_footer':
        raise NodeIdentifierError('body_footer', body_node.identifier)
    body_node.set_parent(self._get_body().identifier)
    self._get_body().remove_child('body_footer')
    self._get_body().append_child(body_node)
```

*Replace the current body->footer node by the given one.*

###### Parameters

- **body_node**: (HTMLNode)


###### Raises

- *NodeTypeError*: if head_node is not an HTMLNode
- *NodeIdentifierError*: if head_node identifier is not "body_footer"

##### get_body_script

```python
def get_body_script(self):
    """Get the body->script element node.

        :return: (HTMLNode) Body script node element

        """
    return self._get_body().get_child('body_script')
```

*Get the body->script element node.*

###### Returns

- (HTMLNode) Body script node element

##### set_body_script

```python
def set_body_script(self, body_node):
    """Replace the current body->script node by the given one.

        :param body_node: (HTMLNode)

        :Raises: NodeTypeError: if head_node is not an HTMLNode
        :raises: NodeIdentifierError: if head_node identifier is not "body_script"

        """
    if hasattr(body_node, 'identifier') is False:
        raise NodeTypeError(type(body_node))
    if body_node.identifier != 'body_script':
        raise NodeIdentifierError('body_script', body_node.identifier)
    body_node.set_parent(self._get_body().identifier)
    self._get_body().remove_child('body_script')
    self._get_body().append_child(body_node)
```

*Replace the current body->script node by the given one.*

###### Parameters

- **body_node**: (HTMLNode)

###### Raises

- *NodeTypeError*: if head_node is not an HTMLNode
- *NodeIdentifierError*: if head_node identifier is not "body_script"

##### comment

```python
def comment(self, content):
    """Add a comment to the body->main."""
    node = HTMLComment(self.body_main.identifier, content)
    self.body_main.append_child(node)
    return node
```

*Add a comment to the body->main.*

##### element

```python
def element(self, tag: str='div', ident=None, class_name=None) -> HTMLNode:
    """Add a node to the body->main.

        :param tag: (str) HTML element name
        :param ident: (str) Identifier of the element
        :param class_name: (str) Value of the class attribute
        :return: (HTMLNode) The created node

        """
    att = dict()
    if ident is not None:
        att['id'] = str(ident)
    if class_name is not None:
        att['class'] = str(class_name)
    node = HTMLNode(self.body_main.identifier, ident, tag, attributes=att)
    self.body_main.append_child(node)
    return node
```

*Add a node to the body->main.*

###### Parameters

- **tag**: (*str*) HTML element name
- **ident**: (*str*) Identifier of the element
- **class_name**: (*str*) Value of the class attribute


###### Returns

- (HTMLNode) The created node

##### button

```python
def button(self, value: str, on_clik: str, identifier: str=None, class_name: str=None) -> HTMLNode:
    """Add a classic button with given text value and onclick event to the body->main.

        :param value: (str) The text write in the button
        :param on_clik: (str) the onclick event of the button (generally call a js function)
        :param identifier: (str) Optional, the identifier of the node (and also the id of the tag in the html generated)
        :param class_name: (str) Optional, the classes attribute for css of the button tag

        :return: (HTMLNode) The button node created

        """
    attributes = {'onclik': on_clik}
    if identifier is not None:
        attributes['id'] = identifier
    if class_name is not None:
        attributes['class'] = class_name
    button = HTMLNode(self.body_main.identifier, identifier, 'button', value=value, attributes=attributes)
    self.body_main.append_child(button)
    return button
```

*Add a classic button with given text value and onclick event to the body->main.*

###### Parameters

- **value**: (*str*) The text write in the button
- **on_clik**: (*str*) the onclick event of the button (generally call a js function)
- **identifier**: (*str*) Optional, the identifier of the node (and also the id of the tag in the html generated)
- **class_name**: (*str*) Optional, the classes attribute for css of the button tag

###### Returns

- (HTMLNode) The button node created

##### image

```python
def image(self, src: str, alt_text: str, identifier: str=None, class_name: str=None) -> HTMLNode:
    """Add an image to the body->main.

        :param src: (str) The path of the image file
        :param alt_text: (str) the alternative text if for some reason the image doesn't display or for narrator
        :param identifier: (str) Optional, the identifier of the node (and also the id of the tag in the html generated)
        :param class_name: (str) Optional, the classes attribute for css of the button tag

        :return: (HTMLNode) The image node created

        """
    attributes = {'src': src, 'alt': alt_text}
    if identifier is not None:
        attributes['id'] = identifier
    if class_name is not None:
        attributes['class'] = class_name
    img = HTMLNode(self.body_main.identifier, identifier, 'img', attributes=attributes)
    self.body_main.append_child(img)
    return img
```

*Add an image to the body->main.*

###### Parameters

- **src**: (*str*) The path of the image file
- **alt_text**: (*str*) the alternative text if for some reason the image doesn't display or for narrator
- **identifier**: (*str*) Optional, the identifier of the node (and also the id of the tag in the html generated)
- **class_name**: (*str*) Optional, the classes attribute for css of the button tag

###### Returns

- (HTMLNode) The image node created

##### serialize_element

```python
@staticmethod
def serialize_element(node: HTMLNode, nbs: int=4) -> str:
    """Serialize an element node only if not empty.

        :param node: (HTMLNode) Any element node
        :param nbs: (int) Number of space for indentation
        :raises: NodeTypeError: If the given parameter is not an HTMLNode
        :return: (str) Serialized node only if it has children or a value.

        """
    if node is None:
        return ''
    if hasattr(node, 'identifier') is False:
        raise NodeTypeError(type(node))
    if node.children_size() > 0 or node.get_value() is not None:
        return node.serialize(nbs)
    return ''
```

*Serialize an element node only if not empty.*

###### Parameters

- **node**: (HTMLNode) Any element node
- **nbs**: (*int*) Number of space for indentation


###### Raises

- *NodeTypeError*: If the given parameter is not an HTMLNode


###### Returns

- (*str*) Serialized node only if it has children or a value.

##### serialize

```python
def serialize(self, nbs: int=4) -> str:
    """Override. Serialize the tree into HTML.

        :param nbs: (int) Number of spaces for the indentation
        :return: (str)

        """
    s = self.__doctype.serialize()
    s += '<html'
    for akey in self.__html.get_attribute_keys():
        avalue = self.__html.get_attribute_value(akey)
        s += ' ' + akey
        if avalue is not None:
            s += '="' + avalue + '"'
    s += '>\n'
    s += self.__html.get_child('head').serialize(nbs)
    s += '<body'
    for akey in self._get_body().get_attribute_keys():
        avalue = self._get_body().get_attribute_value(akey)
        s += ' ' + akey
        if avalue is not None:
            s += '="' + avalue + '"'
    s += '>\n'
    if self.get_body_header() is not None:
        s += self.serialize_element(self.get_body_header(), nbs)
    if self.get_body_nav() is not None:
        s += self.serialize_element(self.get_body_nav(), nbs)
    if self.get_body_main() is not None:
        s += self.get_body_main().serialize(nbs)
    if self.get_body_footer() is not None:
        s += self.serialize_element(self.get_body_footer(), nbs)
    if self.get_body_script() is not None:
        s += self.serialize_element(self.get_body_script(), nbs)
    s += '\n</body>\n</html>\n'
    return s
```

*Override. Serialize the tree into HTML.*

###### Parameters

- **nbs**: (*int*) Number of spaces for the indentation


###### Returns

- (*str*)

##### serialize_to_file

```python
def serialize_to_file(self, filename: str, nbs: int=4) -> str:
    """Serialize the tree into an HTML file.

        The HTML content is saved into the file and its URL is returned.

        :param filename: (str) A filename to save the serialized HTML string.
        :param nbs: (int) Number of spaces for the indentation
        :returns: (str) file URL

        """
    with open(filename, 'w') as fp:
        fp.write(self.serialize(nbs))
    return 'file://' + os.path.abspath(filename)
```

*Serialize the tree into an HTML file.*

The HTML content is saved into the file and its URL is returned.

###### Parameters

- **filename**: (*str*) A filename to save the serialized HTML string.
- **nbs**: (*int*) Number of spaces for the indentation


###### Returns

- (*str*) file URL



#### Private functions

##### _get_body

```python
def _get_body(self) -> HTMLNode:
    """Get the body element node.

        :return: (HTMLNode) The body element node

        """
    return self.__html.get_child('body')
```

*Get the body element node.*

###### Returns

- (HTMLNode) The body element node



#### Overloads

##### __contains__

```python
def __contains__(self, identifier):
    raise NotImplementedError
```



##### __str__

```python
def __str__(self):
    return 'HTMLTree ({:s})'.format(self.identifier)
```





### Class `HTMLTreeError`

#### Constructor

##### __init__

```python
def __init__(self, status, msg_error: str=None):
    """Create an HTML Tree for status error response.

    :param status: (HTTPDStatus) The status of the response. (DO NOT typing it for circular import problem)
    :param msg_error: (str) Optional parameter, error message to display in the page for more information

    """
    text = f'{status.code} : {status.HTTPD_STATUS[status.code]}'
    super(HTMLTreeError, self).__init__(f'tree_{status.code}')
    self.head.title(text)
    h1 = self.element('h1')
    h1.set_value(text)
    if msg_error is not None:
        html_error = self.element('p')
        html_error.set_value(msg_error)
```

*Create an HTML Tree for status error response.*

###### Parameters

- **status**: (HTTPDStatus) The status of the response. (DO NOT typing it for circular import problem)
- **msg_error**: (*str*) Optional parameter, error message to display in the page for more information





~ Created using [Clamming](https://clamming.sf.net) version 1.7 ~
