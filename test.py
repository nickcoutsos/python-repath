from __future__ import unicode_literals

import re
import unittest

import six

import repath

DEFAULT_TOKEN = {
    'prefix': '',
    'optional': False,
    'repeat': False
}

def token(t=None, **kwargs):
    if isinstance(t, six.string_types):
        return t
    t = DEFAULT_TOKEN.copy()
    t.update(kwargs)
    return t

class RePathTestCase(unittest.TestCase):
    pattern = None
    regex = None
    template = None
    tokens = None

    def path(self, path, **options):
        sensitive = options.pop('sensitive', False)
        flags = 0 if sensitive else re.I
        self.pattern = repath.pattern(path, **options)
        self.regex = re.compile(self.pattern, flags)

        if isinstance(path, six.string_types):
            self.template = repath.template(path)
            self.tokens = repath.parse(path)

    def assert_parsed(self, *tokens):
        if self.tokens is None:
            return
        self.assertEqual(self.tokens, list(tokens))

    def assert_will_match(self, string, matched):
        if self.regex is None:
            raise Exception('Call ParameterizedTest.path before assert_will_match')

        match = self.regex.match(string)
        if matched is None:
            self.assertIsNone(match)
        else:
            self.assertEqual(match.group(0), matched)

    def assert_will_group(self, string, *groups, **named_groups):
        match = self.regex.match(string)

        self.assertIsNotNone(match)
        self.assertEqual(match.groups(), groups)
        if named_groups:
            self.assertEqual(match.groupdict(), named_groups)

    def assert_will_template(self, result, **fields):
        if self.template is None:
            raise Exception('Call ParameterizedTest.path before assert_will_template')

        if result is None:
            with self.assertRaises(Exception):
                self.template(fields)
        else:
            self.assertEqual(self.template(fields), result)


# Tests based on the cases from the original path-to-regexp cases converted
# into individually defined functions using helper assertion methods.
class SimplePathTests(RePathTestCase):
    def test_empty_path(self):
        self.path('/')

        self.assert_parsed('/')
        self.assert_will_match('/', '/')
        self.assert_will_match('/route', None)
        self.assert_will_template('/')
        self.assert_will_template('/', id=123)

    def test_single_segment_no_trailing_slash(self):
        self.path('/test')

        self.assert_parsed('/test')
        self.assert_will_match('/test', '/test')
        self.assert_will_match('/route', None)
        self.assert_will_match('/test/route', None)
        self.assert_will_match('/test/', '/test/')
        self.assert_will_template('/test')

    def test_single_segment_with_trailing_slash(self):
        self.path('/test/')

        self.assert_parsed('/test/')
        self.assert_will_match('/test', '/test')
        self.assert_will_match('/test/', '/test/')
        self.assert_will_match('/test//', None)


class NonStringPathTests(RePathTestCase):
    def test_regex_pattern_matches_everything(self):
        self.path(re.compile('.*'))

        self.assert_will_match('/match/anything', '/match/anything')

    def test_regex_pattern_captures_everything(self):
        self.path(re.compile('(.*)'))

        self.assert_parsed(token(name='0', prefix=None, delimiter=None, pattern=None))
        self.assert_will_match('/match/anything', '/match/anything')
        self.assert_will_group('/match/anything', '/match/anything')

    def test_regex_pattern_matches_digits(self):
        self.path(re.compile('/(\\d+)'))

        self.assert_parsed(token(name='0', prefix=None, delimiter=None, pattern=None))
        self.assert_will_match('/abc', None)
        self.assert_will_match('/123', '/123')
        self.assert_will_group('/123', '123')

    def test_array_path_segment_or_digits(self):
        self.path(['/test', re.compile('/(\\d+)')])

        self.assert_parsed(token(name='0', prefix=None, delimiter=None, pattern=None))
        self.assert_will_match('/test', '/test')
        self.assert_will_group('/test', None)

    def test_named_capture_digit_or_nameless_capture_all(self):
        self.path(['/:test(\\d+)', re.compile('(.*)')])

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', pattern='\\d+'),
            token(name='0', prefix=None, delimiter=None, pattern=None)
        )
        self.assert_will_match('/123', '/123')
        self.assert_will_group('/123', '123', None, test='123')
        self.assert_will_match('/abc', '/abc')
        self.assert_will_group('/abc', None, '/abc', test=None)

    def generated_test_59(self):
        self.path([re.compile('^/([^/]+)$'), re.compile('/route/([^/]+)$')])

        self.assert_parsed(
            token(name='0', prefix=None, delimiter=None, pattern=None),
            token(name='0', prefix=None, delimiter=None, pattern=None)
        )
        self.assert_will_match('/test', '/test')
        self.assert_will_group('/test', 'test', None)
        self.assert_will_match('/route/test', '/route/test')
        self.assert_will_group('/route/test', None, 'test')

    def test_regex_match_all_noncapture_group(self):
        self.path(re.compile('(?:.*)'))

        self.assert_will_match('/anything/you/want', '/anything/you/want')


