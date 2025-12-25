import unittest
import json
from io import StringIO
from django.core.management import call_command
from django.conf import settings

# Ensure settings are configured
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=['django_nis2_shield'],
    )
    import django
    django.setup()

from django_nis2_shield.siem_presets import get_elastic_mapping, get_splunk_props

class TestReporting(unittest.TestCase):
    def test_siem_presets(self):
        # Elastic
        mapping = get_elastic_mapping()
        self.assertIn('mappings', mapping)
        self.assertEqual(mapping['mappings']['properties']['timestamp']['type'], 'date')
        
        # Splunk
        props = get_splunk_props()
        self.assertIn('[django_nis2_shield]', props)

    def test_incident_report_command(self):
        out = StringIO()
        call_command('generate_incident_report', hours=24, stdout=out)
        
        output = out.getvalue()
        data = json.loads(output)
        
        self.assertIn('generated_at', data)
        self.assertIn('incidents', data)
        self.assertEqual(data['period_hours'], 24)
        # Check if our mock incident is there
        self.assertEqual(data['incidents'][0]['type'], 'RATE_LIMIT_BLOCK')

if __name__ == '__main__':
    unittest.main()
