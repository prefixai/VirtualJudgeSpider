import time

from spider.src.config import Problem, Result

supports = [
    'Aizu',
    'HDU',
    'FZU',
    'POJ',
    'WUST',
    'ZOJ',
    'Codeforces'
]


class OJBuilder(object):
    @staticmethod
    def build_oj(name, *args, **kwargs):
        if name:
            try:
                module_meta = __import__(f'src.platforms.{str(name).lower()}', globals(), locals(), [name])
                class_meta = getattr(module_meta, name)
                oj = class_meta(*args, **kwargs)
                return oj
            except ModuleNotFoundError:
                print(name, 'NOT SUPPORT')
        return None


class Core(object):
    def __init__(self, oj_name, proxies=None, timeout=5):
        self._remote_oj = oj_name
        self._oj = OJBuilder.build_oj(oj_name, proxies=proxies, timeout=timeout)

    @staticmethod
    def _space_and_enter_strip(data):
        if data:
            return str(data).strip(' ').strip('\r\n').strip(' ')

    # 获取支持的OJ列表
    @staticmethod
    def get_supports():
        return supports

    # 判断当前是否支持
    @staticmethod
    def is_support(oj_name):
        return oj_name in supports

    def get_home_page_url(self):
        if not self._oj:
            return None
        return self._oj.home_page_url()

    def get_cookies(self):
        if not self._oj:
            return None
        return self._oj.get_cookies()

    # 获取题面
    def get_problem(self, pid, account, **kwargs):
        if not self._oj:
            problem = Problem()
            problem.remote_oj = self._remote_oj
            problem.remote_id = pid
            problem.status = Problem.Status.STATUS_OJ_NOT_EXIST
            return problem
        self._oj.set_cookies(account.cookies)
        problem = self._oj.get_problem(pid=pid, account=account, **kwargs)
        problem.title = Core._space_and_enter_strip(problem.title)
        problem.time_limit = Core._space_and_enter_strip(problem.time_limit)
        problem.memory_limit = Core._space_and_enter_strip(problem.memory_limit)
        return problem

    # 提交代码
    def submit_code(self, pid, account, code, language, **kwargs):
        if not self._oj:
            return None
        self._oj.set_cookies(account.cookies)
        if self._oj.submit_code(account=account, code=code, language=language, pid=pid, **kwargs):
            time.sleep(2)
            return self.get_result(account=account, pid=pid, **kwargs)
        else:
            return Result(Result.VerdictCode.VERDICT_SUBMIT_FAILED)

    # 获取结果
    def get_result(self, account, pid, **kwargs):

        if not self._oj:
            return Result(Result.VerdictCode.VERDICT_SUBMIT_FAILED)
        self._oj.set_cookies(account.cookies)
        result = self._oj.get_result(account=account, pid=pid, **kwargs)
        if result is not None:
            if self._oj.is_accepted(result.verdict):
                result.verdict_code = Result.VerdictCode.VERDICT_ACCEPTED
            elif self._oj.is_running(result.verdict):
                result.verdict_code = Result.VerdictCode.VERDICT_RUNNING
            elif self._oj.is_compile_error(result.verdict):
                result.verdict_code = Result.VerdictCode.VERDICT_COMPILE_ERROR
            else:
                result.verdict_code = Result.VerdictCode.VERDICT_RESULT_ERROR
            result.execute_time = Core._space_and_enter_strip(result.execute_time)
            result.execute_memory = Core._space_and_enter_strip(result.execute_memory)

            return result
        return Result(Result.VerdictCode.VERDICT_SUBMIT_FAILED)

    # 通过运行id获取结果
    def get_result_by_rid_and_pid(self, rid, pid):
        if not self._oj:
            return Result(Result.VerdictCode.VERDICT_SUBMIT_FAILED)

        result = self._oj.get_result_by_rid_and_pid(rid, pid)
        if result is not None:
            if self._oj.is_accepted(result.verdict):
                result.verdict_code = Result.VerdictCode.VERDICT_ACCEPTED
            elif self._oj.is_running(result.verdict):
                result.verdict_code = Result.VerdictCode.VERDICT_RUNNING
            elif self._oj.is_compile_error(result.verdict):
                result.verdict_code = Result.VerdictCode.VERDICT_COMPILE_ERROR
            else:
                result.verdict_code = Result.VerdictCode.VERDICT_RESULT_ERROR
            result.execute_time = Core._space_and_enter_strip(result.execute_time)
            result.execute_memory = Core._space_and_enter_strip(result.execute_memory)
            return result
        return Result(Result.VerdictCode.VERDICT_SUBMIT_FAILED)

    # 获取源OJ语言
    def find_language(self, account, **kwargs):
        if not self._oj:
            return None
        self._oj.set_cookies(account.cookies)
        return self._oj.find_language(account=account, **kwargs)

    # 判断是否是等待判题的返回结果，例如pending,Queuing,Compiling
    def is_waiting_for_judge(self, verdict):
        if not self._oj:
            return None
        return self._oj.is_running(verdict)

    # 判断源OJ的网络连接是否良好
    def check_status(self):
        if not self._oj:
            return None
        return self._oj.check_status()

    # 判断结果是否AC
    def is_accepted(self, verdict):
        if not self._oj:
            return None
        return self._oj.is_accepted(verdict)

    # 判断是否运行中或者排队中
    def is_running(self, verdict):
        if not self._oj:
            return None
        return self._oj.is_running(verdict)

    # 判断是否编译错误
    def is_compile_error(self, verdict):
        if not self._oj:
            return None
        return self._oj.is_compile_error(verdict)

    # 判断爬虫账号是否可以正常登陆
    def is_account_valid(self, account):
        if self._oj and account and self._oj.login_website(account=account):
            return True
        return False