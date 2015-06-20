# repath
[![Build Status](https://travis-ci.org/nickcoutsos/python-repath.svg)](https://travis-ci.org/nickcoutsos/python-repath)
[![Coverage Status](https://coveralls.io/repos/nickcoutsos/python-repath/badge.svg?branch=master)](https://coveralls.io/r/nickcoutsos/python-repath?branch=master)
[![PyPI version](https://badge.fury.io/py/repath.svg)](http://badge.fury.io/py/repath)

*Now on pypi*

A port of the node module `path-to-regexp` to Python.

> Turn an Express-style path string such as `/user/:name` into a
> regular expression*.

*(it is actually used to generate patterns which you can then compile using the
`re` module, including appropriate regex flag(s))*

## Installation

*repath* is a single module, so installation can be as simple as copying the
`repath.py` file to your project directory, but traditional methods are also
available:

* Clone this repo, and from the working directory run:
    * `python setup.py install`, or
    * `pip install ./`
* Or fetch from pypi with:
    * `pip install repath`


## Usage

```python
import re
import repath

pattern = repath.pattern(path)
match = re.match(pattern, requested_url_path)

if match:
    params = match.groupdict()
```

- **path** A string in the express format, an array of strings, or a regular expression.
- **kwargs**
    - **strict** When `False` the trailing slash is optional. (default: `False`)
    - **end** Attempt to match full paths (default: `True`)
        - `/foo/bar` with `end=False` will match `/foo/bar` or `/foo/bar/baz`
        - `/foo/bar` with `end=True` will only match `/foo/bar`

```python
>>> pattern('/foo/:bar')
'^/foo/(?<bar>[^/]+?)/?$'
```

**Shortcut:**

```python
>>> from repath import match
>>> match('/things/:thing', /things/1234').groupdict()
{'thing': '1234'}
```

### Parameters

The path has the ability to define parameters and automatically generate capture
groups in the resulting regular expression pattern.

#### Named Parameters

Named parameters are defined by prefixing the parameter name with a colon (e.g.
`:foo`). By default, this parameter will match up to the next path segment.

```python
>>> regex = re.compile(pattern('/:foo/:bar'), re.I)
>>> match = regex.match('/test/route')
>>> match.groups()
('test', 'route',)
>>> match.groupdict()
{'foo': 'test', 'bar': 'route'}
```

#### Suffixed Parameters

##### Optional

Parameters can be suffixed with a question mark (`?`) to make the entire
parameter optional. This will also make any prefixed path delimiter optional
(`/` or `.`).

```python
>>> regex = re.compile(pattern('/:foo/:bar?'))
>>> regex.match('/test').groupdict()
{'foo': 'test', 'bar': None}

>>> regex.match('/test/route').groupdict()
{'foo': 'test', 'bar': 'route'}
```

##### Zero or more

Parameters can be suffixed with an asterisk (`*`) to denote a zero or more
parameter match. The prefixed path delimiter is also taken into account for the
match.

```python
>>> regexp = re.compile(pattern('/:foo*'))
>>> regexp.match('/').groupdict()
{'foo': None}

>>> regexp.match('/bar/baz')
{'foo': 'bar/baz'}
```

##### One or more

Parameters can be suffixed with a plus sign (`+`) to denote a one or more
parameters match. The prefixed path delimiter is included in the match.

```python
>>> regexp = re.compile(pattern('/:foo+'))
>>> regexp.match('/')
None

>>> regexp.match('/bar/baz').groupdict()
{'foo': 'bar/baz'}
```

#### Custom Match Parameters

All parameters can be provided a custom matching regexp and override the
default. Please note: Backslashes need to be escaped in strings.

```python
>>> regexp = re.compile(pattern('/:foo(\\d+)'))
>>> regexp.match('/123').groupdict()
{'foo': '123'}

>>> regexp.match('/abc')
None
```

#### Unnamed Parameters

It is possible to write an unnamed parameter that is only a matching group. It
works the same as a named parameter, except it must be retrieved by its group
number.

```python
>>> regexp = re.compile(pattern('/:foo/(.*)'))
>>> regexp.match('/test/route').groupdict()
{'foo': 'test'}
>>> regexp.match('/test/route').groups()
('test', 'route',)
```

#### Asterisk

An asterisk can be used for matching everything. It is equivalent to an unnamed
matching group of `(.*)`.

```python
>>> regexp = re.compile(pattern('/fooo/*'))
>>> regexp.match('/foo/bar/baz').groups()
('bar/baz',)
```

### Parse

The parse function is exposed via `repath.parse`. This will yield an array of
strings and dictionary tokens.

```python
>>> tokens = repath.parse('/route/:foo/(.*)')
>>> tokens[0]
'/route'
>>> tokens[1]
{'name': 'foo', 'prefix': '/', 'delimiter': '/', 'optional': False, 'repeat': False, 'pattern': '[^/]+?'}
>>> tokens[2]
{'name': '0', 'prefix': '/', 'delimiter': '/', 'optional': False, 'repeat': False, 'pattern': '.*'}
```

**Note:** This method only works with strings.

### Compile ("Reverse" Path-To-RegExp)

*repath* exposes a template function for transforming an express path into a
valid path. Confusing enough? This example will straighten everything out for
you.

```python
>>> template = repath.template('/user/:id')
>>> template({'id': 123})
'/user/123'
```

**Note:** The generated function will throw on any invalid input. It will
execute all necessary checks to ensure the generated path is valid. This method
only works with strings.

### Working with Tokens

*repath* exposes the two functions used internally to generate output based on
the parsed array of tokens.

* `repath.tokens_to_pattern(tokens, strict=False, end=True)` Transform an array
of tokens into a matching regular expression pattern.
* `repath.tokens_to_function(tokens)` Transform an array of tokens into a path
templating function.
