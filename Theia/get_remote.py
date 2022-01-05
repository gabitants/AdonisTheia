"""
Get Remote
==========

Gets a remote...
"""
import sys
import argparse
import requests


def requester(url: str, request_type: str = 'get', kwargs: str = "{}") -> str:
    """
    Get a remote text file.

    :param url: File URL. (str)
    :param request_type: Request type. (str)
    :param kwargs: Stringed keyed arguments of request. (str)
    :return: File content. (str)
    """
    # pylint: disable=eval-used
    return str(getattr(requests, request_type)(url, **eval(kwargs)).text)


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser("Nelogica Command Line Interface")
    main_parser.add_argument("url", help="Request URL.")
    main_parser.add_argument("--request-type", help="Request type. (get or post)", dest="request_type")
    main_parser.add_argument("--kwargs", help="Request keyed arguments.")
    arguments = main_parser.parse_args(sys.argv[1:]).__dict__
    print(requester(**arguments))
