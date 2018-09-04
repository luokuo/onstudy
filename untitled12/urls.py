"""untitled12 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
#from django.contrib import xadmin
import xadmin
from django.views.generic import  TemplateView
from user.views import UserLogin,RegisterView,ActiveUserView,ForgetPwd,ResetView,ModifyPwdView
from organization.views import OrgListView
from django.views.static import serve
from untitled12.settings import MEDIA_ROOT

from  message.views import getForm
from user.views import LogoutView

urlpatterns = [
    url(r'^admin/', xadmin.site.urls),
    url(r'^getform/', getForm,name="getform"),
    url(r'^media/(?P<path>.*)$',serve,{"document_root":MEDIA_ROOT}),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name="index"),
    url('^login/', UserLogin.as_view(), name='login'),
    url('^reg/', RegisterView.as_view(), name='reg'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/', ActiveUserView.as_view(),name='active'),
    url('^forget/', ForgetPwd.as_view(), name='forget'),
    url(r'^reset/(?P<active_code>.*)/', ResetView.as_view(),name='reset'),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),
    url(r'^org/', include('organization.urls',namespace='org')),
    url(r'^course/', include('course.urls',namespace='courses')),
    url(r'^user/', include('user.urls',namespace='users')),

    # 退出登录
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

]
