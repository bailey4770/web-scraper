import unittest
import logging
from web_scraper.crawl import normalize_url

logging.basicConfig(level=logging.INFO)


class TestNormalizeURL(unittest.TestCase):
    def test_remove_https(self):
        input_url = "https://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_remove_https_www(self):
        input_url = "https://www.blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_remove_http(self):
        input_url = "http://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_remove_http_www(self):
        input_url = "http://www.blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_remove_trailing_slash(self):
        input_url = "https://blog.boot.dev/"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev"
        self.assertEqual(actual, expected)

    def test_remove_all_trailing_slashes(self):
        input_url = "https://blog.boot.dev////"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev"
        self.assertEqual(actual, expected)

    def test_remove_query_strings(self):
        input_url = "https://blog.boot.dev/path?foo=bar"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_empty_string(self):
        input_url = ""
        self.assertRaises(ValueError, normalize_url, input_url)

    def test_remove_sections(self):
        input_url = "https://blog.boot.dev/path#section"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_remove_port_numbers(self):
        input_url = "https://blog.boot.dev:8080/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_no_leading_double_slash(self):
        input_url = "www.blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_multiple_leading_www(self):
        input_url = "www.www.www.blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    _ = unittest.main()
