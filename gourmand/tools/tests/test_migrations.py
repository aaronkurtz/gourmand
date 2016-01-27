from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class MigrationTest(TestCase):
    def test_migration(self):
        output = StringIO()

        try:
            call_command('makemigrations', interactive=False, dry_run=True, exit_code=True,
                         stdout=output)
        except SystemExit as e:
            self.assertEqual(str(e), '1')
        else:
            self.fail('Migrations required:\n{}'.format(output.getvalue()))
