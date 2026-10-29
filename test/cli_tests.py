#!/usr/bin/env python3

import pathlib
import subprocess
import sys
import tempfile
import unittest


PROGRAM = str(pathlib.Path(sys.argv.pop(1)).resolve())


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        for name in ('-README.md', '-e', '--extension', '--unsafe', '--', 'ok.md'):
            pathlib.Path(self.directory.name, name).write_text('# Hello\n', encoding='utf-8')

    def convert(self, *arguments, text=''):
        return subprocess.run(
            [PROGRAM, *arguments], input=text, capture_output=True,
            text=True, cwd=self.directory.name, timeout=5)

    def test_dash_prefixed_files(self):
        for name in ('-README.md', '-e', '--extension', '--unsafe', '--'):
            with self.subTest(name=name):
                result = self.convert('--', name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, '<h1>Hello</h1>\n')

    def test_options_before_delimiter(self):
        result = self.convert('-t', 'commonmark', '-e', 'table', '--', '-e')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '# Hello\n')

    def test_multiple_files(self):
        result = self.convert('ok.md', '--', '-README.md', '-e')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '<h1>Hello</h1>\n' * 3)

    def test_standard_input(self):
        for arguments in ((), ('--',)):
            with self.subTest(arguments=arguments):
                result = self.convert(*arguments, text='# Hello\n')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, '<h1>Hello</h1>\n')

    def test_unknown_options_still_fail(self):
        for argument in ('--bogus', '-README.md'):
            with self.subTest(argument=argument):
                self.assertNotEqual(self.convert(argument).returncode, 0)


if __name__ == '__main__':
    unittest.main()