class OptionTests(RePathTestCase):
    def test_lowercase_segment_case_sensitive(self):
        self.path('/test', sensitive=True)

        self.assert_parsed('/test')
        self.assert_will_match('/test', '/test')
        self.assert_will_match('/TEST', None)

    def test_uppercase_segment_case_sensitive(self):
        self.path('/TEST', sensitive=True)

        self.assert_parsed('/TEST')
        self.assert_will_match('/test', None)
        self.assert_will_match('/TEST', '/TEST')

    def test_segment_without_trailing_slash_match_strict(self):
        self.path('/test', strict=True)

        self.assert_parsed('/test')
        self.assert_will_match('/test', '/test')
        self.assert_will_match('/test/', None)
        self.assert_will_match('/TEST', '/TEST')

    def test_segment_with_trailing_slash_mach_strict(self):
        self.path('/test/', strict=True)

        self.assert_parsed('/test/')
        self.assert_will_match('/test', None)
        self.assert_will_match('/test/', '/test/')
        self.assert_will_match('/test//', None)

    def test_segment_without_trailing_slash_non_ending(self):
        self.path('/test', end=False)

        self.assert_parsed('/test')
        self.assert_will_match('/test', '/test')
        self.assert_will_match('/test/', '/test/')
        self.assert_will_match('/test/route', '/test')
        self.assert_will_match('/route', None)

    def test_segment_with_trailing_slash_non_ending(self):
        self.path('/test/', end=False)

        self.assert_parsed('/test/')
        self.assert_will_match('/test/route', '/test')
        self.assert_will_match('/test//', '/test')
        self.assert_will_match('/test//route', '/test')

    def test_capture_segment_without_trailing_slash_non_ending(self):
        self.path('/:test', end=False)

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_template(None)
        self.assert_will_template('/abc', test='abc')

    def test_capture_segment_with_trailing_slash_non_ending(self):
        self.path('/:test/', end=False)

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'),
            '/'
        )
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_template('/abc/', test='abc')

    def test_segment_without_trailing_slash_match_strict_non_ending(self):
        self.path('/test', strict=True, end=False)

        self.assert_parsed('/test')
        self.assert_will_match('/test', '/test')
        self.assert_will_match('/test/', '/test')
        self.assert_will_match('/test/route', '/test')

    def test_segment_with_trailing_slash_match_strict_non_ending(self):
        self.path('/test/', strict=True, end=False)

        self.assert_parsed('/test/')
        self.assert_will_match('/test', None)
        self.assert_will_match('/test/', '/test/')
        self.assert_will_match('/test//', '/test/')
        self.assert_will_match('/test/route', '/test/')

    def test_segment_with_file_extension_match_strict_non_ending(self):
        self.path('/test.json', strict=True, end=False)

        self.assert_parsed('/test.json')
        self.assert_will_match('/test.json', '/test.json')
        self.assert_will_match('/test.json.hbs', None)
        self.assert_will_match('/test.json/route', '/test.json')

    def test_capture_segment_without_trailing_slash_match_strict_non_ending(self):
        self.path('/:test', strict=True, end=False)

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_match('/route/', '/route')
        self.assert_will_group('/route/', 'route', test='route')
        self.assert_will_template(None)
        self.assert_will_template('/abc', test='abc')

    def test_capture_segment_with_trailing_slash_match_strict_non_ending(self):
        self.path('/:test/', strict=True, end=False)

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'),
            '/'
        )
        self.assert_will_match('/route', None)
        self.assert_will_match('/route/', '/route/')
        self.assert_will_group('/route/', 'route', test='route')
        self.assert_will_template('/foobar/', test='foobar')

    def test_alternative_matching_paths(self):
        self.path(['/one', '/two'])

        self.assert_will_match('/one', '/one')
        self.assert_will_match('/two', '/two')
        self.assert_will_match('/three', None)
        self.assert_will_match('/one/two', None)

    def test_segment_without_trailing_slash_non_ending(self):
        self.path('/test', end=False)

        self.assert_parsed('/test')
        self.assert_will_match('/test/route', '/test')


