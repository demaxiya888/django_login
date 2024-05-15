import os
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives # HTML格式邮件方法导入

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_login.settings'

# 纯文本格式邮件
# if __name__ == '__main__':
#
#     send_mail(
#         '测试',
#         '测试django邮件发送',
#         'tjh20020910@163.com',
#         ['2936899439@qq.com'],
#     )

# HTML格式邮件
if __name__ == '__main__':

    # 邮件主题，邮件发送人，邮件收件人
    subject, from_email, to = 'HTML格式测试邮件', 'tjh20020910@163.com', '2936899439@qq.com'
    # text_content是用于当HTML内容无效时的替代txt文本
    text_content = 'HTML格式测试内容替换'
    # HTML内容的邮件内容
    html_content = '<p>欢迎访问<a href="http://www.test.com" target=blank>www.test.com</a>测试网站</p>'
    # 生成HTML邮件对象并发送
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()