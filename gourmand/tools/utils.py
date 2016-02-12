from django.conf import settings


def show_toolbar(request):
    if settings.DEBUG or request.user.is_superuser:
        debug = request.GET.get("debug", None)
        if debug == "on":
            request.session["debug"] = True
        elif debug == "off" and "debug" in request.session:
            del request.session["debug"]
        return "debug" in request.session
