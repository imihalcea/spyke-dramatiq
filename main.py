import sys
import argparse

import dramatiq
from dramatiq.logging import get_logger

from double import double 
from square import square
from plumbing import setup

setup()
logger = get_logger(__name__)

def main():
    logger.info("Starting main")
    parser = argparse.ArgumentParser()
    parser.add_argument("xs", nargs="+", help="x")
    arguments = parser.parse_args()
    #the pipeline is: double -> square
    jobs = dramatiq.group(double.message(int(x)) | square.message() for x in arguments.xs).run()
    for x, y in zip(arguments.xs, jobs.get_results(block=True)):
        print(f"{x} doubled then squared is {y}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
    