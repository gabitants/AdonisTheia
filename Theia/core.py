"""
Core
====
"""
import os
from typing import List, Set
from pathlib import Path
from subprocess import getstatusoutput
from shutil import rmtree

from Theia.utils import cmd, create_logger


class Core:
    """
    VENV manager.
    """

    def __init__(self, directory: str, interpreters: str) -> None:
        """
        :param directory: VENV directory. (str)
        :param interpreters: Comma separated list of base interpreters to try to use. First OK is used. (str)
        :raise UserWarning: If none of the given interpreters are found.
        """
        bases = interpreters.split(",")
        print(f'Searching for base Python with {bases}')
        for c in bases:
            sts, out = getstatusoutput(f'{c} --version')
            if sts == 0:
                self._interpreter = c
                print(f'Set base Python as [{c}] with version {out}')
                break
        else:
            raise UserWarning('Could not find a base Python interpreter in:\n\t' + '\n\t'.join(bases))

        self.install_failures: Set[str] = set()
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.log = create_logger('Theia', base_dir=self.directory)
        self._venv = ""

    @property
    def venv(self) -> str:
        """
        Searches for a VENV in current Main Directory.

        :raise AssertionError: When multiple venv candidates are found.
        :return: VENV path or an empty string if it was not found. (str)
        """
        if not self._venv:
            print(f"Searching for VENV in {self.directory}")
            base_path = Path(os.path.join(self.directory))
            paths = [str(p) for p in base_path.rglob('python.exe')]
            paths += [str(p) for p in base_path.rglob('python')]
            paths = [p for p in paths if 'site-packages' not in p]
            print(f"\tFound {paths}")
            assert len(paths) <= 1, f'Found {len(paths)} possible Python interpreters. \n\t{paths}'
            self._venv = paths[0] if paths else ""
        return self._venv

    def make_venv(self, clear: bool = False) -> None:
        """
        Creates a VENV in `self.directory` using given Python interpreter.

        :param clear: If should wipe VENV dir and create if from scratch. (bool)
        """
        if clear:
            rmtree(self.directory, ignore_errors=True)
        if self.venv:
            return
        cmd(self.log, f'{self._interpreter} -m venv {self.directory}', 'While trying to create venv')
        assert self.venv, 'Could not make virtual environment.'
        self.run('-m pip install --upgrade pip')

    def run(self, c: str, msg: str = "") -> str:
        """
        Runs given command using Python VENV.

        :param c: Command. (str)
        :param msg: Message to show in case of failure. (str)
        :return: Command result. (str)
        """
        return str(cmd(self.log, f'{self.venv} {c}', msg or f'While running {c}'))

    def install(self, requirements: List[str]) -> None:
        """
        Installs given packages using pip. Populates `self.install_failures` with failed installs.

        :param requirements: Packages to install. (list of str)
        """
        for req in requirements:
            if not req:
                continue
            try:
                req = req.replace("\n", "")
                self.run(f'-m pip install {req}', f'While installing requirement {req}')
                if req in self.install_failures:
                    self.install_failures.remove(req)
            except Exception as e:
                print(e)
                self.install_failures.add(req)
