import logging
from lib.engine.converter import SalesConverter

def run():
    """ main program runs here """
    converter = SalesConverter()
    converter.convert()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
