# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf import settings
from django.conf.urls import include, url
from django.views import static
from django.contrib.gis import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib.auth import views as auth_views

from realty import views


urlpatterns = [
    url("^", include("realty.urls")),
    url(r'^admin/', admin.site.urls),
    url(r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'), static.serve,
        kwargs={"document_root": settings.STATIC_ROOT}),
    # url("^", admin.site.urls)

    #login, logout
    # {'template_name': 'registration/login.html'}

    ######## uncomment these to create login/logout functionality
    # url(r'^login/$',auth_views.login, {'template_name': 'admin/login.html'}),
    # url(r'^logout/$',auth_views.logout),

    # url(r'^register/', views.signup),
]
