from django.core.management.base import BaseCommand
from django.conf import settings
import json
import os
import datetime
import re

class Command(BaseCommand):
    help = 'Generates an incident report based on recent logs (Simulated for MVP).'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24, help='Lookback period in hours')
        parser.add_argument('--output', type=str, default=None, help='Output file path')

    def handle(self, *args, **options):
        hours = options['hours']
        output_file = options['output']
        
        self.stderr.write(f"Scanning for incidents in the last {hours} hours...")
        
        # In a real scenario, we would query the SIEM or a database.
        # For this MVP, we will simulate finding incidents based on what the Enforcer would log.
        # We'll look for lines in the log file if it exists, or just generate a sample if not.
        
        incidents = []
        
        # Mocking logic for demonstration purposes since we don't have a persistent log file in this env
        # In production, this would read `settings.LOGGING` config to find the file.
        
        # Let's assume we found some rate limit blocks
        incidents.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "RATE_LIMIT_BLOCK",
            "severity": "HIGH",
            "details": {
                "ip": "192.168.1.100",
                "count": 105,
                "limit": 100
            }
        })
        
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "period_hours": hours,
            "total_incidents": len(incidents),
            "incidents": incidents,
            "compliance_note": "NIS2 Art. 21 requires notification of significant incidents within 24h."
        }
        
        json_output = json.dumps(report, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_output)
            self.stdout.write(self.style.SUCCESS(f"Report written to {output_file}"))
        else:
            self.stdout.write(json_output)
