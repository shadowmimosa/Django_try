import os

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from .operation import add_project_data, add_case_data
from ..models import ProjectInfo, ModuleInfo, TestCaseInfo


def get_testcase(path):
    import collections
    from background.utils import global_varibale as gl

    if gl.get_value("system") == "Windows":
        symbol = "\\"
    else:
        symbol = "/"

    testcase = collections.OrderedDict()  # 初始化用例集合
    foldername = path.split(symbol)[-1]  # 用例文件夹名
    testcase[foldername] = {}  # 用例集合

    for root, dirs, files in os.walk(path):
        root_folder = root.split(symbol)[-1]

        if root == path:
            for index in dirs:
                if 'git' not in index:
                    testcase[foldername][index] = {}

        elif len(root) > len(path):
            if root_folder in testcase[foldername].keys():
                testcase[foldername][root_folder] = files

    print("---> Finding testcases is down. The json is {}".format(testcase))

    return testcase


def newly_testcase(tests_all, path):
    for key in tests_all:
        root = os.path.join(path)
        if ProjectInfo.objects.get_pro_name(key) < 1:
            ProjectInfo.objects.insert_project(
                project_name=key,
                submitted_personnel='Admin',
                simple_desc='接口测试项目',
                file_path=root)
            print("Wrinting ProjectInfo to database is down.")
        elif ProjectInfo.objects.get_pro_name(key) == 1:
            pro = ProjectInfo.objects.get(project_name=key)
            if pro.file_path != root:
                pro.file_path = root
                pro.save()
                print("ProjectInfo is update.")

        pro = ProjectInfo.objects.get(project_name=key)
        for keys, values in tests_all[key].items() and 'Public' not in keys:
            folder = os.path.join(path, keys)
            if ModuleInfo.objects.get_module_name(keys) < 1:
                ModuleInfo.objects.insert_module(
                    module_name=keys,
                    test_user='Admin',
                    simple_desc='该模块测试用例集合',
                    belong_project=pro,
                    file_path=folder)
                print("Wrinting ModuleInfo to database is down.")
            elif ModuleInfo.objects.get_module_name(keys) == 1:
                module = ModuleInfo.objects.get(module_name=keys)
                if module.file_path != folder:
                    module.folder_path = folder
                    module.save()
                    print("ModuleInfo is update.")

            mod = ModuleInfo.objects.get(module_name=keys)
            for index in values:
                files = os.path.join(folder, index)
                if TestCaseInfo.objects.filter(
                        belong_project=pro.project_name
                ).filter(belong_module_id=mod).filter(name=index).count(
                ) < 1 and 'init' not in index and 'git' not in index and '.txt' in index:
                    TestCaseInfo.objects.create(
                        name=index,
                        belong_project=pro.project_name,
                        author='Admin',
                        request='default',
                        belong_module=mod,
                        file_path=files)
                    print("Wrinting TestcaseInfo to database is down.")
                elif TestCaseInfo.objects.filter(name=index).count() == 1:
                    testcase = TestCaseInfo.objects.get(name=index)
                    if testcase.file_path != files:
                        testcase.file_path = files
                        testcase.save()
                        print("TestcaseInfo is update")


def update_testcase():
    pass


def initial_testcase(path):
    tests_all = get_testcase(path)
    newly_testcase(tests_all, path)
    update_testcase()


def project_info_logic(type=True, **kwargs):
    """
    项目信息逻辑处理
    :param type: boolean:True 默认新增项目
    :param kwargs: dict: 项目信息
    :return:
    """
    if kwargs.get('project_name') is '':
        return '项目名称不能为空'
    if kwargs.get('responsible_name') is '':
        return '负责人不能为空'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    if kwargs.get('dev_user') is '':
        return '开发人员不能为空'
    if kwargs.get('publish_app') is '':
        return '发布应用不能为空'

    return add_project_data(type, **kwargs)


def init_filter_session(request, type=True):
    """
    init session
    :param request:
    :return:
    """
    if type:
        request.session['user'] = ''
        request.session['name'] = ''
        request.session['project'] = 'All'
        request.session['module'] = '请选择'
        request.session['report_name'] = ''
    else:
        del request.session['user']
        del request.session['name']
        del request.session['project']
        del request.session['module']
        del request.session['report_name']


def set_filter_session(request):
    """
    update session
    :param request:
    :return:
    """
    if 'user' in request.POST.keys():
        request.session['user'] = request.POST.get('user')
    if 'name' in request.POST.keys():
        request.session['name'] = request.POST.get('name')
    if 'project' in request.POST.keys():
        request.session['project'] = request.POST.get('project')
    if 'module' in request.POST.keys():
        try:
            request.session['module'] = ModuleInfo.objects.get(
                id=request.POST.get('module')).module_name
        except Exception:
            request.session['module'] = request.POST.get('module')
    if 'report_name' in request.POST.keys():
        request.session['report_name'] = request.POST.get('report_name')

    filter_query = {
        'user': request.session['user'],
        'name': request.session['name'],
        'belong_project': request.session['project'],
        'belong_module': request.session['module'],
        'report_name': request.session['report_name']
    }

    return filter_query


