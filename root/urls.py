from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve

from root.settings import ENVIRONMENT, MEDIA_ROOT, STATIC_ROOT
from src.core.handlers import (
    handler404, handler500
)

urlpatterns = []

""" HANDLERS ------------------------------------------------------------------------------------------------------- """
handler404 = handler404
handler500 = handler500

""" EXTERNAL REQUIRED APPS ----------------------------------------------------------------------------------------- """
urlpatterns += [
    path('admin/', admin.site.urls),
    path('whisper/', include('src.apps.whisper.urls')),
]

""" INTERNAL REQUIRED APPS ----------------------------------------------------------------------------------------- """
urlpatterns += [
    path('dashboard/', include('src.services.dashboard.urls', namespace='dashboard')),
    path('accounts/', include('src.services.accounts.urls', namespace='accounts')),
    path('finance/', include('src.services.finance.urls', namespace='finance')),
]

""" ALL AUTH URLS ------------------------------------------------------------------------------------------------------- """

urlpatterns += [
    path('accounts/signup/', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('accounts/', include('allauth.account.urls')),
]

""" STATIC AND MEDIA FILES ----------------------------------------------------------------------------------------- """
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

""" HOME -> LOGIN REDIRECT ------------------------------------------------------------------------------------------ """
urlpatterns += [
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]

""" DEVELOPMENT ONLY -------------------------------------------------------------------------------------------- """
if ENVIRONMENT != 'server':
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls"))
    ]