class CaptureTests(RePathTestCase):
    def test_capture_single_segment(self):
        self.path('/:test')

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_match('/another', '/another')
        self.assert_will_group('/another', 'another', test='another')
        self.assert_will_match('/something/else', None)
        self.assert_will_match('/route.json', '/route.json')
        self.assert_will_group('/route.json', 'route.json', test='route.json')
        self.assert_will_template('/route', test='route')

    def test_capture_single_segment_match_strict(self):
        self.path('/:test', strict=True)

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_match('/route/', None)
        self.assert_will_template('/route', test='route')

    def test_capture_segment_with_trailing_slash_match_strict(self):
        self.path('/:test/', strict=True)

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'),
            '/'
        )
        self.assert_will_match('/route/', '/route/')
        self.assert_will_group('/route/', 'route', test='route')
        self.assert_will_match('/route//', None)
        self.assert_will_template('/route/', test='route')

    def test_capture_segment_without_trailing_slash_non_ending(self):
        self.path('/:test', end=False)

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('/route.json', '/route.json')
        self.assert_will_group('/route.json', 'route.json', test='route.json')
        self.assert_will_match('/route//', '/route')
        self.assert_will_group('/route//', 'route', test='route')
        self.assert_will_template('/route', test='route')

    def test_capture_segment_optional(self):
        self.path('/:test?')

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', optional=True, pattern='[^/]+?'))
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_match('/route/nested', None)
        self.assert_will_match('/', '/')
        self.assert_will_group('/', None, test=None)
        self.assert_will_match('//', None)
        self.assert_will_template('/foobar', test='foobar')

    def test_capture_segment_optional_match_strict(self):
        self.path('/:test?', strict=True)

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', optional=True, pattern='[^/]+?'))
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_match('/', None)
        self.assert_will_match('//', None)
        self.assert_will_template('/foobar', test='foobar')

    def test_capture_segment_optional_with_trailing_slash_match_strict(self):
        self.path('/:test?/', strict=True)

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', optional=True, pattern='[^/]+?'),
            '/'
        )
        self.assert_will_match('/route', None)
        self.assert_will_match('/route/', '/route/')
        self.assert_will_group('/route/', 'route', test='route')
        self.assert_will_match('/', '/')
        self.assert_will_group('/', None)
        self.assert_will_match('//', None)
        self.assert_will_template('/foobar/', test='foobar')


