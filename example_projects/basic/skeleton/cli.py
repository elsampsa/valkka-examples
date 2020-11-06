"""
NAME.py : Description of the file

* Copyright: 2017 [copyright holder]
* Authors  : Sampsa Riikonen
* Date     : 2017
* Version  : 0.1

[copy-paste your license here]
"""
# based on https://github.com/elsampsa/skeleton

import logging
import argparse
import configparser # https://docs.python.org/3/library/configparser.html
from .main import app
from .constant import default_ini
from .tools import getLogger, confLogger


def set_logging(command, options, config):
    for key in config.keys():
        if "logger_" in key:
            pars = config[key]
            qualname = pars["qualname"]
            levelstr = pars["level"]
            level = getattr(logging, levelstr)
            # logger = logging.getLogger(qualname)
            getLogger(qualname)
            confLogger(logger, level)

    ## now, anywhere in your code, do this:
    logger = logging.getLogger("my_valkka_project")
    logger.debug("debug")
    logger.info("info")

    l = config["DEFAULT"]
    logger.info("ServerAliveInterval %s", l["ServerAliveInterval"])

    ## could chain more config / option handling here
    ## next, proceed to the actual entry point of your app
    app(command, options, config)


def process_cl_args():
  
    def str2bool(v):
        return v.lower() in ("yes", "true", "t", "1")

    parser = argparse.ArgumentParser(usage="""     
your_command [options] command

    commands:

        foo     Is not bar
        bar     Is not foo

    options:

        --nice  Be nice or not.  Default true.
        --ini   ini configuration file.

    """)
    # parser.register('type','bool',str2bool)  # this works only in theory..

    parser.add_argument("command", action="store", type=str,                 
                        help="mandatory command")

    parser.add_argument("--nice", action="store", type=str2bool, required=False, default=False,
                        help="Be nice")

    parser.add_argument("--ini", action="store", type=str, required=False, default=None,
                        help=".ini configuration file")

    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args


def main():
    parsed, unparsed = process_cl_args()

    cf = configparser.ConfigParser()
    cf.read_string(default_ini)

    if parsed.ini is None:
        pass
    else:
        files = cf.read(parsed.ini)
        # print("read files", files)

    ## some command filtering here
    if parsed.command in ["foo", "bar"]:
        set_logging(parsed.command, parsed, cf)
    else:
        print("unknown command", parsed.command)

    # logging without ini:
    """
    logger = getLogger("name.space")
    confLogger(logger, logging.INFO)
    """


if (__name__ == "__main__"):
    main()
