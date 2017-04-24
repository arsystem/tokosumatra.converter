""" Sales module """
import logging

from pymongo.errors import DuplicateKeyError
from ..helper.database import DatabaseHelper
from . import Model

import arrow

class Sale(Model):
    """ Model for sale """
    @property
    def sales_date(self):
        return self._sales_date
    @sales_date.setter
    def sales_date(self, value):
        self._sales_date = arrow.get(value).datetime

    def __init__(self, **kwargs):
        self._sales_date = None

        self.code = kwargs.get("code", None)
        self.sales_date = kwargs.get("sales_date", None)
        self.product = kwargs.get("product", None)
        self.qty = kwargs.get("qty", None)
        self.price = kwargs.get("price", None)
        self.department = kwargs.get("department", None)
        self.suplier = kwargs.get("suplier", None)
        self.customer = kwargs.get("customer", None)
        self.cashier = kwargs.get("cashier", None)
        self.machine = kwargs.get("machine", None)

    def to_dict(self):
        """ Convert to dictionary object """
        product_barcode = None
        if self.product is not None:
            product_barcode = self.product.barcode

        price_value = None
        if self.price is not None:
            price_value = self.price.value

        department_code = None
        if self.department is not None:
            department_code = self.department.code

        suplier_code = None
        if self.suplier is not None:
            suplier_code = self.suplier.code

        customer_code = None
        if self.customer is not None:
            customer_code = self.customer.code

        cashier_code = None
        if self.cashier is not None:
            cashier_code = self.cashier.code

        machine_code = None
        if self.machine is not None:
            machine_code = self.machine.code

        return {
            "code": self.code,
            "sales_date": self.sales_date,
            "product": product_barcode,
            "qty": self.qty,
            "price": price_value,
            "department": department_code,
            "suplier": suplier_code,
            "customer": customer_code,
            "cashier": cashier_code,
            "machine": machine_code
        }

    def save(self):
        """ Save to databaes """
        logger = logging.getLogger(__name__)
        try:
            helper = DatabaseHelper()
            helper.dbase = "tokosumatra"
            helper.collection = "sale"
            helper.indexes = [("code", "")]
            helper.insert_one(self.to_dict())
            logger.debug("Inserted or updated one sale")
        except DuplicateKeyError:
            logger.warning("Duplicate code: %s", self.code)
