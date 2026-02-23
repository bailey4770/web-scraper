import unittest
import logging
from web_scraper.crawl import (
    normalize_url,
    get_h1_from_html,
    get_first_paragraph_from_html,
)

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


class TestGetH1FromHTML(unittest.TestCase):
    def test_normal(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_h1_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_no_h1(self):
        input_body = "<html><body><p>Test Title</p></body></html>"
        actual = get_h1_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_multiple_h1(self):
        input_body = (
            "<html><body><h1>Test Title</h1><h1>Another title</h1></body></html>"
        )
        actual = get_h1_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_nested_tags(self):
        input_body = "<html><body><h1><a href='...'>Hello</a></h1></body></html>"
        actual = get_h1_from_html(input_body)
        expected = "Hello"
        self.assertEqual(actual, expected)

    def test_whitespace(self):
        input_body = "<html><body><h1>    Test Title     </h1></body></html>"
        actual = get_h1_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_empty_string(self):
        input_url = ""
        self.assertRaises(ValueError, get_h1_from_html, input_url)


class TestGetFirstParagraphFromHTML(unittest.TestCase):
    def test_p_inside_and_outside_main(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_no_p_in_main(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_multitple_ps(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
                <p>Second paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_no_main_multiple_ps(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <p>Main paragraph.</p>
            <p>Second paragraph.</p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)

    def test_p_whitespace(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>    <p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_empty_string(self):
        input_url = ""
        self.assertRaises(ValueError, get_first_paragraph_from_html, input_url)


if __name__ == "__main__":
    _ = unittest.main()
