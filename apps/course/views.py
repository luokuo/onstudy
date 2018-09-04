from django.shortcuts import render
from django.views.generic.base import View
from .models import Course,CourseResource,Video
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from django.db.models import Q

from operation.models import UserFavorite, UserCourse, CourseComments

from django.http import HttpResponse,JsonResponse
import json


class CourseListView(View):
    def get(self, request):
        # 获取课程
        all_courses = Course.objects.all().order_by("-add_time")
        # 获取热门的
        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        # 课程搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(
                Q(name__icontains=search_keywords) |
                Q(desc__icontains=search_keywords) |
                Q(detail__icontains=search_keywords)
            )
        # 课程排序
        sort = request.GET.get('sort', '')
        if sort == 'students':
            all_courses = all_courses.order_by('-students')
        elif sort == 'hot':
            all_courses = all_courses.order_by('-click_nums')
        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 3, request=request)
        courses = p.page(page)

        return render(request, 'course-list.html', {
            'all_courses': courses,
            'hot_courses': hot_courses,
            'sort': sort,
        })


# 课程详情
class CourseDetailView(View):
    def get(self, request, course_id):
        #  username = request.GET.get("username") #获取浏览器过来的值
        course = Course.objects.get(id=int(course_id))  # 和数据库打交道的

        # 课程点击数 + 1
        course.click_nums += 1
        course.save()

        # 找到相关课程
        tag = course.tag
        relate_courses = []
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:2]

        # 课程/机构收藏
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
        })


# 课程信息
class CourseInfoView(View):
    def get(self, request, course_id):
        # 1获取课程id对应的课程
        course = Course.objects.get(id=int(course_id))
        # 2.课程里面学习人数+1
        course.students += 1
        course.save()
        # 3.查询用户是否学习该课程
        user_couses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_couses:
            user_couses = UserCourse(user=request.user,course=course)
            user_couses.save()

        #所有用户的id
        user_couseses = UserCourse.objects.filter(course=course)
        user_ids =  [user_couse.user.id for user_couse in user_couseses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [ user_couse.course.id for user_couse in  all_user_courses]
        relate_courses =  Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:3]

         #查询所有的资源
        all_resources = CourseResource.objects.filter(course=course)


        return  render(request,'course-video.html',{
            'course':course,
            'relate_courses':relate_courses,
            'all_resources':all_resources,

        })


# 课程评论
class CommentView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course)

        # 得出学过该课程的同学还学过的课程
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        return render(request, 'course-comment.html', {
            'course': course,
            'all_comments': all_comments,
            'all_resources': all_resources,
            'relate_courses': relate_courses,
        })


class AddCommentView(View):
    def post(self,request):
        res = dict()
        #判断用户登录
        if not request.user.is_authenticated():
            res['status'] = 'fail'
            res['msg'] = '用户未登录'
            return HttpResponse(json.dumps(res), content_type='application/json')

        #获取课程id
        course_id= int(request.POST.get('course_id',0))
        #获取评论
        comments = request.POST.get('comments','')

        if course_id and comments:
            course_comments = CourseComments()
            course_comments.course = Course.objects.get(id=course_id)
            course_comments.user = request.user
            course_comments.comments = comments
            course_comments.save()
            res['status'] = 'success'
            res['msg'] = '添加成功'
        else:
            res['status'] = 'fail'
            res['msg'] = '添加失败'
        return HttpResponse(json.dumps(res), content_type='application/json')


class VideoPlayView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        # 2.课程里面学习人数+1
        course.students += 1
        course.save()
        # 3.查询用户是否学习该课程
        user_couses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_couses:
            user_couses = UserCourse(user=request.user,course=course)
            user_couses.save()

        #所有用户的id
        user_couseses = UserCourse.objects.filter(course=course)
        user_ids =  [user_couse.user.id for user_couse in user_couseses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [ user_couse.course.id for user_couse in  all_user_courses]
        relate_courses =  Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:3]

         #查询所有的资源
        all_resources = CourseResource.objects.filter(course=course)


        return  render(request,'video-play.html',{
            'course':course,
            'relate_courses':relate_courses,
            'all_resources':all_resources,
            'video': video,

        })

