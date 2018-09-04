from django.shortcuts import render

from .models import UserMessage

# Create your views here.


def getForm(request):

    if request.method == "POST": # post get
        name = request.POST.get('name', '') #
        message = request.POST.get('message', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')

        user_message = UserMessage()
        user_message.name = name
        user_message.message = message
        user_message.email = email
        user_message.address = address

        user_message.save()

        user_message = UserMessage.objects.all().filter(name='张长志',email='2@qq.com')

        return render(request, "index.html", {})
    elif request.method == "GET":
        return render(request, "index.html", {})

#增加
def insert(request):
    user_message = UserMessage()
    user_message.name ="尚硅谷"
    user_message.message="在尚硅谷学习python"
    user_message.object_id="1"
    user_message.email="2@qq.com"
    user_message.address="bj"
    user_message.save()


def getform1(request):
    # 1.增加
    insert(request)



    # 2.按照条件查询 打印

    # 3.查询结构加上名字111

    # 4.回显

    return render(request,'index.html',{})
