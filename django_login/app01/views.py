from django.shortcuts import render, HttpResponse, redirect

# Create your views here.
from . import models
from . import forms
import hashlib
import datetime
from django.conf import settings

# 密码哈希加密
def hash_password(s, salt='app01'):# 加点盐，salt参数的app01是默认值，后续可以传递新参数值覆盖
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

def index(request):
    if not request.session.get('is_login', None):
        return  redirect('/app01/login/')

    return render(request, 'login/index.html')

# 登陆
def login(request):
    if request.session.get('is_login', None):
        return redirect('/app01/index/')

    if request.method == 'POST':
        login_form = forms.UserForm(request.POST)
        message = '验证码错误'
        if login_form.is_valid():
            print(login_form)
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            try:
                user = models.User.objects.get(name=username) # 不能用if来判断，get方法
            except:
                message = '用户不存在'
                return render(request, 'login/login.html', {'message':message, 'login_form':login_form})

            # 添加是否已经邮件确认验证
            if not user.has_confirmed:
                message = '用户还未经过邮件确认'
                return render(request, 'login/login.html', {'message':message, 'login_form':login_form})


            if hash_password(password) == user.password:
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/app01/index/')

            message = '密码错误'
            return render(request, 'login/login.html', {'message': message, 'login_form': login_form})

        return render(request, 'login/login.html', {'message': message, 'login_form': login_form})


    login_form = forms.UserForm()
    return render(request, 'login/login.html', {'login_form': login_form})

# 登出
def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/app01/login/")

    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect('/app01/login/')

# 注册
def register(request):
    # if request.session.get('is_login', None):
    #     return redirect('/app01/login/')

    if request.method == 'POST':
        message = '验证码错误'
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')

            if models.User.objects.filter(name=username):
                message = '用户已存在'
                return render(request, 'login/register.html', locals())

            if models.User.objects.filter(email=email):
                message = '邮箱已被注册'
                return render(request, 'login/register.html', locals())

            if password1 == password2:
                new_user = models.User.objects.create(name=username, password=hash_password(password1), email=email)

                code = make_confirm_string(new_user)
                send_email(email, code)

                message = '注册确认邮件已发送，请前往您的邮箱中确认'
                return render(request, 'login/confirm.html', locals())

            message = '两次密码输入不一致'
            return render(request, 'login/register.html', locals())

        return render(request, 'login/register.html', locals())

    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())

# 生成确认码
# # 接收一个用户对象作为参数
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 利用datetime模块生成一个当前时间的字符串now作为盐
    code = hash_password(user.name, now) # 以用户名为基础，now为‘盐’，生成一个独一无二的哈希值，使用的是前面密码哈希加密的函数
    models.ConfirmString.objects.create(code=code, user=user) # 生成并保存一个确认码对象
    return code # 返回哈希值加密确认码


# 发送确认邮件
def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives # 使用的是发送HTML格式的的函数

    subject = '注册确认邮件'
    text_content = ' 如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'

    html_content = '''
                    <p>这是注册确认邮件，<a href="http://{}/app01/confirm/?code={}" target=blank>点击此链接确认注册</a></p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
    # 127.0.0.1:8000表示本机，注意：http://{}/app01/confirm/?code={}这个路由
    # 这是我们编写处理注册邮件确认的路由，还需要编写相关的视图函数以及前端模板，里面的参数是code，即为确认码
    # 有效期天数为设置在settings中的CONFIRM_DAYS，我们需要自己设置，这里设置为1天
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# 处理邮件注册确认
# 发送确认邮件函数中的这个url，http://{}/app01/confirm/?code={}，注意code这个参数
def confirm(request):
    code = request.GET.get('code', None) # 从请求的url地址中获取确认码code
    message = ''
    try:
        # 尝试将获取到的code以get方法从模型中查看是否有对应的对象，有的话将对象赋值给confirm
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        # 没有的话输出错误信息
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())

    # 获取注册用户时的时间
    c_time = confirm.c_time
    now = datetime.datetime.now()
    # 将当前的时间与注册用户时的时间加上设定的有效时间对比
    # 如果当前时间大于，表示已经超过有效期
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        # 删除注册的用户，同时注册码也会一并删除，然后返回confirm.html页面，并提示
        confirm.user.delete()
        message = '注册确认邮件已经过期，请重新注册!'
        return render(request, 'login/confirm.html', locals())
    else:
        # 未超期，修改用户的has_confirmed字段为True，并保存，表示通过确认了。
        # 然后删除注册码，但不删除用户本身。最后返回confirm.html页面，并提示
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '注册确认成功，即将跳转至登陆页面'
        return render(request, 'login/confirm.html', locals())

# 重置密码
def reset_password(request):
    if request.method == 'POST':
        reset_form = forms.RetSetPasswordForm(request.POST)
        message = '验证码错误'
        if reset_form.is_valid():
            username = reset_form.cleaned_data.get('username')
            password1 = reset_form.cleaned_data.get('password1')
            password2 = reset_form.cleaned_data.get('password2')

            try:
                user = models.User.objects.filter(name=username)

            except:
                message = '用户不存在'
                return render(request, 'login/reset_password.html', locals())
            if password1 == password2:
                models.User.objects.filter(name=username).update(password=hash_password(password1))
                message = '密码修改成功，2秒后返回登陆页面'
                return render(request, 'login/reset_password.html', locals())

            message = '两次密码输入不一致'
            return render(request, 'login/reset_password.html', locals())

        return render(request, 'login/reset_password.html', locals())

    reset_form = forms.RetSetPasswordForm()
    return render(request, 'login/reset_password.html', locals())