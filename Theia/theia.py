"""
Theia Main Class
================
"""
import os
import platform

from Theia.utils import cmd, show
from Theia.core import Core


class Theia:
    """
    QA VENV execution manager.
    """

    def __init__(self, directory: str, interpreters: str = 'python3,py3,py,python'):
        """
        :param directory: VENV directory. (str)
        :param interpreters: Comma separated list of base interpreters to try to use. First OK is used. (str)
        """
        self.core = Core(directory=directory, interpreters=interpreters)
        show(self.core.log, 'Finished instantiating Theia.\n')
        self._ip = ""
        self._token = ""
        self._api_url = ""

    def ping(self, host: str) -> str:
        """
        Checks if host responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        If host in unreachable, will raise an Exception.

        :param host: Host. (str)
        :return: Ping result. (str)
        """
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        return str(cmd(self.core.log, ' '.join(['ping', param, '1', host]), f'Could not reach host at {host}', raising=False))

    def requester(self, url: str, request_type: str = 'get', kwargs: str = "{}") -> str:
        """
        Calls external script that makes HTTP requests.
        Script is implemented separately as to avoid adding it's requirements to Theia.

        :param url: Request URL. (str)
        :param request_type: If should GET or POST the request. (str)
        :param kwargs: String representation of a dictionary with the keyed arguments used with the request. (str)
        :return: The request text response. (str)
        """
        get_remote_script_path = os.path.join(os.path.dirname(__file__), 'get_remote.py')
        command = f'{get_remote_script_path} {url} --request-type {request_type} --kwargs {kwargs}'
        return str(self.core.run(command, f'Failed in fetching remote {url}'))

    def set_gitlab_runner(self, ip: str, token: str, api_url: str) -> None:
        """
        Sets Gitlab Runner access variables.

        :param ip: IP of the current machine. Required when operating in a runner. (str)
        :param token: Gitlab access token. (str)
        :param api_url: Gitlab API URL used to access runners. e.g. `https://gitlab.com./api/v4/runners`. (str)
        """
        self._ip = ip
        self._token = token
        self._api_url = api_url

    def update(self, path: str = "", clear: bool = False, pause: bool = True, ) -> None:
        """
        If in a runner machine and a VENV already exists, first pause all runner services, then unpause them at the end of
        the update. Creates a nem VENV if it does not exist or `clear` is `True`. Updates requirements based on `path`.

        :param path: Path to requirements. Can ba a local path or an URL. (str)
        :param clear: If should wipe VENV dir and create if from scratch. (bool)
        :param pause: If should pause runner services in machine before operating. (bool)
        :raise AssertionError: When operating in a runner and IP was not given.
        """
        # If there is a VENV already and we are in a runner, pause the runner services to safely alter the VENV.
        runner_manager = os.path.join(os.path.dirname(__file__), 'runner_manager.py')
        if pause and self.core.venv:
            assert self._ip, "If in a runner, IP must be given."
            show(self.core.log, f'Pausing runner {self._ip}', color="cyan")
            show(self.core.log, self.core.run(f'{runner_manager} {self._ip} {self._token} off {self._api_url}', f'Failed turning off {self._ip}'))
            paused = True
        else:
            paused = False

        if not self.core.venv or clear:
            self.core.make_venv(clear=clear)
            show(self.core.log, 'Asserting essential requirements are installed.')
            self.core.install(['setuptools_scm', 'requests'])

        if path:
            if path.startswith("http"):
                content = self.requester(path, kwargs="dict(allow_redirects=True)")
                requirements_path = os.path.join(self.core.directory, "requirements.txt")
                with open(requirements_path, "w", encoding='utf8') as f:
                    f.write(content)
                path = requirements_path
            assert os.path.exists(path), f"Path does not exist: {path}"
            show(self.core.log, f'Updating requirements from {path}')
            with open(path, encoding='utf8') as f:
                self.core.log.info(f.read())
            self.core.run(f"-m pip install -r {path} --upgrade")  # https://pip.pypa.io/en/stable/cli/pip_install/

        if paused:
            show(self.core.log, f'Staring runner {self._ip}', color="cyan")
            show(self.core.log, self.core.run(f'{runner_manager} {self._ip} {self._token} on {self._api_url}', f'Failed turning on {self._ip}'))
