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
    ec_symbol = 0  # ec 文件夹标记

    for root, dirs, files in os.walk(path):
        root_folder = root.split(symbol)[-1]

        if root == path:
            for index in dirs:
                if "git" not in index and "Public" not in index:
                    testcase[foldername][index] = {}

        elif len(root) > len(path):
            if root_folder == 'ec' and ec_symbol == 0:
                print(files)
                ec_symbol = 1

            if root_folder == 'ec' and ec_symbol == 1:
                pass
            elif root_folder in testcase[foldername].keys():
                if root_folder=='ec':
                    print(files)
                for values in files:
                    if 'init' in values or 'git' in values or '.txt' not in values:
                        files.remove(values)
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
        for keys, values in tests_all[key].items():

            folder = os.path.join(path, keys)
            if ModuleInfo.objects.get_module_name(keys) < 1:
                ModuleInfo.objects.insert_module(
                    module_name=keys,
                    test_user='Admin',
                    simple_desc='该模块测试用例集合',
                    belong_project=pro,
                    file_path=folder)
                print("Wrinting ModuleInfo of {} to database is down.".format(
                    keys))
            elif ModuleInfo.objects.get_module_name(keys) == 1:
                module = ModuleInfo.objects.get(module_name=keys)
                if module.file_path != folder:
                    module.folder_path = folder
                    module.save()
                    print("ModuleInfo of {} is update.".format(keys))

            mod = ModuleInfo.objects.get(module_name=keys)
            for index in values:
                files = os.path.join(folder, index)
                if TestCaseInfo.objects.filter(
                        belong_project=pro.project_name).filter(
                            belong_module_id=mod).filter(
                                name=index).count() < 1:
                    TestCaseInfo.objects.create(
                        name=index,
                        belong_project=pro.project_name,
                        author='Admin',
                        request='default',
                        belong_module=mod,
                        file_path=files)
                    print("Wrinting TestcaseInfo of {} to database is down.".
                          format(index))
                elif TestCaseInfo.objects.filter(name=index).count() == 1:
                    testcase = TestCaseInfo.objects.get(name=index)
                    if testcase.file_path != files:
                        testcase.file_path = files
                        testcase.save()
                        print("TestcaseInfo of {} is update".format(index))


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


