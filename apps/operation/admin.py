import  xadmin
from  .models import  UserMessage


class UserMessageAdmin(object):
     list_display ={'user','message','has_read'}

xadmin.site.register(UserMessage, UserMessageAdmin)


