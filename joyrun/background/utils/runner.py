from django.http import HttpResponse
from ..models import ProjectInfo, TestReports


def pybot_command(file_path, env='test'):
    '''
    生成 robot 命令  
    ``env``: 'test' 代表测试环境，'production' 代表生产环境
    '''

    project_path = ProjectInfo.objects.get(
        project_name='thejoyrunTestcode').file_path
    var_path = project_path + "\\Public\\JoyrunOnline_var.py"

    if env == 'test':
        command = "pybot --include Test  --variable  JoyrunEvn:Test    -d "
    elif env == 'production':
        command = "pybot --include Online  --variable  JoyrunEvn:Online -V {} -d ".format(
            var_path)
    else:
        return HttpResponse("It's something wrong")

    import subprocess, time, platform

    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()).split()
    date_num = start_time[0]
    clock_num = start_time[-1].replace(':', '-')
    
    if platform.system() == "Windows":
        report_path = 'C:\\Users\\ShadowMimosa\\Documents\\STU\Top\\ForDjango\\joyrun\\background\\reports\\' + date_num + '\\' + clock_num
    elif platform.system() == "Linux":
        report_path = './' + date_num + '/' + clock_num
    
    # setting 中变量并不可用
    # if DEBUG:
    #     print("Debug is here now!")
        
    subprocess.call(command + report_path + '\t' + file_path, shell=True)

    reports = {
        'report_name': int(time.time()),
        'status': 1,
        'successes': 1,
        'testsRun': 1,
        'start_at': start_time,
        'reports': report_path
    }
    TestReports.objects.create(**reports)
    pagenum = TestReports.objects.get(reports=report_path).id

    return pagenum
