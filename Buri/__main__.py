"""
Buri Main
==========

"""
import os
import sys
from argparse import ArgumentParser

# pylint: disable=wrong-import-position
p = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, p)
print(f'Added to PATH: {p}')

from Buri.utils import create_logger, show
from Buri.buri import Buri

CI_FOLDER = os.environ.get("THEIA_ROOT_DIR", r"C:\ci" if sys.platform.startswith("win") else '/opt/ci')


def job(root_dir: str, sub_dir: str, interpreters: str, requirements: str, ip: str, pause: bool, token: str, clear: bool, url: str) -> None:
    """ Job task. """
    original_dir = os.getcwd()
    theia_dir = os.path.join(root_dir, sub_dir)
    os.makedirs(theia_dir, exist_ok=True)
    logger_instance = create_logger('Buri', base_dir=theia_dir)
    show(logger_instance, f'Going from:\n\t\t{original_dir}\n\tto:\n\t\t{theia_dir}')
    os.chdir(theia_dir)

    t = Buri(theia_dir, interpreters)
    t.set_gitlab_runner(ip, token, url)
    t.update(path=requirements, clear=clear, pause=pause)


if __name__ == '__main__':
    main_parser = ArgumentParser("Buri Command Line Interface")
    main_parser.add_argument("--directory", "--root-dir", default=CI_FOLDER, dest="root_dir",
                             help="Base directory to use for Buri VENV.")
    main_parser.add_argument("--sub-dir", default="buri_venv", dest="sub_dir",
                             help="Sub directory to use for Buri VENV.")
    main_parser.add_argument("--interpreters", default='python3,py3,py,python',
                             help="List of base Python interpreter paths. Separate with comma.")
    main_parser.add_argument("--requirements", help="Requirements path for new bares.",
                             default='requirements.txt')
    main_parser.add_argument("--ip", help="IP of the current machine.", default="")
    main_parser.add_argument("--token", help="Git access token.", default="")
    main_parser.add_argument("--url", help="Gitlab API runner URL.", default="https://gitlab.nelogica.com.br/api/v4/runners")
    main_parser.add_argument("--pause-runner", default=False, dest="pause", action="store_true",
                             help="Manage VENV after pausing associated Gitlab Runners.")
    main_parser.add_argument("--clear", default=False, action="store_true",
                             help="Deletes previous VENVs created in final directory.")
    arguments = main_parser.parse_args(sys.argv[1:]).__dict__
    print(f"Using arguments: {arguments}")
    job(**arguments)
