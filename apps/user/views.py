from django.shortcuts import render
# 导入系统的方法 验证 登陆
from django.contrib.auth import authenticate, login, logout

from .models import UserProfile
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import UserProfile,EmailVerifyRecord

from .forms import LoginForm,RegisterForm,ForgetForm,ModifyPwdForm
from django.views.generic.base import View

from django.contrib.auth.hashers import make_password
from utils.email_send import send_register_email


from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from course.models import Course
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from django.http import HttpResponse, HttpResponsePermanentRedirect
from .forms import UserInfoForm,UploadImageForm

import json
from django.core.urlresolvers import reverse

# Create your views here.


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


'''
 用户登录
'''

#方法过去时
def user_login(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():  # 验证成功
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, "index.html")
            else:
                return render(request, "login.html", {"msg": u"用户名或密码错误"})
        else:
            return render(request, "login.html", {"login_form": login_form})

    elif request.method == "GET":
        print("11111")
        return render(request, "login.html", {})


class UserLogin(View):
    def get(self, request):
        print("11111")
        return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():  # 验证成功
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            user = authenticate(username=username, password=password)
            if user is not None:
               if user.is_active:
                    login(request, user)
                    return render(request, "index.html")
               else:
                   return render(request,'login.html',{"msg":"用户没有激活，请进入邮箱激活"})
            else:
                return render(request, "login.html", {"msg": u"用户名或密码错误"})
        else:
            return render(request, "login.html", {"login_form": login_form})


class RegisterView(View):
    def get(self, request):
        # get 请求的时候，把验证码组件一系列的 HTML render 到 register.html 里
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            email = request.POST.get('email', '')
            if UserProfile.objects.filter(email=email):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已经存在！'})
            password = request.POST.get('password', '')

            user_profile = UserProfile()
            user_profile.username = email
            user_profile.email = email
            user_profile.password = make_password(password)
            user_profile.is_active = False
            user_profile.save()
            send_register_email(email)
            return render(request, 'send_success.html')

        return render(request, 'register.html', {'register_form': register_form})


# 验证用户注册后，在邮件里点击注册链接
class ActiveUserView(View):
    def get(self, request, active_code):
        # 为什么用 filter ？ 因为用户可能注册了好多次，一个 email 对应了好多个 code
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for records in all_records:
                #查询邮箱
                email = records.email
                #查询userprofile里面对应用户
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
                return render(request, 'login.html')
        return render(request, 'active_fail.html')


'''
  忘记密码
'''

class ForgetPwd(View):
    def get(self,request):
        forget_form = ForgetForm()
        return  render(request,'forgetpwd.html',{"forget_form":forget_form})
    def post(self,request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            send_register_email(email, "forget")
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})



class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email":email})
        else:
            return render(request, "active_fail.html")



class ModifyPwdView(View):
    """
    修改用户密码
    """

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email": email, "msg": "密码不一致"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()

            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modify_form": modify_form})


# userprofile
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'usercenter-info.html')

    # 用户修改昵称，手机号，地址，生日
    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        res = dict()

        if user_info_form.is_valid():
            user_info_form.save()
            res['status'] = 'success'

        else:
            res = user_info_form.errors

        return HttpResponse(json.dumps(res), content_type='application/json')


# 用户修改头像
class UploadImageView(LoginRequiredMixin, View):
    def post(self, request):
        # image_form = UploadImageForm(request.POST, request.FILES)
        # if image_form.is_valid():
        #     image = image_form.cleaned_data['image']
        #     request.user.image = image
        #     request.user.save()
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        res = dict()
        if image_form.is_valid():
            image_form.save()
            res['status'] = 'success'
            res['msg'] = '头像修改成功'
        else:
            res['status'] = 'fail'
            res['msg'] = '头像修改失败'
        return HttpResponse(json.dumps(res), content_type='application/json')


#用户修改密码
# 用户在个人中心修改密码
class UpdatePwdView(LoginRequiredMixin, View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        res = dict()

        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                res['status'] = 'fail'
                res['msg'] = '两次密码不一致'
                return HttpResponse(json.dumps(res), content_type='application/json')

            user = request.user
            user.password = make_password(pwd2)
            user.save()

            res['status'] = 'success'
            res['msg'] = '密码修改成功'
        else:
            res = modify_form.errors

        return HttpResponse(json.dumps(res), content_type='application/json')


# 发送修改邮箱时的邮箱验证码
class SendEmailCodeView(LoginRequiredMixin, View):
    def get(self, request):
        email = request.GET.get('email', '')

        res = dict()
        if UserProfile.objects.filter(email=email):
            res['email'] = '邮箱已注册'
            return HttpResponse(json.dumps(res), content_type='application/json')
        send_register_email(email, 'update_email')
        res['status'] = 'success'
        res['msg'] = '发送验证码成功'
        return HttpResponse(json.dumps(res), content_type='application/json')


# 修改个人邮箱
class UpdateEmailView(LoginRequiredMixin, View):
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        res = dict()
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            res['status'] = 'success'
            res['msg'] = '邮箱修改成功！'
        else:
            res['status'] = 'fail'
            res['msg'] = '验证码出错！'

        return HttpResponse(json.dumps(res), content_type='application/json')


# 我的课程
class MyCourseView(LoginRequiredMixin, View):
    def get(self, request):
     user_courses = UserCourse.objects.filter(user=request.user)
     return render(request, 'usercenter-mycourse.html', {
         'user_courses': user_courses,
     })


# 我收藏的课程机构
class MyFavOrgView(LoginRequiredMixin, View):
    def get(self, request):
     org_list = []
     fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
     for fav_org in fav_orgs:
         org_id = fav_org.fav_id
         org = CourseOrg.objects.get(id=org_id)
         org_list.append(org)
     return render(request, 'usercenter-fav-org.html', {
         'org_list': org_list,
     })


# 我收藏的授课讲师
class MyFavTeacherView(LoginRequiredMixin, View):
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {
            'teacher_list': teacher_list,
        })


# 我收藏的课程
class MyFavCourseView(LoginRequiredMixin, View):
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {
            'course_list': course_list,
        })


#用户登出
class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponsePermanentRedirect(reverse('index'))


# 我的消息
class MyMessageView(LoginRequiredMixin, View):
    def get(self, request):
        # 如果 user = 0 ，代表全局消息，所有用户都能收到
        all_message = UserMessage.objects.filter(user=request.user.id)

        #进入到我的消息页面后，把已读的消息清空
        all_unread_message = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_message:
            unread_message.has_read = True
            unread_message.save()

        # 对个人消息分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_message, 2, request=request)
        messages = p.page(page)

        return render(request, 'usercenter-message.html', {
            'messages': messages,
        })
