from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=128)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    gender = (
        ('male', '男'),
        ('female', '女'),
    )
    sex = models.CharField(max_length=32, choices=gender, default="男")
    c_time = models.DateTimeField(auto_now_add=True)
    # 是否已经邮件确认字段，布尔值
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-c_time"] # 最近创建的用户优先显示
        verbose_name = "用户"
        verbose_name_plural = "用户"

# 邮件确认注册相关信息存放模型
class ConfirmString(models.Model):
    code = models.CharField(max_length=256) # code字段是哈希后的注册码
    user = models.OneToOneField('User', on_delete=models.CASCADE) # 一对一关系
    c_time = models.DateTimeField(auto_now_add=True) # c_time是注册的提交时间

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"