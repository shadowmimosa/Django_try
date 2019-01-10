import logging, json, os
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import csrf_exempt

from background.models import UserInfo, ProjectInfo, ModuleInfo, TestCaseInfo, EnvInfo, TestReports, TestSuite
from .utils.operation import add_project_data, del_project_data
from .utils.common import project_info_logic, initial_testcase, set_filter_session, init_filter_session, case_info_logic, get_ajax_msg, judge_type, return_msg
from .utils.pagination import get_pager_info
from .utils.runner import pybot_command

logger = logging.getLogger()


def login_check(func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_status'):
            return HttpResponseRedirect(
                reverse('background:function', kwargs={'function': 'login'}))
        return func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'POST':
        account = request.POST.get('account')
        password = request.POST.get('password')
        check_status = 0

        if account == '' or password == '':
            return return_msg(request, '用户名或密码为空！')
        try:
            if '@thejoyrun.com' in account:
                user = UserInfo.objects.get(email=account)
                account_type = 1
            else:
                user = UserInfo.objects.get(username=account)
                account_type = 0
        except ObjectDoesNotExist:
            return return_msg(request, '用户名或邮箱不存在！')

        if check_password(password, user.password):
            if user.status:
                check_status = 1

        if check_status == 1:
            logger.info('{username} 登录成功'.format(username=account))
            request.session["login_status"] = True
            if account_type == 1:
                account = UserInfo.objects.get(email__exact=account).username
            request.session["now_account"] = account
            return HttpResponseRedirect(
                reverse('background:function', kwargs={'function': 'index'}))

        return return_msg(request, '用户名或密码错误！')

    if request.method == 'GET':
        return render(request, "background/login.html")


@login_check
def logout(request):
    """
    注销登录
    :param request:
    :return:
    """

    if request.method == 'GET':
        logger.info(
            '{username}退出'.format(username=request.session['now_account']))
        try:
            del request.session['now_account']
            del request.session['login_status']
            init_filter_session(request, type=False)
        except KeyError:
            logging.error('session invalid')
        return HttpResponseRedirect(
            reverse('background:function', kwargs={'function': 'login'}))


@csrf_exempt
def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.method == 'POST' and False:
        msg = "注册还不能用哈哈哈！登录请 @ShadowMimosa."
        ret = {"msg": msg}
        return render(request, "background/register.html", ret)

    if request.method == 'POST':
        account = request.POST.get('account')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')

        if UserInfo.objects.filter(username__exact=account).count():
            msg = "用户名已经注册！请尝试登陆或 @Shadowmimosa."
        elif UserInfo.objects.filter(email__exact=email).count():
            msg = "此邮箱已经注册！请尝试登陆或 @Shadowmimosa."
        elif '@thejoyrun.com' not in email:
            msg = "请使用工作邮箱！"
        elif password != repassword:
            msg = "两次输入的密码不相同！"
        else:
            password = make_password(password, None, 'pbkdf2_sha256')

            UserInfo.objects.insert_user(account, password, email)
            request.session["login_status"] = True
            request.session["now_account"] = account
            return HttpResponseRedirect(
                reverse('background:function', kwargs={'function': 'index'}))

        ret = {"msg": msg}
        return render(request, "background/register.html", ret)
    elif request.method == 'GET':
        return render(request, "background/register.html")


@login_check
def index(request):
    """
    首页
    :param request:
    :return:
    """
    project_length = ProjectInfo.objects.count()
    module_length = ModuleInfo.objects.count()
    test_length = TestCaseInfo.objects.filter(type__exact=1).count()
    suite_length = TestSuite.objects.count()

    total = {
        'pass': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 90, 60],
        'fail': [90, 80, 70, 60, 50, 40, 30, 20, 10, 0, 10, 40],
        'percent': [
            10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 11.0,
            20.0
        ]
    }
    # total = get_total_values()

    manage_info = {
        'project_length': project_length,
        'module_length': module_length,
        'test_length': test_length,
        'suite_length': suite_length,
        'account': request.session["now_account"],
        'total': total
    }

    init_filter_session(request)

    return render(request, 'background/index.html', manage_info)


