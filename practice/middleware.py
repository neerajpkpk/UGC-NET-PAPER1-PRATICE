from django.http import HttpResponsePermanentRedirect


class RedirectRenderDomainMiddleware:
    """Permanently send the old Render hostname to the custom domain."""

    render_host = "ugc-net-paper1-pratice.onrender.com"
    custom_domain = "https://ugcnetprep.me"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.get_host().lower() == self.render_host:
            return HttpResponsePermanentRedirect(
                f"{self.custom_domain}{request.get_full_path()}"
            )
        return self.get_response(request)
