from functools import partial
from django.test import TestCase
from mock import Mock, MagicMock, patch
from django.test.client import RequestFactory
from cache_tools.tools import cache_page_in_group, get_group_key, expire_cache_group, TIME_TO_CACHE

class CachingTest(TestCase):
    """
    # This gets overwritten by the function below it. Why's it here?
    # Also, if it gets run, it fails
    def test_get_group_key(self):
        key = get_group_key('test')
        assert key == 'test2'
    """

    @patch('cache_tools.tools.cache.get')
    def test_get_group_key(self, cache_get):
        cache_get.return_value = 15

        key = get_group_key('test')
        assert key == 'test15'

    @patch('cache_tools.tools.cache_page')
    def test_get_group_key(self, cache_page):
        cache_page.return_value = 'success'


    @patch('cache_tools.tools.cache.get')
    @patch('cache_tools.tools.cache.set')
    def test_expire_cache_group(self, cache_set, cache_get):
        cache_get.return_value = 15
        expire_cache_group('test')
        cache_set.assert_called_with('cache_group_test', 16, TIME_TO_CACHE)


    @patch('cache_tools.tools.cache.get')
    @patch('cache_tools.tools.cache_page')
    def test_cache_group(self, cache_page, cache_get):
        dict_group = {'some_id': 4, 'some key': 'hello',
            'another key': 'world'}
        tuple_group = ('some key', 'some_id', 'another key')
        callable_group = lambda **kwargs: dict_group
        groups = ('test', dict_group, tuple_group, callable_group)

        cache_get.return_value = 15
        view = Mock()

        for group in groups:
            decorated_view = cache_page_in_group(group)(view)
            request = RequestFactory().get('/test/')
            response = decorated_view(request, **dict_group)

            expected_prefix = '366791489260553153815'
            if isinstance(group, basestring):
                expected_prefix = 'test15'
            cache_page.assert_called_with(TIME_TO_CACHE,
                key_prefix=expected_prefix)

    @patch('cache_tools.tools.cache_page')
    def test_cache_group_initial(self, cache_page):
        view = Mock()
        decorated_view = cache_page_in_group('test')(view)
        request = RequestFactory().get('/test/')
        response = decorated_view(request)

        cache_page.assert_called_with(TIME_TO_CACHE, key_prefix='test1')
