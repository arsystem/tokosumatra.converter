""" A skleton for all programs """
import os
import logging

from lib.model.products import Product
from lib.model.prices import Price
from lib.model.supliers import Suplier
from lib.model.customers import Customer
from lib.model.departments import Department
from lib.model.sales import Sale

import click
import dbfread
import profig

@click.command()
def run():
    pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
