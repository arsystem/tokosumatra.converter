""" A wrapper for converter program """
import logging
import time

from lib.engine.converter import DepartmentsConverter, SupliersConverter, \
                                 ProductsConverter, CustomersConverter, \
                                 SalesConverter
import schedule

def run(convert):
    """ Main program runs here """
    if convert.lower() == "departments":
        converter = DepartmentsConverter()
    if convert.lower() == "supliers":
        converter = SupliersConverter()
    if convert.lower() == "products":
        converter = ProductsConverter()
    if convert.lower() == "customers":
        converter = CustomersConverter()
    if convert.lower() == "sales":
        converter = SalesConverter()
    converter.convert()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    schedule.every().hour.do(run, "products")
    schedule.every().hour.do(run, "departments")
    schedule.every().hour.do(run, "supliers")
    schedule.every().hour.do(run, "customers")
    schedule.every().day.at("22:30").do(run, "sales")

    while True:
        schedule.run_pending()
        time.sleep(10)
