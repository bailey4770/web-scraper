import unittest
import logging
from web_scraper.crawl import (
    normalize_url,
    get_h1_from_html,
    get_first_paragraph_from_html,
    get_urls_from_html,
    get_images_from_html,
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


class TestGetURLsFromHTML(unittest.TestCase):
    def test_absolute_url(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="https://blog.boot.dev"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev"]
        self.assertEqual(actual, expected)

    def test_absolute_url_and_relative_image(self):
        input_url = "https://blog.boot.dev"
        input_body = """<html>
  <body>
    <a href="https://blog.boot.dev">Go to Boot.dev</a>
    <img src="/logo.png" alt="Boot.dev Logo" />
  </body>
</html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev"]
        self.assertEqual(actual, expected)

    def test_list_relative_links(self):
        input_url = "https://blog.boot.dev"
        input_body = """<html>
  <body>
    <a href="/go">Go to Boot.dev</a>
    <a href="/python">Go to Boot.dev</a>
    <a href="/cooking_recipes">Go to Boot.dev</a>
    <a href="/memes">Go to Boot.dev</a>
  </body>
</html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://blog.boot.dev/go",
            "https://blog.boot.dev/python",
            "https://blog.boot.dev/cooking_recipes",
            "https://blog.boot.dev/memes",
        ]
        self.assertEqual(actual, expected)

    def test_no_links(self):
        input_url = "https://blog.boot.dev"
        input_body = """<html>
  <body>
    <p>text</p>
  </body>
</html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_empty_string(self):
        input_url = "https://blog.boot.dev"
        input_body = ""
        self.assertRaises(ValueError, get_urls_from_html, input_body, input_url)

    def test_fragment_only_link(self):
        input_url = "https://blog.boot.dev"
        input_body = '<a href="#section">Jump</a>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev#section"]
        self.assertEqual(actual, expected)

    def test_deeply_nested_links(self):
        input_url = "https://blog.boot.dev"
        input_body = '<div><ul><li><a href="/deep">link</a></li></ul></div>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/deep"]
        self.assertEqual(actual, expected)

    def test_fragment_and_query(self):
        input_url = "https://blog.boot.dev"
        input_body = '<a href="/path?foo=bar#section">link</a>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/path?foo=bar#section"]
        self.assertEqual(actual, expected)

    def test_link_no_scheme(self):
        input_url = "https://blog.boot.dev"
        input_body = """<html>
  <body>
    <a href="www.wikipedia.com">Go to Boot.dev</a>
  </body>
</html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://www.wikipedia.com"]
        self.assertEqual(actual, expected)


class TestGetImagesFromHTML(unittest.TestCase):
    def test_get_images_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/logo.png"]
        self.assertEqual(actual, expected)

    def test_absolute_image(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="https://cdn.example.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.example.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_no_images(self):
        input_url = "https://blog.boot.dev"
        input_body = "<html><body><p>no images</p></body></html>"
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_multiple_images(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="/a.png"><img src="/b.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/a.png", "https://blog.boot.dev/b.png"]
        self.assertEqual(actual, expected)

    def test_img_without_src(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img alt="no src"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_empty_string(self):
        input_url = "https://blog.boot.dev"
        self.assertRaises(ValueError, get_images_from_html, "", input_url)

    def test_links_not_included(self):
        input_url = "https://blog.boot.dev"
        input_body = (
            '<html><body><a href="/page">link</a><img src="/a.png"></body></html>'
        )
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/a.png"]
        self.assertEqual(actual, expected)

    def test_absolute_image_src(self):
        input_url = "https://blog.boot.dev"
        input_body = (
            '<html><body><img src="https://www.wikipedia.com/page.png"></body></html>'
        )
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://www.wikipedia.com/page.png"]
        self.assertEqual(actual, expected)

    def test_malformed_img_src(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="www.wikipedia.com/page.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://www.wikipedia.com/page.png"]
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    _ = unittest.main()