class RepetitionTests(RePathTestCase):
    def test_capture_segment_repeating(self):
        self.path('/:test+')

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', repeat=True, pattern='[^/]+?'))
        self.assert_will_match('/', None)
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_match('/some/basic/route', '/some/basic/route')
        self.assert_will_group('/some/basic/route', 'some/basic/route', test='some/basic/route')
        self.assert_will_match('//', None)
        self.assert_will_template(None)
        self.assert_will_template('/foobar', test='foobar')
        self.assert_will_template('/a/b/c', test=['a', 'b', 'c'])

    def test_capture_custom_segment_repeating(self):
        self.path('/:test(\\d+)+')

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', repeat=True, pattern='\\d+'))
        self.assert_will_match('/abc/456/789', None)
        self.assert_will_match('/123/456/789', '/123/456/789')
        self.assert_will_group('/123/456/789', '123/456/789', test='123/456/789')
        self.assert_will_template(None, test='abc')
        self.assert_will_template('/123', test=123)
        self.assert_will_template('/1/2/3', test=[1, 2, 3])

    def test_segment_capture_extension_from_optional_cases_repeating(self):
        self.path('/route.:ext(json|xml)+')

        self.assert_parsed(
            '/route',
            token(name='ext', prefix='.', delimiter='.', repeat=True, pattern='json|xml')
        )
        self.assert_will_match('/route', None)
        self.assert_will_match('/route.json', '/route.json')
        self.assert_will_group('/route.json', 'json', ext='json')
        self.assert_will_match('/route.xml.json', '/route.xml.json')
        self.assert_will_group('/route.xml.json', 'xml.json', ext='xml.json')
        self.assert_will_match('/route.html', None)
        self.assert_will_template(None, ext='foobar')
        self.assert_will_template('/route.xml', ext='xml')
        self.assert_will_template('/route.xml.json', ext=['xml', 'json'])

    def test_segment_capture_optional_repeat(self):
        self.path('/:test*')

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', optional=True, repeat=True, pattern='[^/]+?'))
        self.assert_will_match('/', '/')
        self.assert_will_group('/', None, test=None)
        self.assert_will_match('//', None)
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', test='route')
        self.assert_will_match('/some/basic/route', '/some/basic/route')
        self.assert_will_group('/some/basic/route', 'some/basic/route', test='some/basic/route')
        self.assert_will_template('')
        self.assert_will_template('/foobar', test='foobar')
        self.assert_will_template('/foo/bar', test=['foo', 'bar'])

    def test_segment_capture_extension_repeating(self):
        self.path('/route.:ext([a-z]+)*')

        self.assert_parsed(
            '/route',
            token(name='ext', prefix='.', delimiter='.', optional=True, repeat=True, pattern='[a-z]+')
        )
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', None)
        self.assert_will_match('/route.json', '/route.json')
        self.assert_will_group('/route.json', 'json', ext='json')
        self.assert_will_match('/route.json.xml', '/route.json.xml')
        self.assert_will_group('/route.json.xml', 'json.xml', ext='json.xml')
        self.assert_will_match('/route.123', None)
        self.assert_will_template('/route')
        self.assert_will_template('/route', ext=[])
        self.assert_will_template(None, ext='123')
        self.assert_will_template('/route.foobar', ext='foobar')
        self.assert_will_template('/route.foo.bar', ext=['foo', 'bar'])

    def test_capture_custom_segment_digits_only(self):
        self.path('/:test(\\d+)')

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', pattern='\\d+'))
        self.assert_will_match('/123', '/123')
        self.assert_will_group('/123', '123', test='123')
        self.assert_will_match('/abc', None)
        self.assert_will_match('/123/abc', None)
        self.assert_will_template(None, test='abc')
        self.assert_will_template('/123', test='123')

    def test_capture_custom_segment_digits_only_non_ending(self):
        self.path('/:test(\\d+)', end=False)

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', pattern='\\d+'))
        self.assert_will_match('/123', '/123')
        self.assert_will_group('/123', '123', test='123')
        self.assert_will_match('/abc', None)
        self.assert_will_match('/123/abc', '/123')
        self.assert_will_group('/123/abc', '123', test='123')
        self.assert_will_template('/123', test='123')

    def test_capture_custom_segment_any_characters(self):
        self.path('/:test(.*)')

        self.assert_parsed(token(name='test', prefix='/', delimiter='/', pattern='.*'))
        self.assert_will_match('/anything/goes/here', '/anything/goes/here')
        self.assert_will_group('/anything/goes/here', 'anything/goes/here', test='anything/goes/here')
        self.assert_will_template('/', test='')
        self.assert_will_template('/abc', test='abc')
        self.assert_will_template('/abc%2F123', test='abc/123')

    def test_capture_custom_segment_letters_only(self):
        self.path('/:route([a-z]+)')

        self.assert_parsed(token(name='route', prefix='/', delimiter='/', pattern='[a-z]+'))
        self.assert_will_match('/abcde', '/abcde')
        self.assert_will_group('/abcde', 'abcde', route='abcde')
        self.assert_will_match('/12345', None)
        self.assert_will_template(None, route='')
        self.assert_will_template(None, route='123')
        self.assert_will_template('/abc', route='abc')

    def test_capure_segment_from_selected_strings(self):
        self.path('/:route(this|that)')

        self.assert_parsed(token(name='route', prefix='/', delimiter='/', pattern='this|that'))
        self.assert_will_match('/this', '/this')
        self.assert_will_group('/this', 'this', route='this')
        self.assert_will_match('/that', '/that')
        self.assert_will_group('/that', 'that', route='that')
        self.assert_will_match('/foo', None)
        self.assert_will_template('/this', route='this')
        self.assert_will_template(None, route='foo')
        self.assert_will_template('/that', route='that')


