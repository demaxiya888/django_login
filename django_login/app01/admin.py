from django.contrib import admin

# Register your models here.
# 用户名：admin 密码：y
from . import models

admin.site.register(models.User)
admin.site.register(models.ConfirmString)
