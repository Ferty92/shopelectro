from .config import SHOP


def shop(request):
    """
    Injects shop dict into request.

    Shop dict contains information about shop:
    emails, phones, API-integrations.
    """
    return {'shop': SHOP}