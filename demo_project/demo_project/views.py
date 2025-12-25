from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def home(request):
    return HttpResponse("<h1>NIS2 Shield Demo</h1><p>Welcome to the public area.</p>")

def spam(request):
    return HttpResponse("<h1>Spam Me!</h1><p>Refresh this page to test Rate Limiting.</p>")

@login_required
def protected(request):
    return HttpResponse("<h1>Protected Area</h1><p>You are logged in.</p>")

def mfa_verify(request):
    # Simulate MFA verification
    if request.method == 'POST':
        request.session['is_verified_mfa'] = True
        next_url = request.GET.get('next', '/admin/')
        return HttpResponse(f"<h1>MFA Verified!</h1><a href='{next_url}'>Continue</a>")
    return HttpResponse("<h1>MFA Verification Needed</h1><form method='post'><button>Verify MFA</button></form>")
