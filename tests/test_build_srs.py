import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'build_srs', Path(__file__).resolve().parents[1] / 'scripts' / 'build_srs.py')
build_srs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_srs)


class PayloadTests(unittest.TestCase):
    def test_apex_and_subdomain_semantics(self):
        rule = build_srs.convert_payload(
            ['exact.example', '+.suffix.example', '.subdomains.example'], 'domain')['rules'][0]
        self.assertEqual(rule['domain'], ['exact.example'])
        self.assertEqual(rule['domain_suffix'], ['suffix.example', '.subdomains.example'])

    def test_ipv4_and_ipv6(self):
        rule = build_srs.convert_payload(['192.0.2.0/24', '2001:db8::/32'], 'ipcidr')
        self.assertEqual(rule['rules'][0]['ip_cidr'], ['192.0.2.0/24', '2001:db8::/32'])

    def test_unsupported_pattern_is_not_silently_changed(self):
        for pattern in ['*.example.com', '+.*.example.com']:
            with self.subTest(pattern=pattern), self.assertRaises(ValueError):
                build_srs.convert_payload([pattern], 'domain')

    def test_invalid_ip_and_empty_payload_fail(self):
        for lines in [['invalid/24'], []]:
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                build_srs.convert_payload(lines, 'ipcidr')


if __name__ == '__main__':
    unittest.main()
