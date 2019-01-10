from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def process(request, **kwargs):
    app = kwargs.pop('app', None)
    fun = kwargs.pop('function', None)
    index = kwargs.pop('pagenum', None)

    if app:
        app = 'background'
    elif fun:
        app = 'background'
    else:
        raise Exception

    try:
        app = __import__("%s.views" % app)
        view = getattr(app, 'views')
        fun = getattr(view, fun)

        # 执行view.py中的函数，并获取其返回值
        result = fun(request, index) if index else fun(request)
    except (ImportError, AttributeError):
        raise Exception

    return result
