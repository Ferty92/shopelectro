from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST


# Sets CSRF-cookie to CBVs.
set_csrf_cookie = method_decorator(ensure_csrf_cookie, name='dispatch')


@require_POST
def set_view_type(request):
    """Setting view type to user's session."""
    request.session['view_type'] = request.POST['view_type']
    return HttpResponse('ok')  # Return 200 OK
