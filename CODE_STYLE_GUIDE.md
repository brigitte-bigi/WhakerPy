# Code style guide

## General rules

### Base coding rules

The base rules are in PEP8 Style Guide: <https://peps.python.org/pep-0008/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.

### Commit message

A correct commit message must therefore be structured as:
`name.of.module: Action message`
where Action includes but is not limited to "added", "fixed", "cleaned", "removed".
Example: sppas.src.annotations.Cuedpseech.whenhend: Added test for the model 4 -- custom rules.

### Naming

- General class names are in Pascal Case. Example: `class WorkerOnSomething:`.
- SPPAS integrated class names are in CamelCase. Example: `class sppasWorkerOnSomething:`
- Function names are Snake Cases: all words lowercase separated by underscores. Example `def work_hard():`
- Variable names and objects are Snake Cases: all words lowercase separated by underscores,
   and must express their use more than their type. Example `work_hard = True`. Exceptions: 
   local iterators variables like i, j, k.
- Constants are Upper Case with Underscores. Example: `MSG_HELLO = _("Hello")`.
- Files that define a class should have the same name as the class but in Snake Case;
   and it should contain only one class. Example: `worker_on_something.py`. Abbreviations are 
   allowed. Example: `worker_on_sth.py`.

### Formatting

- Special characters like page break must be avoided.
- Indentation must use 4 spaces everywhere.

### Commenting

Comments are in American English. 
Consider a comment to be like a sentence: it starts with an uppercase,
it contains a verb, and it explains something that is not obvious when reading the lines
of code. The sentences should be in the passive voice, so they do not use 'you' or 'we'.

There can never be too many comments in a program! However, tricky code should not be 
commented on but rewritten! In general, the use of comments should be minimized through
appropriate naming choices and an explicit logical structure.

### Documentation Strings

The base rules are in PEP257 Style Guide: <https://peps.python.org/pep-0257/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.

### Type Hints

The base rules are in PEP484 Style Guide: <https://peps.python.org/pep-0484/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.


## SPPAS specific rules

### Coding rules

- Limit all lines to a maximum of 119 characters.
- Do not use in-line comments.
- For type hints, do not use 'typing' library.
- Do not use property decorator. Use "property" function instead.

- Always explicit what is compared to what. Do not use 'not'. Examples:
```python
>>> # Correct -- also because it makes everything clear:
>>> # if boolean
>>> if greeting is False:
>>>     pass
>>> # if int
>>> if greeting == 0:
>>>     pass
>>> # if string
>>> if greeting == '0':
>>>     pass
>>> # if None
>>> if greeting is None:
>>>     pass
>>> # if list, tuple or dict
>>> if len(greeting) == 0:
>>>    pass

>>> # Wrong because it's too confusing and can induce an error:
>>> if greeting: 
>>>    pass
>>> if not greeting:
>>>    pass
```

### Documentation Strings

- The short summary is limited to 79 characters. It starts with an uppercase and ends with a dot.
- Markdown syntax can be used but is limited to `markdown2` support.
- An extra blank-line must be added before closing.
- See ClammingPy for additional details and examples: <https://clamming.sourceforge.io/>.
- Example:

```python
>>>def add(a: int, b: int) -> int:
>>>"""Estimate the sum of two integers.

   It checks the types of given parameters and return their sum if both are integers.
   
   :example:
   >>> add(3, 4)
   7
   >>> add(3, -4)
   -1
   >>> add('3', 4)
   TypeError("First parameter is not an int")
   
   :param a: (int) First value to be added
   :param b: (int) Second value to be added
   :raises: TypeError: First parameter is not an int
   :raises: TypeError: Second parameter is not an int
   :return: (int) The sum of the given parameters

   """
```
