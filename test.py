import re
import unittest

import nose.tools

import repath

class RePathTestCase(unittest.TestCase):
    pattern = None
    regex = None
    template = None
    tokens = None

    def path(self, path, options=None):
        flags = 0 if options.get('sensitive') else re.I
        self.pattern = repath.path_to_pattern(path, options)
        self.regex = re.compile(self.pattern, flags)
        self.template = repath.compile(path)

        if isinstance(path, basestring):
            self.tokens = repath.parse(path)

    def assert_parsed(self, tokens):
        self.assertEqual(self.tokens, tokens)

    def assert_will_match(self, string, matched):
        if self.regex is None:
            raise Exception('Call ParameterizedTest.path before assert_will_match')

        match = self.regex.match(string)
        if matched is None:
            self.assertIsNone(match)
        else:
            self.assertEqual(match.group(0), matched)

    def assert_will_capture(self, string, *groups, **named_groups):
        match = self.regex.match(string)

        self.assertIsNotNone(match)
        self.assertEqual(match.groups(), groups)
        self.assertEqual(match.groupdict(), named_groups)

    def assert_will_template(self, result, **fields):
        if self.template is None:
            raise Exception('Call ParameterizedTest.path before assert_will_template')

        if result is None:
            with self.assertRaises(Exception):
                self.template(fields)
        else:
            self.assertEqual(self.template(fields), result)


