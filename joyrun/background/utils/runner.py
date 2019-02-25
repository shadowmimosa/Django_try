from django.http import HttpResponse
from ..models import ProjectInfo, TestReports


def pybot_command(file_path, env='test'):
    '''
    生成 robot 命令  
    ``env``: 'test' 代表测试环境，'production' 代表生产环境
    '''

    project_path = ProjectInfo.objects.get(
        project_name='thejoyrunTestcode').file_path
    var_path = project_path + "/Public/JoyrunOnline_var.py"

    if env == 'test':
        command = "pybot --include Test  --variable  JoyrunEvn:Test    -d "
    elif env == 'production':
        command = "pybot --include Online  --variable  JoyrunEvn:Online -V {} -d ".format(
            var_path)
    else:
        return HttpResponse("It's something wrong")

    import subprocess, time, platform, os

    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()).split()
    date_num = start_time[0]
    clock_num = start_time[-1].replace(':', '-')

    from background.utils import global_varibale as gl

    if gl.get_value("system") == "Windows":
        symbol = "\\"
        rootpath = str(os.getcwd())
        report_path = rootpath + "\\background\\reports\\{}\\{}".format(
            date_num, clock_num)
    else:
        symbol = "/"
        report_path = '/home/apps/reports/' + date_num + '/' + clock_num
    print("--->{}".format(file_path))
    print("--->{}".format(file_path.split("thejoyrunTestcode")[0]))

    # subprocess.call(command + report_path + '\t' + file_path, shell=True)

    run_path = os.path.join(
        file_path.split("thejoyrunTestcode")[0],
        "thejoyrunTestcode{}Run.py".format(symbol))
    new_command = "python {} {} {} {}".format(
        run_path,
        env,
        file_path,
        report_path,
    )
    # subprocess.call(
    #     "sudo /home/apps/.local/share/virtualenvs/joyrun-s4DpRjB1/bin/activate",
    #     shell=True)
    subprocess.call("source /opt/py3.6/bin/activate")
    subprocess.call(new_command, shell=True)
    subprocess.call("deactivate")

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
