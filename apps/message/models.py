from django.db import models

# Create your models here.
class UserMessage(models.Model):
    name = models.CharField(max_length=20,null=True,blank=True,default="")
    email = models.EmailField(max_length=30,verbose_name='邮箱')
    address =models.CharField(max_length=100,verbose_name='地址')
    message =models.CharField(max_length=500,verbose_name='信息')

    class Meta:
        verbose_name = "留言版"
        verbose_name_plural = verbose_name
