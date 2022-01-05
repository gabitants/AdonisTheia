"""
Runner Manager
==============

"""
import sys
from typing import List
import argparse
import socket
from time import sleep, time
import requests


class RunnerManager:
    """
    Manages the status of runner services in a target machine.
    """

    def __init__(self, ip: str, token: str, base_url: str) -> None:
        """
        :param ip: IP of the target runner. (str)
        :param token: Gitlab API token used to manage runners. (str)
        :param base_url: Base URL of Gitlab API. (str)
        """
        self._target_runners: List[str] = []
        self._ip = ip
        self._token = token
        self._base_url = base_url

    @property
    def token(self) -> str:
        """
        :return: Access token used on requests. (str)
        """
        return "access_token=" + self._token

    @property
    def target_runners(self) -> list[str]:
        """
        :param: Runner service IDs in the target machine. (list)
        """
        if not self._target_runners:
            ip = socket.gethostbyname(self._ip)
            print(f"Working with machine: {ip}")
            max_runners = 100
            url = f"{self._base_url}/all/?{self.token}&per_page={max_runners}"
            runners = requests.get(url).json()
            assert len(runners) < max_runners, f"There are more than {max_runners} runners, this automation should be updated."
            # Get the runner by the ip
            try:
                self._target_runners = [r['id'] for r in runners if r['ip_address'] == ip]
            except Exception as e:
                print(runners)
                raise e
            print(f"Existing runners {self._target_runners}")
        return self._target_runners

    def stop(self) -> None:
        """
        Stops runners of machine. Waits for all jobs to finish.
        """
        for runner_id in self.target_runners:
            print(f"Stopping runner {runner_id}")
            requests.put(f"{self._base_url}/{runner_id}/?{self.token}", {"active": False})

        # Wait all jobs in machine to end before exit or timeout
        start = time()
        while (time() - start) // 60 < 15:
            jobs = []
            for runner_id in self.target_runners:
                jobs += requests.get(f"{self._base_url}/{runner_id}/jobs/?status=running&{self.token}").json()
            print(f"Jobs still running: {len(jobs)} ")
            if not jobs:
                break
            sleep(10)

    def start(self) -> None:
        """
        Starts runners of machine.
        """
        for runner_id in self.target_runners:
            requests.put(f"{self._base_url}/{runner_id}/?{self.token}", {"active": True})
            sleep(0.5)


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser("Nelogica Command Line Interface")
    main_parser.add_argument("ip", help="Ip of the runner to work with.")
    main_parser.add_argument("token", help="Gitlab access token.")
    main_parser.add_argument("status", help="Change the active status of the runner.", choices=['off', 'on'])
    main_parser.add_argument("url", help="Gitlab API URL used to access runners.")
    arguments = main_parser.parse_args(sys.argv[1:]).__dict__

    rm = RunnerManager(arguments["ip"], arguments["token"], arguments["url"])
    if arguments.get("status", "off") == "off":
        rm.stop()
    else:
        rm.start()