class UnprexedPatternTests(RePathTestCase):
    def test_match_unprefixed_string(self):
        self.path('test')

        self.assert_parsed('test')
        self.assert_will_match('test', 'test')
        self.assert_will_match('/test', None)

    def test_capture_unprefixed_string(self):
        self.path(':test')

        self.assert_parsed(token(name='test', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('route', 'route')
        self.assert_will_group('route', 'route')
        self.assert_will_match('/route', None)
        self.assert_will_match('route/', 'route/')
        self.assert_will_group('route/', 'route')
        self.assert_will_template(None, test='')
        self.assert_will_template(None)
        self.assert_will_template(None, test=None)
        self.assert_will_template('route', test='route')

    def test_capture_unprefixed_string_match_strict(self):
        self.path(':test', strict=True)

        self.assert_parsed(token(name='test', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('route', 'route')
        self.assert_will_group('route', 'route', test='route')
        self.assert_will_match('/route', None)
        self.assert_will_match('route/', None)
        self.assert_will_template('route', test='route')

    def test_capture_unprefixed_string_non_ending(self):
        self.path(':test', end=False)

        self.assert_parsed(token(name='test', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('route', 'route')
        self.assert_will_group('route', 'route', test='route')
        self.assert_will_match('/route', None)
        self.assert_will_match('route/', 'route/')
        self.assert_will_group('route/', 'route', test='route')
        self.assert_will_match('route/foobar', 'route')
        self.assert_will_group('route/foobar', 'route', test='route')
        self.assert_will_template('route', test='route')

    def test_capture_unprefixed_string_optional(self):
        self.path(':test?')

        self.assert_parsed(token(name='test', delimiter='/', optional=True, pattern='[^/]+?'))
        self.assert_will_match('route', 'route')
        self.assert_will_group('route', 'route', test='route')
        self.assert_will_match('/route', None)
        self.assert_will_match('', '')
        self.assert_will_group('', None)
        self.assert_will_match('route/foobar', None)
        self.assert_will_template('')
        self.assert_will_template(None, test='')
        self.assert_will_template('route', test='route')


class PathExtensionTests(RePathTestCase):
    def test_match_filename_and_extension(self):
        self.path('/test.json')

        self.assert_parsed('/test.json')
        self.assert_will_match('/test.json', '/test.json')
        self.assert_will_match('/route.json', None)
        self.assert_will_template('/test.json')

    def test_capture_filename_with_specific_extension(self):
        self.path('/:test.json')

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'),
            '.json'
        )
        self.assert_will_match('/test.json', '/test.json')
        self.assert_will_group('/test.json', 'test', test='test')
        self.assert_will_match('/route.json', '/route.json')
        self.assert_will_group('/route.json', 'route', test='route')
        self.assert_will_match('/route.json.json', '/route.json.json')
        self.assert_will_group('/route.json.json', 'route.json', test='route.json')
        self.assert_will_template('/foo.json', test='foo')

    def test_match_filename_capture_extension(self):
        self.path('/test.:format')

        self.assert_parsed(
            '/test',
            token(name='format', prefix='.', delimiter='.', pattern='[^.]+?')
        )
        self.assert_will_match('/test.html', '/test.html')
        self.assert_will_group('/test.html', 'html', format='html')
        self.assert_will_match('/test.hbs.html', None)
        self.assert_will_template(None)
        self.assert_will_template(None, format='')
        self.assert_will_template('/test.foo', format='foo')

    def test_match_filename_capture_extension_repeating(self):
        self.path('/test.:format+')

        self.assert_parsed(
            '/test',
            token(name='format', prefix='.', delimiter='.', repeat=True, pattern='[^.]+?')
        )
        self.assert_will_match('/test.html', '/test.html')
        self.assert_will_group('/test.html', 'html', format='html')
        self.assert_will_match('/test.hbs.html', '/test.hbs.html')
        self.assert_will_group('/test.hbs.html', 'hbs.html', format='hbs.html')
        self.assert_will_template(None, format=[])
        self.assert_will_template('/test.foo', format='foo')
        self.assert_will_template('/test.foo.bar', format=['foo', 'bar'])

    def test_match_filename_capture_extension_non_ending(self):
        self.path('/test.:format', end=False)

        self.assert_parsed(
            '/test',
            token(name='format', prefix='.', delimiter='.', pattern='[^.]+?')
        )
        self.assert_will_match('/test.html', '/test.html')
        self.assert_will_group('/test.html', 'html', format='html')
        self.assert_will_match('/test.hbs.html', None)
        self.assert_will_template('/test.foo', format='foo')

    def test_match_filename_capture_extension_expect_trailing_dot(self):
        self.path('/test.:format.')

        self.assert_parsed(
            '/test',
            token(name='format', prefix='.', delimiter='.', pattern='[^.]+?'),
            '.'
        )
        self.assert_will_match('/test.html.', '/test.html.')
        self.assert_will_group('/test.html.', 'html', format='html')
        self.assert_will_match('/test.hbs.html', None)
        self.assert_will_template(None, format='')
        self.assert_will_template('/test.foo.', format='foo')

    def test_capture_filename_and_extension_separately(self):
        self.path('/:test.:format')

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'),
            token(name='format', prefix='.', delimiter='.', pattern='[^.]+?')
        )
        self.assert_will_match('/route.html', '/route.html')
        self.assert_will_group('/route.html', 'route', 'html', test='route', format='html')
        self.assert_will_match('/route', None)
        self.assert_will_match('/route.html.json', '/route.html.json')
        self.assert_will_group('/route.html.json', 'route.html', 'json', test='route.html', format='json')
        self.assert_will_template(None)
        self.assert_will_template('/route.foo', test='route', format='foo')

    def test_capture_filename_and_optionally_extension(self):
        self.path('/:test.:format?')

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'),
            token(name='format', prefix='.', delimiter='.', optional=True, pattern='[^.]+?')
        )
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', None)
        self.assert_will_match('/route.json', '/route.json')
        self.assert_will_group('/route.json', 'route', 'json', test='route', format='json')
        self.assert_will_match('/route.json.html', '/route.json.html')
        self.assert_will_group('/route.json.html', 'route.json', 'html')
        self.assert_will_template('/route', test='route')
        self.assert_will_template(None, test='route', format='')
        self.assert_will_template('/route.foo', test='route', format='foo')

    def test_capture_filename_and_optionally_extension_non_ending(self):
        self.path('/:test.:format?', end=False)

        self.assert_parsed(
            token(name='test', prefix='/', delimiter='/', pattern='[^/]+?'),
            token(name='format', prefix='.', delimiter='.', optional=True, pattern='[^.]+?')
        )
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route', None, test='route', format=None)
        self.assert_will_match('/route.json', '/route.json')
        self.assert_will_group('/route.json', 'route', 'json', test='route', format='json')
        self.assert_will_match('/route.json.html', '/route.json.html')
        self.assert_will_group('/route.json.html', 'route.json', 'html', test='route.json', format='html')
        self.assert_will_template('/route', test='route')
        self.assert_will_template('/route', test='route', format=None)
        self.assert_will_template(None, test='route', format='')
        self.assert_will_template('/route.foo', test='route', format='foo')

    def test_capture_extension_with_custom_suffix(self):
        self.path('/test.:format(.*)z', end=False)

        self.assert_parsed(
            '/test',
            token(name='format', prefix='.', delimiter='.', pattern='.*'),
            'z'
        )
        self.assert_will_match('/test.abc', None)
        self.assert_will_match('/test.z', '/test.z')
        self.assert_will_group('/test.z', '', format='')
        self.assert_will_match('/test.abcz', '/test.abcz')
        self.assert_will_group('/test.abcz', 'abc', format='abc')
        self.assert_will_template(None)
        self.assert_will_template('/test.z', format='')
        self.assert_will_template('/test.fooz', format='foo')


class UnnamedCaptureGroupTests(RePathTestCase):
    def test_capture_segment_digits_only(self):
        self.path('/(\\d+)')

        self.assert_parsed(token(name='0', prefix='/', delimiter='/', pattern='\\d+'))
        self.assert_will_match('/123', '/123')
        self.assert_will_group('/123', '123')
        self.assert_will_match('/abc', None)
        self.assert_will_match('/123/abc', None)
        self.assert_will_template(None)

    def test_capture_segment_digits_non_ending(self):
        self.path('/(\\d+)', end=False)

        self.assert_parsed(token(name='0', prefix='/', delimiter='/', pattern='\\d+'))
        self.assert_will_match('/123', '/123')
        self.assert_will_group('/123', '123')
        self.assert_will_match('/abc', None)
        self.assert_will_match('/123/abc', '/123')
        self.assert_will_group('/123/abc', '123')
        self.assert_will_match('/123/', '/123/')
        self.assert_will_group('/123/', '123')

    def test_capture_optional_segment_digits_only(self):
        self.path('/(\\d+)?')

        self.assert_parsed(token(name='0', prefix='/', delimiter='/', optional=True, pattern='\\d+'))
        self.assert_will_match('/', '/')
        self.assert_will_group('/', None)
        self.assert_will_match('/123', '/123')
        self.assert_will_group('/123', '123')
        self.assert_will_template('')

    def test_capture_anything(self):
        self.path('/(.*)')

        self.assert_parsed(token(name='0', prefix='/', delimiter='/', pattern='.*'))
        self.assert_will_match('/', '/')
        self.assert_will_group('/', '')
        self.assert_will_match('/route', '/route')
        self.assert_will_group('/route', 'route')
        self.assert_will_match('/route/nested', '/route/nested')
        self.assert_will_group('/route/nested', 'route/nested')


class EscapedCharacterTests(RePathTestCase):
    def test_escaped_parans(self):
        self.path('/\\(testing\\)')

        self.assert_parsed('/(testing)')
        self.assert_will_match('/testing', None)
        self.assert_will_match('/(testing)', '/(testing)')

    def test_escaped_regex_special_characters(self):
        self.path('/.+\\*?=^!:${}[]|')

        self.assert_parsed('/.+*?=^!:${}[]|')
        self.assert_will_match('/.+*?=^!:${}[]|', '/.+*?=^!:${}[]|')


class WildcardPatternTests(RePathTestCase):
    def test_match_whatever(self):
        self.path('/*')

        self.assert_parsed(token(name='0', prefix='/', delimiter='/', pattern='.*'))
        self.assert_will_match('', None)
        self.assert_will_match('/', '/')
        self.assert_will_group('/', '')
        self.assert_will_match('/foo/bar', '/foo/bar')
        self.assert_will_group('/foo/bar', 'foo/bar')

    def test_match_path_and_optional_nested_paths(self):
        self.path('/foo/*')

        self.assert_parsed(
            '/foo',
            token(name='0', prefix='/', delimiter='/', pattern='.*')
        )
        self.assert_will_match('', None)
        self.assert_will_match('/test', None)
        self.assert_will_match('/foo', None)
        self.assert_will_match('/foo/', '/foo/')
        self.assert_will_group('/foo/', '')
        self.assert_will_match('/foo/bar', '/foo/bar')
        self.assert_will_group('/foo/bar', 'bar')

    def test_capture_path_with_optional_nested_paths(self):
        self.path('/:foo/*')

        self.assert_parsed(
            token(name='foo', prefix='/', delimiter='/', pattern='[^/]+?'),
            token(name='0', prefix='/', delimiter='/', pattern='.*')
        )
        self.assert_will_match('', None)
        self.assert_will_match('/test', None)
        self.assert_will_match('/foo', None)
        self.assert_will_match('/foo/', '/foo/')
        self.assert_will_group('/foo/', 'foo', '', foo='foo')
        self.assert_will_match('/foo/bar', '/foo/bar')
        self.assert_will_group('/foo/bar', 'foo', 'bar', foo='foo')
        self.assert_will_template(None, foo='foo')


class ExampleUseTests(RePathTestCase):
    def test_capture_multiple_segments(self):
        self.path('/:foo/:bar')

        self.assert_parsed(
            token(name='foo', prefix='/', delimiter='/', pattern='[^/]+?'),
            token(name='bar', prefix='/', delimiter='/', pattern='[^/]+?')
        )
        self.assert_will_match('/match/route', '/match/route')
        self.assert_will_group('/match/route', 'match', 'route', foo='match', bar='route')
        self.assert_will_template('/a/b', foo='a', bar='b')

    def test_capture_segments_with_custom_patterns(self):
        self.path('/:remote([\\w\\-.]+)/:user([\\w\\-]+)')

        self.assert_parsed(
            token(name='remote', prefix='/', delimiter='/', pattern='[\\w\\-.]+'),
            token(name='user', prefix='/', delimiter='/', pattern='[\\w\\-]+')
        )
        self.assert_will_match('/endpoint/user', '/endpoint/user')
        self.assert_will_group('/endpoint/user', 'endpoint', 'user', remote='endpoint', user='user')
        self.assert_will_match('/endpoint/user-name', '/endpoint/user-name')
        self.assert_will_group('/endpoint/user-name', 'endpoint', 'user-name', remote='endpoint', user='user-name')
        self.assert_will_match('/foo.bar/user-name', '/foo.bar/user-name')
        self.assert_will_group('/foo.bar/user-name', 'foo.bar', 'user-name', remote='foo.bar', user='user-name')
        self.assert_will_template('/foo/bar', remote='foo', user='bar')
        self.assert_will_template('/foo.bar/uno', remote='foo.bar', user='uno')

    def test_capture_segment_followed_by_question_mark(self):
        self.path('/:foo\\?')

        self.assert_parsed(
            token(name='foo', prefix='/', delimiter='/', pattern='[^/]+?'),
            '?'
        )
        self.assert_will_match('/route?', '/route?')
        self.assert_will_group('/route?', 'route', foo='route')
        self.assert_will_template('/bar?', foo='bar')

    def test_capture_segment_with_unicode_characters(self):
        self.path('/:foo')

        self.assert_parsed(token(name='foo', prefix='/', delimiter='/', pattern='[^/]+?'))
        self.assert_will_match('/caf\xe9', '/caf\xe9')
        self.assert_will_group('/caf\xe9', 'caf\xe9', foo='caf\xe9')
        self.assert_will_template('/caf%C3%A9', foo='caf\xe9')


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

    def test_match_returns_regex_match_results(self):
        path = '/:foo/:bar'

        results = repath.match(path, '/something/another')

        self.assertIsNotNone(results)
        self.assertIsNotNone(results.groupdict())
        self.assertEqual(results.groupdict()['foo'], 'something')
        self.assertEqual(results.groupdict()['bar'], 'another')

    def test_compile_returns_regex_object(self):
        path = '/route/:foo'

        regex = repath.compile(path, re.I)

        self.assertIsInstance(regex, type(re.compile('')))
        self.assertIsNotNone(regex.match('/ROUTE/test'))
        self.assertIsNone(regex.match('/routes/test'))


class CompileErrorTests(unittest.TestCase):
    def check_to_path(self, path, params, exception, message):
        to_path = repath.template(path)
        with self.assertRaises(exception) as context:
            to_path(params)

        self.assertEqual(context.exception.args[0], message)

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