[('thejoyrunTestcode', {
    'CrewAPI': [
        'crew-user-crew_Post.txt', 'crew-event-list_Post.txt',
        'crew-club-info_Post.txt', 'crew-search_Get.txt', 'crew-info_Post.txt',
        'crew-event-detail_Post.txt', 'crew-club-avg-rank-last-week_Post.txt',
        'crew-join-cancel_Post.txt', 'crew-discover_Post.txt',
        'crew-join-quit_Post.txt', 'crew-club-update_Post.txt',
        'crew-club-member_Post.txt', 'crew-recommend_Post.txt',
        'crew-club-avg-rank-week_Post.txt'
    ],
    'equipmentapi': [
        'saveUserCurrentEqpt_Post.txt', 'getUserEqptByType_Get.txt',
        'getUserCurrentEqpt_Get.txt'
    ],
    'marathonapi':
    ['marathon_online-mls-list_Post.txt', 'marathon_his-mls-list_Post.txt'],
    'wearapi': [
        'brand-shoe-search_Get.txt', 'user-shoe-meters-mark_Get.txt',
        'starting-shoe-list_Post.txt', 'brand-shoe-hot-tag_Get.txt',
        'shoe-multi-color-list_Get.txt', 'shoe-comment_Get.txt',
        'user-shoe-add_Get.txt', 'user-shoe-color-set_Get.txt',
        'user-shoe-retire_Get.txt', 'user-shoe-list_Post.txt',
        'brand-shoe-list-tag_Get.txt', 'user-shoe-delete_Get.txt',
        'brand-shoe-list_Post.txt', 'shoe-comment-pre-check_Get.txt',
        'brand-list_Post.txt', 'shoe-comment-eval_Get.txt',
        'user-shoe-remark-set_Get.txt', 'shoe-comment-list-hot_Post.txt',
        'user-shoe-detail_Get.txt', 'user-shoe-meters-set_Get.txt',
        'starting-shoe-detail_Get.txt', 'brand-shoe-detail_Post.txt',
        'user-shoe-meters-mark-info_Get.txt', 'user-shoe-size-set_Get.txt',
        'shoe-comment-list_Post.txt'
    ],
    'CrewappAPI': [
        'crew_app_event_list_Post.txt', 'crew_event_cancle_app_Post.txt',
        'crew-app-event-recommend-list_Post.txt',
        'crew_event_new_app_Post.txt', 'crew-event-join-app_Post.txt',
        'crew-event-detail-app_Get.txt'
    ],
    'beta':
    ['api_ios_dynamic_config_do_Post.txt', 'api_dynamic_config_do_Post.txt'],
    'eventapi': ['app_getUserEvents_Get.txt'],
    'searchapi': [
        'squareSearchByType_Get.txt', 'squareSearchByTypes_Get.txt',
        'squareSearchAgg_Get.txt'
    ],
    'topicapi': [
        'newTopic_topicDetail_Post.txt', 'newTopic_getBannerList_Get.txt',
        'newTopic_getSquareAndRunDynamicTopic_Get.txt',
        'newTopic_getChoicestArtideList_Get.txt',
        'newTopic_getFourTopicList_Get.txt',
        'newTopic_getHotsFeedList_Get.txt', 'newTopic_search_Get.txt',
        'newTopic_getHotsFeedList_Post.txt',
        'newTopic_getRunTopicConfigList_Get.txt',
        'newTopic_getTopicList_Post.txt'
    ],
    'raceliveapi': [
        'live_racesAndItems_Get.txt', 'live_race_recommend_Get.txt',
        'live_races_Get.txt', 'live_races_count_Get.txt',
        'live_raceItems_Get.txt', 'live_runner_Get.txt'
    ],
    'mediaapi': [
        'article-favor-add_Post.txt', 'article-get_Post.txt',
        'subject-list-v1_Post.txt', 'article-list-v1_Post.txt',
        'article-recommend-list_Post.txt', 'article-favor-list_Post.txt',
        'article-comment-list_Post.txt', 'article-comment-eval_Post.txt',
        'article-comment-list-hot_Post.txt', 'slide-list_Post.txt'
    ],
    'walletapi': [
        'wallet_listUserTransDetails_Get.txt',
        'wallet_withdrawRequest_Post.txt',
        'wallet_getUserBalanceAmount_Get.txt',
        'wallet_withdrawAccount_list_Get.txt',
        'wallet_withdrawAccount_delete.txt', 'wallet_codeVerify_Get.txt',
        'wallet_recharge_payResult_Get.txt', 'wallet_bind_post.txt',
        'wallet_withdrawAccount_bind_Post.txt'
    ],
    'challengeAPI': [
        'getActivity_Post.txt', 'challenge_list_Post.txt',
        'challengeuser_getCompleteUsers_Post.txt',
        'challenge_myChallenges_Get.txt',
        'challenge_getActivityForPersonalRank_Post.txt',
        'challengeuser_getCompleteUsersV2_Get.txt',
        'challenge_getCompleteActivity_Get.txt',
        'challengeuser_getAwardUsersV2_Get.txt',
        'challengeuser_isAwardUser_Get.txt',
        'challenge_getActivityInfo_Post.txt', 'challengeList_Get.txt',
        'sign_Post.txt'
    ],
    'webevent':
    ['weather_uv_Get.txt', 'weather_forecast_Get.txt', 'weather_air_Get.txt'],
    'integrate': [
        'register_Cell_Post.txt', 'updata_Run_record.txt',
        'userAdd_Del_shoe_Post.txt', 'class_partin_pay_Post.txt',
        'add_online_marathon_Get.txt', 'challengeuser_join_Post.txt',
        'class_sponsor_pay_post.txt', 'feed_post_run_Post.txt',
        'RunRecord_Online_Test.txt', 'run_delete_Post.txt'
    ],
    'AdvertAPI': [
        'advert-list_Post.txt', 'notify-list_Post.txt', 'hudong-list_Post.txt'
    ],
    'PointAPI': ['upnt-point-info_Post.txt'],
    'trainingdubbox': ['pay_Get.txt', 'voicetraining_list-finish_Post.txt'],
    'API': [
        'friend_aspx_Post.txt', 'friendFeedListv5_aspx_Post.txt',
        'dataMessages_Post.txt', 'runAppeal_incompleteCount_Get.txt',
        'userBlacklist_checkAndSync_Get.txt', 'feed_check_run_Get.txt',
        'race-calendar_race-search_Post.txt', 'run_update_coverImg_Post.txt',
        'run_best_Post.txt', 'user_login_phonecode_get.txt',
        'Run_SetPrivate_aspx_Post.txt', 'check_run_Post.txt',
        'runAppeal_appealedRunList_Get.txt', 'userusersetting_asp_Post.txt',
        'JoyRunMaster_Default_aspx_Post.txt', 'misc_geocoding_reverse_Get.txt',
        'po_aspx_Post.txt', 'regdevicetoken_aspx_Post.txt',
        'user_find_Get.txt', 'logout_aspx_Get.txt', 'weather_Post.txt',
        'validate_otp_Post.txt', 'race-calendar_race-list_Post.txt',
        'feedMessageList_Post.txt', 'validate_registered_Post.txt',
        'user_aspx_Post.txt', 'rank_aspx_Post.txt',
        'RunnerLevel_GetRunnerLevelDetail_aspx_Get.txt',
        'runAppeal_canAppealRunList_Get.txt', 'resetpwd_aspx_Post.txt',
        'daily_getDaily_Post.txt', 'user_userBrandLists_Get.txt',
        'feed_getFriendFeedImgs_Post.txt', 'Run_GetInfo_aspx_Post.txt',
        'userBlacklist_add_Post.txt', 'userInvitesv2_aspx_Post.txt',
        'weather_Get.txt', 'user_getlist_aspx_Post.txt', 'run_delete_Get.txt',
        'misc_sensitiveWords_check_Post.txt', 'video_getUploadSetting_Get.txt',
        'register_fast_Post.txt', 'feed_post_run_Post.txt',
        'phone_getVerificationCode_post.txt', 'usernote_aspx_Post.txt',
        'userRunList_aspx_Post.txt', 'Run_SetPublic_aspx_Post.txt',
        'misc_upload_addressBook_Post.txt', 'user_recommandUserBrands_Get.txt',
        'feedListv5_aspx_Post.txt', 'Social_GetFeedRemind_aspx_Post.txt',
        'user_runLevel_timeline_Post.txt', 'citywide_aspx_Post.txt',
        'feed_aspx_Post.txt', 'importPo_aspx_Post.txt',
        'CellVerification_getCellVerificationCode_aspx_Post.txt',
        'userBlacklist_remove_Post.txt', 'runLevel_timeline_Post.txt',
        'oneclickdetails_aspx_Get.txt', 'oneclickdetails_aspx_Post.txt',
        'runAppeal_add_Post.txt', 'userBlacklist_list_Get.txt',
        'misc_qrCodeProcess_Post.txt', 'feed_feedListBasicBulk_POST.txt',
        'feed_delete_Post.txt', 'feed_video_getUploadSetting_Post.txt',
        'feed_recommandFeedId_Get.txt'
    ],
    'recommendapi': [
        'link_from_invite_post.txt', 'recommend-users_Get.txt',
        'wallet_ad_Get.txt', 'recommend-crews_Get.txt',
        'push-user-cache_Get.txt'
    ],
    'mappapi': [
        'getRankByPage_Post.txt', 'getMemberRunCale_Post.txt',
        'wallet_getWalletByUid_Get.txt', 'bet_class_list_Post.txt',
        'user_my_mission_Get.txt', 'getMemberCrewInfos_Post.txt',
        'getMemberInfo_Post.txt', 'getMemberDayRank_Post.txt',
        'getListByPage_Post.txt', 'getMemberChampionCount_Post.txt',
        'user_class_info_Get.txt', 'class_detail_info_Get.txt',
        'getByUid_cover_Post.txt'
    ],
    'Demo': [
        'autotest.txt', 'Demo_Connect_Case.txt', 'Demo.txt', 'Demo_Get.txt',
        'Demo_Postp.txt', 'report.html', 'Demo_Postd.txt', 'Itchat.txt',
        'Demo_Get_nosign.txt', 'feedaddVideoPv.txt'
    ],
    'crew-muiltapi': [
        'structure_getUserCrewLevel_Post.txt',
        'crewRunStat_avgRunDistance_Get.txt', 'crew_crewApplyList_Post.txt',
        'crewCreateApply_cancelApply_Get.txt',
        'msgBoard_getMsgBoardList_Post.txt', 'getUserOnGoingApplyCrew_Get.txt',
        'msgBoard_publish_Post.txt', 'crewRunStat_avgCheckin_Get.txt',
        'structure-remove-Member_Post.txt',
        'crewCreateApply_newApply_Post.txt',
        'eventapp_crew-event-update-app_Post.txt',
        'crewRunStat_avgRunPace_Get.txt',
        'eventapp_crew-event-cancle-app_Post.txt',
        'eventapp_getCrewEventList_Post.txt',
        'crew_getUserOnGoingApplyCrew_Get.txt',
        'structure_removeCrewAssstantAdmin_Post.txt',
        'structure_removeNodeAdmin_Post.txt',
        'structure_setCrewAssstantAdmin_Post.txt',
        'user_getAllCrewMember_Get.txt', 'structure_memberManage_Post.txt',
        'structure_updateCrewNodeInfo_post.txt',
        'contribution_getUserWeekScore_Get.txt',
        'eventapp_crew-app-event-list_Get.txt', 'rank_member_Get.txt',
        'user_getNotCheckinList_Post.txt', 'structure_getCrewNode_Get.txt',
        'rank_week_index_Get.txt',
        'eventapp_crew-app-event-recommend-list_Get.txt',
        'eventapp_getNewCrewEventApp_Post.txt', 'rank_week_index_Post.txt',
        'crew_applyJoinCrew_Post.txt', 'structure_setNodeAdmin_Post.txt',
        'contribution_rank_Get.txt', 'structure_getMyCrewInfo_Post.txt',
        'eventapp_crew-event-new-app_Post.txt',
        'eventapp_crew-event-join-list-app_Get.txt',
        'crew_applyReview_Post.txt', 'crew_quitCrewLastMonth_Post.txt',
        'crewCreateApply_getUserLastApply_Get.txt',
        'user_getCheckinList_Post.txt',
        'crewRunStat_getCrewRunStatistics_Post.txt',
        'eventapp_crew-event-detail-app_Get.txt',
        'eventapp_crew-event-join-app_Post.txt',
        'structure_getCrewInfo_Post.txt',
        'contribution_getUserHistoryList_Post.txt',
        'structure_searchCrewInfo_post.txt', 'crew_bottomNodeList_Post.txt',
        'user_searchCrewMembers_Get.txt'
    ],
    'ec': {},
    'LiveApi': ['listOnlineLiveRace_Post.txt'],
    'RdApi': [
        'running_domain_apply_Post.txt', 'running_domain_detail_Post.txt',
        'domain_checkin_ranking_30days_Post.txt',
        'running_domain_disassociate_Post.txt',
        'running_domain_supportcity_post.txt', 'running_domain_feed_Post.txt',
        'running_domain_list_Post.txt', 'running_domain_getByRun_Post.txt',
        'domain_checkin_list_Post.txt'
    ],
    'uapi': [
        'run_available_task_Get.txt', 'badge_getBadgeTypeTabSort_Post.txt',
        'badge_getRecommendBdgBadge_Get.txt',
        'badge_getBadgeByTypeAndBusinessId_Post.txt',
        'badge_getRecentlyBadges_Post.txt',
        'user_checkRealNameVerification_Get.txt',
        'badge_getBadgeListByBadgeIds_Get.txt',
        'badge_getBadgeSecondTypeList_Post.txt',
        'badge_getBadgeListByUpdateTime_Post.txt',
        'user_run_currentweeks_Post.txt', 'badge_getALLBadgeList_Post.txt'
    ],
    'betapi': [
        'create_class_role_Get.txt', 'class_sponsorlist_Get.txt',
        'class_list_Get.txt', 'class_rank_Get.txt', 'class_feed_list_Get.txt',
        'Class_Create_Post.txt', 'user_partin_list_Get.txt',
        'order_pay_result_Get.txt', 'user_class_diploma_Get.txt',
        'stat_user_total_Get.txt', 'user_my_mission_Get.txt',
        'user_advance_graduate_Post.txt', 'user_create_class_role_Get.txt',
        'user_partin_listbytime_Get.txt', 'user_class_info_Get.txt',
        'class_detail_info_Get.txt'
    ],
    'tripapi': [
        'race_getRandomTripMotto_Get.txt', 'user_cancelSign_Post.txt',
        'user_getUserWantRace_Post.txt', 'user_downLike_Post.txt',
        'user_getUserInfo_Post.txt', 'race_listRaceHome_Get.txt',
        'race_reasonIdGetRace_Get.txt', 'user_getUserRaceRunCount_Post.txt',
        'race_getCategory_Get.txt', 'race_getHotComment_Get.txt',
        'user_addUserComment_Post.txt', 'user_updateUserComment_Post.txt',
        'race_getNewComment_Post.txt', 'user_getUserCommentAndRun_Post.txt',
        'user_judgeBanding_Post.txt', 'user_getUserCertainRaceWant_Post.txt',
        'user_addUserWant_Post.txt', 'race_searchVisitRankRace_Get.txt',
        'user_getUserRaceSignCount_Post.txt',
        'race_reasonRaceIdByCertification_Get.txt',
        'race_resonRaceIdGetEvent_Get.txt',
        'user_getUserCanBandingUser_Post.txt', 'user_ypBandingWx_Post.txt',
        'user_cancelWant_Post.txt', 'user_getUserRaceSign_Post.txt',
        'listRaceHome_Get.txt', 'user_addUserRaceSign_Post.txt',
        'race_getSearchParams_Get.txt', 'race_searchRecommendRankRace_Get.txt',
        'user_delUserRaceCommentsOrRun_Post.txt',
        'race_findUpcomingRace_Get.txt', 'user_getUserRaceNewComment_Post.txt',
        'user_upLike_Post.txt', 'race_searchScoreRankRace_Get.txt'
    ],
    'trainingapi': [
        'finishUserTrainPlanDetail_Post.txt', 'terminateTrainPlan_Post.txt',
        'saveUserVoiceTraining_Post.txt', 'joinUserTrainPlan_Post.txt',
        'listVoiceTrainingSectionWithPoints_Post.txt',
        'getPlanDetails_Post.txt',
        'listVoiceTrainingGroupByTrainingId_Post.txt',
        'getUserRepairTrainPlan_Post.txt', 'getUserHisPlanDetail_Post.txt',
        'showUserTrainPlanScheduling_Post.txt',
        'listVoicePackageByTrainingId_Post.txt',
        'getPlanCategoriesV2_Post.txt', 'listOnlineVoiceTraining_Post.txt',
        'deleteTrainPlanHis_Post.txt', 'repairUserTrainPlanDetai_Post.txt',
        'getUserProceedTrainPlan_Post.txt', 'getPlansByCategoryId_Post.txt',
        'getUserTrainPlanRunsByDateline_Post.txt',
        'getUserHisTrainPlans_Post.txt'
    ]
})]
