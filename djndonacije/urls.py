"""djndonacije URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import djnd_supporters
from djnd_supporters.views import AddSegmentContacts

admin.site.site_url = '/api/transaction-export/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('djnd_supporters.urls', 'djnd_supporters'), namespace='supporters')),
    path('tinymce/', include('tinymce.urls')),
    path('shop/', include('shop.urls')),
    path('api/shop/', include('shop.urls_api')),
    path('novicnik/<slug:slug>/', AddSegmentContacts.as_view(), name='add-segment-contacts'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