@login_check
def project_list(request, pagenum=1):
    account = request.session["now_account"]

    filter_query = set_filter_session(request)
    pro_list = get_pager_info(ProjectInfo, filter_query, '/project_list/',
                              pagenum)
    manage_info = {
        'account': account,
        'project': pro_list[1],
        'page_list': pro_list[0],
        'info': filter_query,
        'sum': pro_list[2],
        'env': EnvInfo.objects.all().order_by('-create_time'),
        'project_all': ProjectInfo.objects.all().order_by('-update_time')
    }

    return render(request, 'background/project_list.html', manage_info)


@login_check
def module_list(request, pagenum=1):
    """
    模块列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]

    filter_query = set_filter_session(request)
    module_list = get_pager_info(ModuleInfo, filter_query, '/module_list/',
                                 pagenum)
    manage_info = {
        'account': account,
        'module': module_list[1],
        'page_list': module_list[0],
        'info': filter_query,
        'sum': module_list[2],
        'env': EnvInfo.objects.all().order_by('-create_time'),
        'project': ProjectInfo.objects.all().order_by('-update_time')
    }
    return render(request, 'background/module_list.html', manage_info)


@login_check
def testcase_list(request, pagenum=1):
    """
    用例列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]

    filter_query = set_filter_session(request)
    test_list = get_pager_info(TestCaseInfo, filter_query, '/testcase_list/',
                               pagenum)
    manage_info = {
        'account': account,
        'test': test_list[1],
        'page_list': test_list[0],
        'info': filter_query,
        'env': EnvInfo.objects.all().order_by('-create_time'),
        'project': ProjectInfo.objects.all().order_by('-update_time')
    }
    return render(request, 'background/testcase_list.html', manage_info)


@login_check
def add_case(request):
    """
    新增用例
    :param request:
    :return:
    """
    account = request.session["now_account"]
    if request.is_ajax():
        testcase_info = json.loads(request.body.decode('utf-8'))
        msg = case_info_logic(**testcase_info)
        return HttpResponse(get_ajax_msg(msg, '/testcase_list/1/'))
    elif request.method == 'GET':
        manage_info = {
            'account':
            account,
            'project':
            ProjectInfo.objects.all().values('project_name').order_by(
                '-create_time')
        }
        return render(request, 'background/add_case.html', manage_info)


@login_check
def build_report():
    pass


@login_check
def run_test(request):
    if request.method == 'POST':

        kwargs = judge_type(request.POST.copy())

        index = kwargs[0].get('id')
        env_name = kwargs[1]
        run_type = kwargs[2].get(id=index)

        pagenum = pybot_command(run_type.file_path, env=env_name)

        return HttpResponseRedirect(
            reverse(
                'background:pagenum',
                kwargs={
                    'function': 'report_check',
                    'pagenum': pagenum
                }))


@login_check
def run_batch_test(request):

    kwargs = request.POST.copy()
    kwargs = judge_type(request.POST.copy())

    obj = kwargs[0]
    env_name = kwargs[1]
    run_type = kwargs[2]

    file_path = ''

    for value in obj.values():

        file_path += run_type.get(id=value).file_path
        file_path += '\t'

    pagenum = pybot_command(file_path, env=env_name)

    return HttpResponseRedirect(
        reverse(
            'background:pagenum',
            kwargs={
                'function': 'report_check',
                'pagenum': pagenum
            }))


@login_check
def report_check(request, pagenum):

    folder_name = TestReports.objects.get(id=pagenum).reports

    if 'report_check' and 'log.html' in request.get_full_path():
        file_name = folder_name + "\\log.html"
    else:
        file_name = folder_name + "\\report.html"

    def readFile(fn, buf_size=262144):
        print(os.getcwd())
        f = open(fn, "rb")
        while True:
            c = f.read(buf_size)
            if c:
                yield c
            else:
                break
        f.close()

    return HttpResponse(readFile(file_name))


def image(request):

    return HttpResponse("You're in my heart")
    return render(request, 'background/image.html')


# 测试用例路径
# path = 'D:\\test\\JoyrunTestOA\\thejoyrunTestcode'
# initial_testcase(os.path.relpath(path))

path = './background/thejoyrunTestcode'
initial_testcase(os.path.abspath(path))

print("---> It's in initial database now.")
