1. 进入项目的根目录，终端运行pip install -r requirements.txt下载所有依赖的库
2. 打开settings_example文件，修改DATABASE数据库相关参数（自己使用哪个数据库，确保使用的数据库已经创建），邮件发送相关参数后，将其重命名为settings
3. 终端运行python manage.py migrate同步操作到数据库中
4. 终端运行python manage.py runserver运行项目
   
