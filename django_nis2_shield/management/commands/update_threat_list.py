from django.core.management.base import BaseCommand
from django.core.cache import cache
import urllib.request
import logging

logger = logging.getLogger('django_nis2_shield')

class Command(BaseCommand):
    help = 'Updates the list of Tor Exit Nodes for the NIS2 Shield.'

    def handle(self, *args, **options):
        url = "https://check.torproject.org/torbulkexitlist"
        self.stdout.write(f"Downloading Tor Exit Nodes from {url}...")
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = response.read().decode('utf-8')
                
            ips = set(line.strip() for line in data.splitlines() if line.strip())
            
            # Cache for 24 hours (86400 seconds)
            cache.set('nis2_tor_exit_nodes', ips, timeout=86400)
            
            self.stdout.write(self.style.SUCCESS(f"Successfully updated {len(ips)} Tor Exit Nodes."))
            logger.info(f"NIS2 Threat List Updated: {len(ips)} Tor nodes.")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to update Tor list: {e}"))
            logger.error(f"NIS2 Threat List Update Failed: {e}")