TEST_CASES = [
    # Simple paths.
    [
        '/',
        None,
        [
            '/'
        ],
        [
            ['/', ['/']],
            ['/route', None]
        ],
        [
            [None, '/'],
            [{}, '/'],
            [{ 'id': 123 }, '/']
        ]
    ],
    [
        '/test',
        None,
        [
            '/test'
        ],
        [
            ['/test', ['/test']],
            ['/route', None],
            ['/test/route', None],
            ['/test/', ['/test/']]
        ],
        [
            [None, '/test'],
            [{}, '/test']
        ]
    ],
    [
        '/test/',
        None,
        [
            '/test/'
        ],
        [
            ['/test', ['/test']],
            ['/test/', ['/test/']],
            ['/test//', None]
        ],
        [
            [None, '/test/']
        ]
    ],

    # Case-sensitive paths.
    
    [
        '/test',
        {
            'sensitive': True
        },
        [
            '/test'
        ],
        [
            ['/test', ['/test']],
            ['/TEST', None]
        ],
        [
            [None, '/test']
        ]
    ],
    [
        '/TEST',
        {
            'sensitive': True
        },
        [
            '/TEST'
        ],
        [
            ['/test', None],
            ['/TEST', ['/TEST']]
        ],
        [
            [None, '/TEST']
        ]
    ],

    # Strict mode.
    
    [
        '/test',
        {
            'strict': True
        },
        [
            '/test'
        ],
        [
            ['/test', ['/test']],
            ['/test/', None],
            ['/TEST', ['/TEST']]
        ],
        [
            [None, '/test']
        ]
    ],
    [
        '/test/',
        {
            'strict': True
        },
        [
            '/test/'
        ],
        [
            ['/test', None],
            ['/test/', ['/test/']],
            ['/test//', None]
        ],
        [
            [None, '/test/']
        ]
    ],

    # Non-ending mode.
    
    [
        '/test',
        {
            'end': False
        },
        [
            '/test'
        ],
        [
            ['/test', ['/test']],
            ['/test/', ['/test/']],
            ['/test/route', ['/test']],
            ['/route', None]
        ],
        [
            [None, '/test']
        ]
    ],
    [
        '/test/',
        {
            'end': False
        },
        [
            '/test/'
        ],
        [
            ['/test/route', ['/test']],
            ['/test//', ['/test']],
            ['/test//route', ['/test']]
        ],
        [
            [None, '/test/']
        ]
    ],
    [
        '/:test',
        {
            'end': False
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/route', ['/route', 'route'], {'test': 'route'}]
        ],
        [
            [{}, None],
            [{ 'test': 'abc' }, '/abc']
        ]
    ],
    [
        '/:test/',
        {
            'end': False
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            '/'
        ],
        [
            ['/route', ['/route', 'route'], {'test': 'route'}]
        ],
        [
            [{ 'test': 'abc' }, '/abc/']
        ]
    ],

    # Combine modes.
    
    [
        '/test',
        {
            'end': False,
            'strict': True
        },
        [
            '/test'
        ],
        [
            ['/test', ['/test']],
            ['/test/', ['/test']],
            ['/test/route', ['/test']]
        ],
        [
            [None, '/test']
        ]
    ],
    [
        '/test/',
        {
            'end': False,
            'strict': True
        },
        [
            '/test/'
        ],
        [
            ['/test', None],
            ['/test/', ['/test/']],
            ['/test//', ['/test/']],
            ['/test/route', ['/test/']]
        ],
        [
            [None, '/test/']
        ]
    ],
    [
        '/test.json',
        {
            'end': False,
            'strict': True
        },
        [
            '/test.json'
        ],
        [
            ['/test.json', ['/test.json']],
            ['/test.json.hbs', None],
            ['/test.json/route', ['/test.json']]
        ],
        [
            [None, '/test.json']
        ]
    ],
    [
        '/:test',
        {
            'end': False,
            'strict': True
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/route', ['/route', 'route'], {'test': 'route'}],
            ['/route/', ['/route', 'route'], {'test': 'route'}]
        ],
        [
            [{}, None],
            [{ 'test': 'abc' }, '/abc']
        ]
    ],
    [
        '/:test/',
        {
            'end': False,
            'strict': True
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            '/'
        ],
        [
            ['/route', None],
            ['/route/', ['/route/', 'route'], {'test': 'route'}]
        ],
        [
            [{ 'test': 'foobar' }, '/foobar/']
        ]
    ],

    # Arrays of simple paths.
    
    [
        ['/one', '/two'],
        None,
        [],
        [
            ['/one', ['/one']],
            ['/two', ['/two']],
            ['/three', None],
            ['/one/two', None]
        ]
    ],

    # Non-ending simple path.
    
    [
        '/test',
        {
            'end': False
        },
        [
            '/test'
        ],
        [
            ['/test/route', ['/test']]
        ],
        [
            [None, '/test']
        ]
    ],

    # Single named parameter.
    [
        '/:test',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/route', ['/route', 'route'], {'test': 'route'}],
            ['/another', ['/another', 'another'], {'test': 'another'}],
            ['/something/else', None],
            ['/route.json', ['/route.json', 'route.json'], {'test': 'route.json'}]
        ],
        [
            [{ 'test': 'route' }, '/route']
        ]
    ],
    [
        '/:test',
        {
            'strict': True
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/route', ['/route', 'route'], {'test': 'route'}],
            ['/route/', None]
        ],
        [
            [{ 'test': 'route' }, '/route']
        ]
    ],
    [
        '/:test/',
        {
            'strict': True
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            '/'
        ],
        [
            ['/route/', ['/route/', 'route'], {'test': 'route'}],
            ['/route//', None]
        ],
        [
            [{ 'test': 'route' }, '/route/']
        ]
    ],
    [
        '/:test',
        {
            'end': False
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/route.json', ['/route.json', 'route.json'], {'test': 'route.json'}],
            ['/route//', ['/route', 'route'], {'test': 'route'}]
        ],
        [
            [{ 'test': 'route' }, '/route']
        ]
    ],

    # Optional named parameter.
    
    [
        '/:test?',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': True,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/route', ['/route', 'route'], {'test': 'route'}],
            ['/route/nested', None],
            ['/', ['/', None], {'test': None}],
            ['//', None]
        ],
        [
            [None, ''],
            [{ 'test': 'foobar' }, '/foobar']
        ]
    ],
    [
        '/:test?',
        {
            'strict': True
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': True,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/route', ['/route', 'route'], {'test': 'route'}],
            ['/', None], # Questionable behaviour.
            ['//', None]
        ],
        [
            [None, ''],
            [{ 'test': 'foobar' }, '/foobar']
        ]
    ],
    [
        '/:test?/',
        {
            'strict': True
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': True,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            '/'
        ],
        [
            ['/route', None],
            ['/route/', ['/route/', 'route'], {'test': 'route'}],
            ['/', ['/', None]],
            ['//', None]
        ],
        [
            [None, '/'],
            [{ 'test': 'foobar' }, '/foobar/']
        ]
    ],

    # Repeated one or more times parameters.
    [
        '/:test+',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': True,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/', None],
            ['/route', ['/route', 'route'], {'test': 'route'}],
            ['/some/basic/route', ['/some/basic/route', 'some/basic/route'], {'test': 'some/basic/route'}],
            ['//', None]
        ],
        [
            [{}, None],
            [{ 'test': 'foobar' }, '/foobar'],
            [{ 'test': ['a', 'b', 'c'] }, '/a/b/c']
        ]
    ],
    [
        '/:test(\\d+)+',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': True,
                'pattern': '\\d+'
            }
        ],
        [
            ['/abc/456/789', None],
            ['/123/456/789', ['/123/456/789', '123/456/789'], {'test': '123/456/789'}]
        ],
        [
            [{ 'test': 'abc' }, None],
            [{ 'test': 123 }, '/123'],
            [{ 'test': [1, 2, 3] }, '/1/2/3']
        ]
    ],
    [
        '/route.:ext(json|xml)+',
        None,
        [
            '/route',
            {
                'name': 'ext',
                'prefix': '.',
                'delimiter': '.',
                'optional': False,
                'repeat': True,
                'pattern': 'json|xml'
            }
        ],
        [
            ['/route', None],
            ['/route.json', ['/route.json', 'json'], {'ext': 'json'}],
            ['/route.xml.json', ['/route.xml.json', 'xml.json'], {'ext': 'xml.json'}],
            ['/route.html', None]
        ],
        [
            [{ 'ext': 'foobar' }, None],
            [{ 'ext': 'xml' }, '/route.xml'],
            [{ 'ext': ['xml', 'json'] }, '/route.xml.json']
        ]
    ],

    # Repeated zero or more times parameters.
    
    [
        '/:test*',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': True,
                'repeat': True,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/', ['/', None], {'test': None}],
            ['//', None],
            ['/route', ['/route', 'route'], {'test': 'route'}],
            ['/some/basic/route', ['/some/basic/route', 'some/basic/route'], {'test': 'some/basic/route'}]
        ],
        [
            [{}, ''],
            [{ 'test': 'foobar' }, '/foobar'],
            [{ 'test': ['foo', 'bar'] }, '/foo/bar']
        ]
    ],
    [
        '/route.:ext([a-z]+)*',
        None,
        [
            '/route',
            {
                'name': 'ext',
                'prefix': '.',
                'delimiter': '.',
                'optional': True,
                'repeat': True,
                'pattern': '[a-z]+'
            }
        ],
        [
            ['/route', ['/route', None]],
            ['/route.json', ['/route.json', 'json'], {'ext': 'json'}],
            ['/route.json.xml', ['/route.json.xml', 'json.xml'], {'ext': 'json.xml'}],
            ['/route.123', None]
        ],
        [
            [{}, '/route'],
            [{ 'ext': [] }, '/route'],
            [{ 'ext': '123' }, None],
            [{ 'ext': 'foobar' }, '/route.foobar'],
            [{ 'ext': ['foo', 'bar'] }, '/route.foo.bar']
        ]
    ],

    # Custom named parameters.
    
    [
        '/:test(\\d+)',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '\\d+'
            }
        ],
        [
            ['/123', ['/123', '123'], {'test': '123'}],
            ['/abc', None],
            ['/123/abc', None]
        ],
        [
            [{ 'test': 'abc' }, None],
            [{ 'test': '123' }, '/123']
        ]
    ],
    [
        '/:test(\\d+)',
        {
            'end': False
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '\\d+'
            }
        ],
        [
            ['/123', ['/123', '123'], {'test': '123'}],
            ['/abc', None],
            ['/123/abc', ['/123', '123'], {'test': '123'}]
        ],
        [
            [{ 'test': '123' }, '/123']
        ]
    ],
    [
        '/:test(.*)',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '.*'
            }
        ],
        [
            ['/anything/goes/here', ['/anything/goes/here', 'anything/goes/here'], {'test': 'anything/goes/here'}]
        ],
        [
            [{ 'test': '' }, '/'],
            [{ 'test': 'abc' }, '/abc'],
            [{ 'test': 'abc/123' }, '/abc%2F123']
        ]
    ],
    [
        '/:route([a-z]+)',
        None,
        [
            {
                'name': 'route',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[a-z]+'
            }
        ],
        [
            ['/abcde', ['/abcde', 'abcde'], {'route': 'abcde'}],
            ['/12345', None]
        ],
        [
            [{ 'route': '' }, None],
            [{ 'route': '123' }, None],
            [{ 'route': 'abc' }, '/abc']
        ]
    ],
    [
        '/:route(this|that)',
        None,
        [
            {
                'name': 'route',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': 'this|that'
            }
        ],
        [
            ['/this', ['/this', 'this'], {'route': 'this'}],
            ['/that', ['/that', 'that'], {'route': 'that'}],
            ['/foo', None]
        ],
        [
            [{ 'route': 'this' }, '/this'],
            [{ 'route': 'foo' }, None],
            [{ 'route': 'that' }, '/that']
        ]
    ],

    # Prefixed slashes could be omitted.
    
    [
        'test',
        None,
        [
            'test'
        ],
        [
            ['test', ['test']],
            ['/test', None]
        ],
        [
            [None, 'test']
        ]
    ],
    [
        ':test',
        None,
        [
            {
                'name': 'test',
                'prefix': '',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['route', ['route', 'route']],
            ['/route', None],
            ['route/', ['route/', 'route']]
        ],
        [
            [{ 'test': '' }, None],
            [{}, None],
            [{ 'test': None }, None],
            [{ 'test': 'route' }, 'route']
        ]
    ],
    [
        ':test',
        {
            'strict': True
        },
        [
            {
                'name': 'test',
                'prefix': '',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['route', ['route', 'route'], {'test': 'route'}],
            ['/route', None],
            ['route/', None]
        ],
        [
            [{ 'test': 'route' }, 'route']
        ]
    ],
    [
        ':test',
        {
            'end': False
        },
        [
            {
                'name': 'test',
                'prefix': '',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['route', ['route', 'route'], {'test': 'route'}],
            ['/route', None],
            ['route/', ['route/', 'route'], {'test': 'route'}],
            ['route/foobar', ['route', 'route'], {'test': 'route'}]
        ],
        [
            [{ 'test': 'route' }, 'route']
        ]
    ],
    [
        ':test?',
        None,
        [
            {
                'name': 'test',
                'prefix': '',
                'delimiter': '/',
                'optional': True,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['route', ['route', 'route'], {'test': 'route'}],
            ['/route', None],
            ['', ['', None]],
            ['route/foobar', None]
        ],
        [
            [{}, ''],
            [{ 'test': '' }, None],
            [{ 'test': 'route' }, 'route']
        ]
    ],

    # Formats.
    
    [
        '/test.json',
        None,
        [
            '/test.json'
        ],
        [
            ['/test.json', ['/test.json']],
            ['/route.json', None]
        ],
        [
            [{}, '/test.json']
        ]
    ],
    [
        '/:test.json',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            '.json'
        ],
        [
            ['/test.json', ['/test.json', 'test'], {'test': 'test'}],
            ['/route.json', ['/route.json', 'route'], {'test': 'route'}],
            ['/route.json.json', ['/route.json.json', 'route.json'], {'test': 'route.json'}]
        ],
        [
            [{ 'test': 'foo' }, '/foo.json']
        ]
    ],

    # Format params.
    
    [
        '/test.:format',
        None,
        [
            '/test',
            {
                'name': 'format',
                'prefix': '.',
                'delimiter': '.',
                'optional': False,
                'repeat': False,
                'pattern': '[^.]+?'
            }
        ],
        [
            ['/test.html', ['/test.html', 'html'], {'format': 'html'}],
            ['/test.hbs.html', None]
        ],
        [
            [{}, None],
            [{ 'format': '' }, None],
            [{ 'format': 'foo' }, '/test.foo']
        ]
    ],
    # [
    #     '/test.:format.:format',
    #     None,
    #     [
    #         '/test',
    #         {
    #             'name': 'format',
    #             'prefix': '.',
    #             'delimiter': '.',
    #             'optional': False,
    #             'repeat': False,
    #             'pattern': '[^.]+?'
    #         },
    #         {
    #             'name': 'format',
    #             'prefix': '.',
    #             'delimiter': '.',
    #             'optional': False,
    #             'repeat': False,
    #             'pattern': '[^.]+?'
    #         }
    #     ],
    #     [
    #         ['/test.html', None],
    #         ['/test.hbs.html', ['/test.hbs.html', 'hbs', 'html']]
    #     ],
    #     [
    #         [{ 'format': 'foo.bar' }, None],
    #         [{ 'format': 'foo' }, '/test.foo.foo']
    #     ]
    # ],
    [
        '/test.:format+',
        None,
        [
            '/test',
            {
                'name': 'format',
                'prefix': '.',
                'delimiter': '.',
                'optional': False,
                'repeat': True,
                'pattern': '[^.]+?'
            }
        ],
        [
            ['/test.html', ['/test.html', 'html'], {'format': 'html'}],
            ['/test.hbs.html', ['/test.hbs.html', 'hbs.html'], {'format': 'hbs.html'}]
        ],
        [
            [{ 'format': [] }, None],
            [{ 'format': 'foo' }, '/test.foo'],
            [{ 'format': ['foo', 'bar'] }, '/test.foo.bar']
        ]
    ],
    [
        '/test.:format',
        {
            'end': False
        },
        [
            '/test',
            {
                'name': 'format',
                'prefix': '.',
                'delimiter': '.',
                'optional': False,
                'repeat': False,
                'pattern': '[^.]+?'
            }
        ],
        [
            ['/test.html', ['/test.html', 'html'], {'format': 'html'}],
            ['/test.hbs.html', None]
        ],
        [
            [{ 'format': 'foo' }, '/test.foo']
        ]
    ],
    [
        '/test.:format.',
        None,
        [
            '/test',
            {
                'name': 'format',
                'prefix': '.',
                'delimiter': '.',
                'optional': False,
                'repeat': False,
                'pattern': '[^.]+?'
            },
            '.'
        ],
        [
            ['/test.html.', ['/test.html.', 'html'], {'format': 'html'}],
            ['/test.hbs.html', None]
        ],
        [
            [{ 'format': '' }, None],
            [{ 'format': 'foo' }, '/test.foo.']
        ]
    ],

    # Format and path params.
    
    [
        '/:test.:format',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            {
                'name': 'format',
                'prefix': '.',
                'delimiter': '.',
                'optional': False,
                'repeat': False,
                'pattern': '[^.]+?'
            }
        ],
        [
            ['/route.html', ['/route.html', 'route', 'html'], {'test': 'route', 'format': 'html'}],
            ['/route', None],
            ['/route.html.json', ['/route.html.json', 'route.html', 'json'], {'test': 'route.html', 'format': 'json'}]
        ],
        [
            [{}, None],
            [{ 'test': 'route', 'format': 'foo' }, '/route.foo']
        ]
    ],
    [
        '/:test.:format?',
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            {
                'name': 'format',
                'prefix': '.',
                'delimiter': '.',
                'optional': True,
                'repeat': False,
                'pattern': '[^.]+?'
            }
        ],
        [
            ['/route', ['/route', 'route', None]],
            ['/route.json', ['/route.json', 'route', 'json'], {'test': 'route', 'format': 'json'}],
            ['/route.json.html', ['/route.json.html', 'route.json', 'html']]
        ],
        [
            [{ 'test': 'route' }, '/route'],
            [{ 'test': 'route', 'format': '' }, None],
            [{ 'test': 'route', 'format': 'foo' }, '/route.foo']
        ]
    ],
    [
        '/:test.:format?',
        {
            'end': False
        },
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            {
                'name': 'format',
                'prefix': '.',
                'delimiter': '.',
                'optional': True,
                'repeat': False,
                'pattern': '[^.]+?'
            }
        ],
        [
            ['/route', ['/route', 'route', None], {'test': 'route', 'format': None}],
            ['/route.json', ['/route.json', 'route', 'json'], {'test': 'route', 'format': 'json'}],
            ['/route.json.html', ['/route.json.html', 'route.json', 'html'], {'test': 'route.json', 'format': 'html'}]
        ],
        [
            [{ 'test': 'route' }, '/route'],
            [{ 'test': 'route', 'format': None }, '/route'],
            [{ 'test': 'route', 'format': '' }, None],
            [{ 'test': 'route', 'format': 'foo' }, '/route.foo']
        ]
    ],
    [
        '/test.:format(.*)z',
        {
            'end': False
        },
        [
            '/test',
            {
                'name': 'format',
                'prefix': '.',
                'delimiter': '.',
                'optional': False,
                'repeat': False,
                'pattern': '.*'
            },
            'z'
        ],
        [
            ['/test.abc', None],
            ['/test.z', ['/test.z', ''], {'format': ''}],
            ['/test.abcz', ['/test.abcz', 'abc'], {'format': 'abc'}]
        ],
        [
            [{}, None],
            [{ 'format': '' }, '/test.z'],
            [{ 'format': 'foo' }, '/test.fooz']
        ]
    ],

    # Unnamed params.
    
    [
        '/(\\d+)',
        None,
        [
            {
                'name': '0',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '\\d+'
            }
        ],
        [
            ['/123', ['/123', '123']],
            ['/abc', None],
            ['/123/abc', None]
        ],
        [
            [{}, None],
            [{ '0': '123' }, '/123']
        ]
    ],
    [
        '/(\\d+)',
        {
            'end': False
        },
        [
            {
                'name': '0',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '\\d+'
            }
        ],
        [
            ['/123', ['/123', '123']],
            ['/abc', None],
            ['/123/abc', ['/123', '123']],
            ['/123/', ['/123/', '123']]
        ],
        [
            [{ '0': '123' }, '/123']
        ]
    ],
    [
        '/(\\d+)?',
        None,
        [
            {
                'name': '0',
                'prefix': '/',
                'delimiter': '/',
                'optional': True,
                'repeat': False,
                'pattern': '\\d+'
            }
        ],
        [
            ['/', ['/', None]],
            ['/123', ['/123', '123']]
        ],
        [
            [{}, ''],
            [{ '0': '123' }, '/123']
        ]
    ],
    [
        '/(.*)',
        None,
        [
            {
                'name': '0',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '.*'
            }
        ],
        [
            ['/', ['/', '']],
            ['/route', ['/route', 'route']],
            ['/route/nested', ['/route/nested', 'route/nested']]
        ],
        [
            [{ '0': '' }, '/'],
            [{ '0': '123' }, '/123']
        ]
    ],

    # Regexps.
    [
        re.compile('.*'),
        None,
        [],
        [
            ['/match/anything', ['/match/anything']]
        ]
    ],
    [
        re.compile('(.*)'),
        None,
        [
            {
                'name': '0',
                'prefix': None,
                'delimiter': None,
                'optional': False,
                'repeat': False,
                'pattern': None
            }
        ],
        [
            ['/match/anything', ['/match/anything', '/match/anything']]
        ]
    ],
    [
        re.compile('/(\\d+)'),
        None,
        [
            {
                'name': '0',
                'prefix': None,
                'delimiter': None,
                'optional': False,
                'repeat': False,
                'pattern': None
            }
        ],
        [
            ['/abc', None],
            ['/123', ['/123', '123']]
        ]
    ],

    # Mixed arrays.
    [
        ['/test', re.compile('/(\\d+)')],
        None,
        [
            {
                'name': '0',
                'prefix': None,
                'delimiter': None,
                'optional': False,
                'repeat': False,
                'pattern': None
            }
        ],
        [
            ['/test', ['/test', None]]
        ]
    ],
    [
        ['/:test(\\d+)', re.compile('(.*)')],
        None,
        [
            {
                'name': 'test',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '\\d+'
            },
            {
                'name': '0',
                'prefix': None,
                'delimiter': None,
                'optional': False,
                'repeat': False,
                'pattern': None
            }
        ],
        [
            ['/123', ['/123', '123', None], {'test': '123'}],
            ['/abc', ['/abc', None, '/abc'], {'test': None}]
        ]
    ],

    # Correct names and indexes.
    # [
    #     ['/:test', '/route/:test'],
    #     None,
    #     [
    #         {
    #             'name': 'test',
    #             'prefix': '/',
    #             'delimiter': '/',
    #             'optional': False,
    #             'repeat': False,
    #             'pattern': '[^/]+?'
    #         },
    #         {
    #             'name': 'test',
    #             'prefix': '/',
    #             'delimiter': '/',
    #             'optional': False,
    #             'repeat': False,
    #             'pattern': '[^/]+?'
    #         }
    #     ],
    #     [
    #         ['/test', ['/test', 'test', None]],
    #         ['/route/test', ['/route/test', None, 'test']]
    #     ]
    # ],
    [
        [re.compile('^/([^/]+)$'), re.compile('/route/([^/]+)$')],
        None,
        [
            {
                'name': '0',
                'prefix': None,
                'delimiter': None,
                'optional': False,
                'repeat': False,
                'pattern': None
            },
            {
                'name': '0',
                'prefix': None,
                'delimiter': None,
                'optional': False,
                'repeat': False,
                'pattern': None
            }
        ],
        [
            ['/test', ['/test', 'test', None]],
            ['/route/test', ['/route/test', None, 'test']]
        ]
    ],

    # Ignore non-matching groups in regexps.
    [
        re.compile('(?:.*)'),
        None,
        [],
        [
            ['/anything/you/want', ['/anything/you/want']]
        ]
    ],

    # Respect escaped characters.
    [
        '/\\(testing\\)',
        None,
        [
            '/(testing)'
        ],
        [
            ['/testing', None],
            ['/(testing)', ['/(testing)']]
        ],
        [
            [None, '/(testing)']
        ]
    ],
    [
        '/.+\\*?=^!:${}[]|',
        None,
        [
            '/.+*?=^!:${}[]|'
        ],
        [
            ['/.+*?=^!:${}[]|', ['/.+*?=^!:${}[]|']]
        ],
        [
            [None, '/.+*?=^!:${}[]|']
        ]
    ],

    # Asterisk functionality.
    [
        '/*',
        None,
        [
            {
                'name': '0',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '.*'
            }
        ],
        [
            ['', None],
            ['/', ['/', '']],
            ['/foo/bar', ['/foo/bar', 'foo/bar']]
        ],
        [
            [None, None],
            [{ '0': '' }, '/'],
            [{ '0': 'foobar' }, '/foobar']
        ]
    ],
    [
        '/foo/*',
        None,
        [
            '/foo',
            {
                'name': '0',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '.*'
            }
        ],
        [
            ['', None],
            ['/test', None],
            ['/foo', None],
            ['/foo/', ['/foo/', '']],
            ['/foo/bar', ['/foo/bar', 'bar']]
        ],
        [
            [{ '0': 'bar' }, '/foo/bar']
        ]
    ],
    [
        '/:foo/*',
        None,
        [
            {
                'name': 'foo',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            {
                'name': '0',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '.*'
            }
        ],
        [
            ['', None],
            ['/test', None],
            ['/foo', None],
            ['/foo/', ['/foo/', 'foo', ''], {'foo': 'foo'}],
            ['/foo/bar', ['/foo/bar', 'foo', 'bar'], {'foo': 'foo'}]
        ],
        [
            [{ 'foo': 'foo' }, None],
            [{ '0': 'bar' }, None],
            [{ 'foo': 'foo', '0': 'bar' }, '/foo/bar']
        ]
    ],

    # Random examples.
    [
        '/:foo/:bar',
        None,
        [
            {
                'name': 'foo',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            {
                'name': 'bar',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            ['/match/route', ['/match/route', 'match', 'route'], {'foo': 'match', 'bar': 'route'}]
        ],
        [
            [{ 'foo': 'a', 'bar': 'b' }, '/a/b']
        ]
    ],
    [
        '/:remote([\\w\-.]+)/:user([\\w\-]+)',
        None,
        [
            {
                'name': 'remote',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[\\w\-.]+'
            },
            {
                'name': 'user',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[\\w\-]+'
            }
        ],
        [
            ['/endpoint/user', ['/endpoint/user', 'endpoint', 'user'], {'remote': 'endpoint', 'user': 'user'}],
            ['/endpoint/user-name', ['/endpoint/user-name', 'endpoint', 'user-name'], {'remote': 'endpoint', 'user': 'user-name'}],
            ['/foo.bar/user-name', ['/foo.bar/user-name', 'foo.bar', 'user-name'], {'remote': 'foo.bar', 'user': 'user-name'}]
        ],
        [
            [{ 'remote': 'foo', 'user': 'bar' }, '/foo/bar'],
            [{ 'remote': 'foo.bar', 'user': 'uno' }, '/foo.bar/uno']
        ]
    ],
    [
        '/:foo\\?',
        None,
        [
            {
                'name': 'foo',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            },
            '?'
        ],
        [
            ['/route?', ['/route?', 'route'], {'foo': 'route'}]
        ],
        [
            [{ 'foo': 'bar' }, '/bar?']
        ]
    ],

    # Unicode characters.
    [
        '/:foo',
        None,
        [
            {
                'name': 'foo',
                'prefix': '/',
                'delimiter': '/',
                'optional': False,
                'repeat': False,
                'pattern': '[^/]+?'
            }
        ],
        [
            [u'/caf\u00e9', [u'/caf\u00e9', u'caf\u00e9'], {'foo': u'caf\u00e9'}]
        ],
        [
            [{ 'foo': u'caf\u00e9' }, '/caf%C3%A9']
        ]
    ]
]


def test_generator():
    for case in TEST_CASES:
        case.extend([[]] * (5 - len(case)))
        path, opts, tokens, match_cases, compile_cases = case
        yield check_definition, path, opts, tokens, match_cases, compile_cases


def check_definition(path, opts, tokens, match_cases, compile_cases):
    opts = opts or {}
    sensitive = opts.pop('sensitive', False)
    pattern = repath.path_to_pattern(path, **opts)
    regexp = re.compile(pattern, 0 if sensitive else re.I)

    if isinstance(path, basestring):
        nose.tools.eq_(repath.parse(path), tokens)

        compiled = repath.compile(path)
        for input_, output in compile_cases:
            if output is not None:
                nose.tools.eq_(compiled(input_), output)
            else:
                with nose.tools.assert_raises(Exception):
                    repath.compile(input_)

    pad_case = lambda m: m.extend(['', [], {}][3 - (3 - len(m)):])
    map(pad_case, match_cases)
    for string, matches, named_groups in match_cases:
        match = regexp.match(string)
        if matches is None:
            nose.tools.assert_is_none(match)
        else:
            groups = match.groupdict()
            nose.tools.assert_is_not_none(match)
            nose.tools.eq_(match.group(0), matches[0])
            nose.tools.eq_(list(match.groups()), matches[1:])
            for name, value in named_groups.iteritems():
                nose.tools.assert_equal(groups[name], value, 'Expected value %r != captured %r' % (value, groups[name]))


class Tests(unittest.TestCase):
    def setUp(self):
        self.path = '/user/:id'
        self.param = {
            'name': 'id',
            'prefix': '/',
            'delimiter': '/',
            'optional': False,
            'repeat': False,
            'pattern': '[^/]+?'
        }

    def check_regex_match(self, regexp, string, matched, *captures):
        match = regexp.match(string)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(0), matched)
        self.assertEqual(list(match.groups()), list(captures))

    def test_should_expose_method_to_compile_tokens_to_regexp(self):
        tokens = repath.parse(self.path)
        pattern = repath.tokens_to_pattern(tokens)
        regexp = re.compile(pattern)

        self.check_regex_match(regexp, '/user/123', '/user/123', '123')

    def test_should_expose_method_to_compile_tokens_to_path_function(self):
        tokens = repath.parse(self.path)
        fn = repath.tokens_to_template(tokens)

        self.assertEqual(fn({'id': 123}), '/user/123')


class CompileErrorTests(unittest.TestCase):
    def check_to_path(self, path, params, exception, message):
        to_path = repath.compile(path)
        with self.assertRaises(exception) as context:
            to_path(params)

        self.assertEqual(context.exception.message, message)

    def test_should_raise_error_when_a_required_param_is_missing(self):
        self.check_to_path(
            '/a/:b/c', {},
            KeyError, 'Expected "b" to be defined')

    def test_should_raise_error_when_param_does_not_match_pattern(self):
        self.check_to_path(
            '/:foo(\\d+)', {'foo': 'abc'},
            ValueError, 'Expected "foo" to match "\\d+"')

    def test_should_raise_error_when_expecting_a_repeated_value(self):
        self.check_to_path(
            '/:foo+', {'foo': []},
            ValueError, 'Expected "foo" to not be empty')

    def test_should_raise_error_when_not_expecting_repeated_value(self):
        self.check_to_path(
            '/:foo', {'foo': []},
            TypeError, 'Expected "foo" to not repeat')

    def test_should_raise_error_when_repeated_value_does_not_match(self):
        self.check_to_path(
            '/:foo(\\d+)+', {'foo': [1, 2, 3, 'a']},
            ValueError, 'Expected all "foo" to match "\\d+"')