def update_include(include):
    for i in range(0, len(include)):
        if isinstance(include[i], dict):
            id = include[i]['config'][0]
            source_name = include[i]['config'][1]
            try:
                name = TestCaseInfo.objects.get(id=id).name
            except ObjectDoesNotExist:
                name = source_name + '_已删除!'
                # logger.warning(
                #     '依赖的 {name} 用例/配置已经被删除啦！！'.format(name=source_name))

            include[i] = {'config': [id, name]}
        else:
            id = include[i][0]
            source_name = include[i][1]
            try:
                name = TestCaseInfo.objects.get(id=id).name
            except ObjectDoesNotExist:
                name = source_name + ' 已删除'
                # logger.warning(
                #     '依赖的 {name} 用例/配置已经被删除啦！！'.format(name=source_name))

            include[i] = [id, name]

    return include


def type_change(type, value):
    """
    数据类型转换
    :param type: str: 类型
    :param value: object: 待转换的值
    :return: ok or error
    """
    try:
        if type == 'float':
            value = float(value)
        elif type == 'int':
            value = int(value)
    except ValueError:
        # logger.error('{value}转换{type}失败'.format(value=value, type=type))
        return 'exception'
    if type == 'boolean':
        if value == 'False':
            value = False
        elif value == 'True':
            value = True
        else:
            return 'exception'
    return value


def key_value_list(keyword, **kwargs):
    """
    dict change to list
    :param keyword: str: 关键字标识
    :param kwargs: dict: 待转换的字典
    :return: ok or tips
    """
    if not isinstance(kwargs, dict) or not kwargs:
        return None
    else:
        lists = []
        test = kwargs.pop('test')
        for value in test:
            if keyword == 'setup_hooks':
                if value.get('key') != '':
                    lists.append(value.get('key'))
            elif keyword == 'teardown_hooks':
                if value.get('value') != '':
                    lists.append(value.get('value'))
            else:
                key = value.pop('key')
                val = value.pop('value')
                if 'type' in value.keys():
                    type = value.pop('type')
                else:
                    type = 'str'
                tips = '{keyword}: {val}格式错误,不是{type}类型'.format(
                    keyword=keyword, val=val, type=type)
                if key != '':
                    if keyword == 'validate':
                        value['check'] = key
                        msg = type_change(type, val)
                        if msg == 'exception':
                            return tips
                        value['expected'] = msg
                    elif keyword == 'extract':
                        value[key] = val
                    elif keyword == 'variables':
                        msg = type_change(type, val)
                        if msg == 'exception':
                            return tips
                        value[key] = msg
                    elif keyword == 'parameters':
                        try:
                            if not isinstance(eval(val), list):
                                return '{keyword}: {val}格式错误'.format(
                                    keyword=keyword, val=val)
                            value[key] = eval(val)
                        except Exception:
                            # logging.error('{val}->eval 异常'.format(val=val))
                            return '{keyword}: {val}格式错误'.format(
                                keyword=keyword, val=val)

                lists.append(value)
        return lists


def key_value_dict(keyword, **kwargs):
    """
    字典二次处理
    :param keyword: str: 关键字标识
    :param kwargs: dict: 原字典值
    :return: ok or tips
    """
    if not isinstance(kwargs, dict) or not kwargs:
        return None
    else:
        dicts = {}
        test = kwargs.pop('test')
        for value in test:
            key = value.pop('key')
            val = value.pop('value')
            if 'type' in value.keys():
                type = value.pop('type')
            else:
                type = 'str'

            if key != '':
                if keyword == 'headers':
                    value[key] = val
                elif keyword == 'data':
                    msg = type_change(type, val)
                    if msg == 'exception':
                        return '{keyword}: {val}格式错误,不是{type}类型'.format(
                            keyword=keyword, val=val, type=type)
                    value[key] = msg
                dicts.update(value)
        return dicts


def load_modules(**kwargs):
    """
    加载对应项目的模块信息，用户前端ajax请求返回
    :param kwargs:  dict：项目相关信息
    :return: str: module_info
    """
    belong_project = kwargs.get('name').get('project')
    module_info = ModuleInfo.objects.filter(belong_project__project_name=belong_project) \
        .values_list('id', 'module_name').order_by('-create_time')
    module_info = list(module_info)
    string = ''
    for value in module_info:
        string = string + str(value[0]) + '^=' + value[1] + 'replaceFlag'
    return string[:len(string) - 11]


