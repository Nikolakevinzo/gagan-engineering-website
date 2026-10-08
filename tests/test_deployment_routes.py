"""Check configured route precedence; this does not emulate Vercel deployment."""
import json
import re
import unittest
from pathlib import Path


ROUTES = json.loads((Path(__file__).resolve().parents[1] / 'vercel.json').read_text())['routes']


def configured_route(path, user_agent='Mozilla/5.0'):
    for route in ROUTES:
        if 'src' not in route or not re.fullmatch(route['src'], path):
            continue
        conditions = route.get('has', [])
        if any(condition['type'] == 'host' for condition in conditions):
            continue  # These checks use the production custom hostname.
        if any(not re.fullmatch(condition['value'], user_agent)
               for condition in conditions if condition['type'] == 'header'):
            continue
        return route
    raise AssertionError(f'No configured route for {path}')


class DeploymentRouteTests(unittest.TestCase):
    def test_existing_browser_routes_keep_the_react_app(self):
        for path in ('/', '/products', '/products/automatic-ctl-machine',
                     '/products/category/roll-forming-sheet-metal', '/blog',
                     '/blog/gc-roofing-sheet-manufacturing-business-guide',
                     '/about', '/factory', '/contact', '/privacy-policy',
                     '/return-policy', '/terms', '/admin', '/admin/login',
                     '/admin/blogs/edit/example'):
            with self.subTest(path=path):
                route = configured_route(path)
                self.assertEqual(route['dest'], 'frontend/index.html')
                self.assertEqual(route.get('status', 200), 200)

    def test_unknown_browser_paths_are_nonindexable_404s(self):
        for path in ('/non-existent-machine-test-404', '/bogus/extra/path', '/blog/a/b'):
            with self.subTest(path=path):
                route = configured_route(path)
                self.assertEqual(route['status'], 404)
                self.assertIn('noindex', route['headers']['X-Robots-Tag'])

    def test_crawler_pages_reach_the_server_before_browser_fallback(self):
        for path in ('/blog', '/blog/example', '/products/example', '/unknown'):
            with self.subTest(path=path):
                route = configured_route(path, 'Googlebot')
                self.assertEqual(route['dest'], '/api/index.py?__seo_path=$1')

    def test_legacy_aliases_redirect_before_crawler_rewrite(self):
        expected = {'/product': '/products', '/gallery': '/factory',
                    '/returns': '/return-policy',
                    '/category/roll-forming-sheet-metal': '/products/category/$1'}
        for path, destination in expected.items():
            for user_agent in ('Mozilla/5.0', 'Googlebot'):
                with self.subTest(path=path, user_agent=user_agent):
                    route = configured_route(path, user_agent)
                    self.assertEqual(route['status'], 301)
                    self.assertEqual(route['headers']['Location'],
                                     'https://www.gaganengineerings.in' + destination)


if __name__ == '__main__':
    unittest.main()
