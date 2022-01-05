# Theia

Theia is a Python virtual environment (VENV) manager. From a requirements file, one may easily create VENVs.
It has great synergy with Gitlab Runners and was developed to constantly upgrade Python libraries in a CI/CD infrastructure of
Linux and Windows machines.

The name Theia is from the [Greek goddess of sight and vision](https://en.wikipedia.org/wiki/Theia).

## Usage

Execute Theia through `Theia/__main__.py`, by calling `python3 -m Theia {ARGUMENTS}`.
Arguments are described below and can be seen by calling `python3 -m Theia --help`.
By default, a VENV is created in `C:\ci\theia_venv\Scripts\python.exe`.

- `--root-dir`: Base directory where to instantiate VENVs. All files created by Theia will be in this directory. Default is `Theia.CI_FOLDER`.
- `--sub-dir`: Sub directory inside `--root-dir` where VENV is created. This allows multiple VENVs. Default is `theia_venv`.
- `--interpreters`: List of base Python interpreter paths. First existing interpreter of list will be used to create VENV. Separate with comma.
- `--requirements`: Requirements text file used to create VENV. Can be a local path or a URL.
- `--clear`: Deletes existing VENV and recreate it.

### Theia.CI_FOLDER

The CI_FOLDER variable is `C:\ci` in Windows machines and `/opt/ci` in Linux.
You may overwrite this variable with the environment variable `THEIA_ROOT_DIR`.

### Gitlab Runner Arguments

Theia can manage Gitlab Runner instances. Ignore this section if you're not working with Gitlab Runners.

- `--pause-runner`: Manage Theia VENV only after pausing Gitlab Runners associated with current machine and waiting for any running jobs to finish.
- `--ip`: IP of the current machine.
- `--token`: Gitlab access token used to pause/unpause runners.

The Gitlab URL is defined through `CI_API_V4_URL`. In Gitlab CI/CD, it is equal to `https://<Gitlab Private Domain>/api/v4`.


# Extra

## Locking Requirements in Python

Check out the [pip documentation on the requirements file](https://pip.pypa.io/en/stable/reference/requirements-file-format/).

- `--index-url` is useful if you have an independent Package Registry that is not PyPI.
- The `requirement-name~=X.Y` is specially useful in locking requirements, as it guarantees one is using the X version, but also updates to any versions greater than `X.Y.0`.

## Ansible with Windows

If you intend to use Ansible, here's a useful script to configure the target machine.

https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1

`cd C:/ci ; .\ConfigureRemotingForAnsible.ps1 -EnableCredSSP`