def load_cases(type=1, **kwargs):
    """
    加载指定项目模块下的用例
    :param kwargs: dict: 项目与模块信息
    :return: str: 用例信息
    """
    belong_project = kwargs.get('name').get('project')
    module = kwargs.get('name').get('module')
    if module == '请选择':
        return ''
    case_info = TestCaseInfo.objects.filter(belong_project=belong_project, belong_module=module, type=type). \
        values_list('id', 'name').order_by('-create_time')
    case_info = list(case_info)
    string = ''
    for value in case_info:
        string = string + str(value[0]) + '^=' + value[1] + 'replaceFlag'
    return string[:len(string) - 11]


def case_info_logic(type=True, **kwargs):
    """
    用例信息逻辑处理以数据处理
    :param type: boolean: True 默认新增用例信息， False: 更新用例
    :param kwargs: dict: 用例信息
    :return: str: ok or tips
    """
    test = kwargs.pop('test')
    '''
        动态展示模块
    '''
    if 'request' not in test.keys():
        type = test.pop('type')
        if type == 'module':
            return load_modules(**test)
        elif type == 'case':
            return load_cases(**test)
        else:
            return load_cases(type=2, **test)

    else:
        # logging.info('用例原始信息: {kwargs}'.format(kwargs=kwargs))
        if test.get('name').get('case_name') is '':
            return '用例名称不可为空'
        if test.get('name').get('module') == '请选择':
            return '请选择或者添加模块'
        if test.get('name').get('project') == '请选择':
            return '请选择项目'
        if test.get('name').get('project') == '':
            return '请先添加项目'
        if test.get('name').get('module') == '':
            return '请添加模块'

        name = test.pop('name')
        test.setdefault('name', name.pop('case_name'))

        test.setdefault('case_info', name)

        validate = test.pop('validate')
        if validate:
            validate_list = key_value_list('validate', **validate)
            if not isinstance(validate_list, list):
                return validate_list
            test.setdefault('validate', validate_list)

        extract = test.pop('extract')
        if extract:
            test.setdefault('extract', key_value_list('extract', **extract))

        request_data = test.get('request').pop('request_data')
        data_type = test.get('request').pop('type')
        if request_data and data_type:
            if data_type == 'json':
                test.get('request').setdefault(data_type, request_data)
            else:
                data_dict = key_value_dict('data', **request_data)
                if not isinstance(data_dict, dict):
                    return data_dict
                test.get('request').setdefault(data_type, data_dict)

        headers = test.get('request').pop('headers')
        if headers:
            test.get('request').setdefault(
                'headers', key_value_dict('headers', **headers))

        variables = test.pop('variables')
        if variables:
            variables_list = key_value_list('variables', **variables)
            if not isinstance(variables_list, list):
                return variables_list
            test.setdefault('variables', variables_list)

        parameters = test.pop('parameters')
        if parameters:
            params_list = key_value_list('parameters', **parameters)
            if not isinstance(params_list, list):
                return params_list
            test.setdefault('parameters', params_list)

        hooks = test.pop('hooks')
        if hooks:

            setup_hooks_list = key_value_list('setup_hooks', **hooks)
            if not isinstance(setup_hooks_list, list):
                return setup_hooks_list
            test.setdefault('setup_hooks', setup_hooks_list)

            teardown_hooks_list = key_value_list('teardown_hooks', **hooks)
            if not isinstance(teardown_hooks_list, list):
                return teardown_hooks_list
            test.setdefault('teardown_hooks', teardown_hooks_list)

        kwargs.setdefault('test', test)
        return add_case_data(type, **kwargs)


def get_ajax_msg(msg, success):
    """
    ajax提示信息
    :param msg: str：msg
    :param success: str：
    :return:
    """
    return success if msg is 'ok' else msg


def judge_type(kwargs):

    env_name = kwargs.pop('env_name').pop(0)
    try:
        run_type = kwargs.pop('type').pop(0)
    except KeyError:
        run_type = None

    # 如果运行环境为空，则默认为 test
    if not env_name:
        env_name = 'test'
    # 如果运行类型为空，则默认为 用例
    if not run_type:
        run_type = 'test'

    run_type = obj_type(run_type)

    L = [kwargs, env_name, run_type]
    return L


def obj_type(run_type):

    if run_type == 'test':
        return TestCaseInfo.objects
    elif run_type == 'module':
        return ModuleInfo.objects
    elif run_type == 'project':
        return ProjectInfo.objects


def return_msg(request, msg):

    # logger.info('{username} 登录失败, 请检查用户名或者密码'.format(username=account))
    request.session["login_status"] = False
    ret = {"msg": msg}
    return render(request, "background/login.html", ret)
