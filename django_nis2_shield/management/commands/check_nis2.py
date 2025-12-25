from django.core.management.base import BaseCommand
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Audits the Django configuration for NIS2 compliance.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('[NIS2 SHIELD AUDIT REPORT]'))
        self.stdout.write('------------------------------------------------')
        
        score = 0
        total_checks = 0
        
        # Check 1: DEBUG
        total_checks += 1
        if not settings.DEBUG:
            self.stdout.write(self.style.SUCCESS('[PASS] DEBUG is False'))
            score += 1
        else:
            self.stdout.write(self.style.ERROR('[FAIL] DEBUG is True (CRITICAL)'))

        # Check 2: ALLOWED_HOSTS
        total_checks += 1
        if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS != ['*']:
             self.stdout.write(self.style.SUCCESS('[PASS] ALLOWED_HOSTS is configured'))
             score += 1
        else:
             self.stdout.write(self.style.ERROR('[FAIL] ALLOWED_HOSTS is empty or wildcard'))

        # Check 3: SESSION_COOKIE_SECURE
        total_checks += 1
        if getattr(settings, 'SESSION_COOKIE_SECURE', False):
             self.stdout.write(self.style.SUCCESS('[PASS] SESSION_COOKIE_SECURE is True'))
             score += 1
        else:
             self.stdout.write(self.style.ERROR('[FAIL] SESSION_COOKIE_SECURE is False (CRITICAL for NIS2)'))

        # Check 4: CSRF_COOKIE_SECURE
        total_checks += 1
        if getattr(settings, 'CSRF_COOKIE_SECURE', False):
             self.stdout.write(self.style.SUCCESS('[PASS] CSRF_COOKIE_SECURE is True'))
             score += 1
        else:
             self.stdout.write(self.style.WARNING('[WARN] CSRF_COOKIE_SECURE is False'))

        # Check 5: Password Validators
        total_checks += 1
        validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        if len(validators) >= 3:
             self.stdout.write(self.style.SUCCESS('[PASS] Password Validators seem strong'))
             score += 1
        else:
             self.stdout.write(self.style.WARNING(f'[WARN] Only {len(validators)} Password Validators configured'))

        self.stdout.write('------------------------------------------------')
        final_score = int((score / total_checks) * 100)
        self.stdout.write(f'COMPLIANCE SCORE: {final_score}/100')
        
        if final_score < 100:
            self.stdout.write(self.style.WARNING('Action Required: Fix the failed checks above.'))
