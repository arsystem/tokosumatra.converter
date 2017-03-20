""" Module for all converter """
import os
import copy
import logging

import profig
import tablib
import dbfread

from ..helper.database import DatabaseHelper
from ..model.departments import Department
from ..model.supliers import Suplier
from ..model.prices import Price
from ..model.products import Product
from ..model.customers import Customer
from ..model.sales import Sale

class Converter:
    """ Converter base class """
    def __init__(self):
        self.cfg = profig.Config(os.path.join(os.getcwd(), "config.ini"))
        self.cfg.sync()

    def convert(self):
        """ Convert from dbf to mongodb """
        raise NotImplementedError

class DepartmentsConverter(Converter):
    """ A class to convert from Department DBF to MongoDB
        This class is depends on `config.ini`
    """
    def __init__(self):
        super(DepartmentsConverter, self).__init__()

    def convert(self):
        """ Convert from dbf to mongodb """
        table = tablib.Dataset()
        table.dbf = open(self.cfg["dbf_path.department"], "rb").read()
        for row in table:
            Department(code=row[0], name=row[1]).save()
        del table

class SupliersConverter(Converter):
    """ A class to convert from Suplier DBF to MongoDB
        This class is depends on `config.ini`
    """
    def __init__(self):
        super(SupliersConverter, self).__init__()

    def convert(self):
        """ Overiding `convert` function from parent """
        table = tablib.Dataset()
        table.dbf = open(self.cfg["dbf_path.suplier"], "rb").read()
        for row in table:
            Suplier(
                code=row[0],
                name=row[1],
                address=row[2],
                city=row[3],
                phone=row[4],
                contact_person=row[5]
            ).save()
        del table

class ProductsConverter(Converter):
    """ A class to convert from product DBF to MongoDB
        This class is depends on `config.ini`
    """
    def __init__(self):
        super(ProductsConverter, self).__init__()

    def convert(self):
        """ Overiding `convert` function from parent """
        table = dbfread.DBF(self.cfg["dbf_path.produk"])
        for row in table:
            department = Department(code=row["DEPT"])
            prices = [
                Price(min_qty=row["QTY1"], value=row["PRICE"]),
                Price(min_qty=row["QTY2"], value=row["PRICE2"]),
                Price(min_qty=row["QTY3"], value=row["PRICE3"])
            ]
            suplier = Suplier(code=row["SUPL"])
            Product(
                barcode=row["CODE"],
                name=row["DESC"],
                department=department,
                prices=prices,
                suplier=suplier
            ).save()
        del table

class CustomersConverter(Converter):
    """ A class to convert from customer DBF to MongoDB
        This class is depends on `config.ini`
    """
    def __init__(self):
        super(CustomersConverter, self).__init__()

    def convert(self):
        """ Overiding `convert` function from parent """
        table = dbfread.DBF(self.cfg["dbf_path.customer"])
        for row in table:
            Customer(
                code=row["CODE"],
                name=row["DESC"],
                address=row["ALAMAT"],
                city=row["KOTA"],
                postcode=row["KDPOS"],
                phone=row["TELP"],
                mobile=row["HP"],
                member_since=row["TANGGAL"],
                birthday=row["LAHIR"],
                gender=row["JENIS"],
                email=row["EMAIL"],
                ktp=row["KTP"],
                point=row["POINT"],
                point_expirity_date=row["P_EXPD"],
                expired_point=0
            ).save()
        del table

class SalesConverter(Converter):
    """ A class to convert from sales DBF to MongoDB
        This class is depends on `config.ini`
    """
    def __init__(self):
        super(SalesConverter, self).__init__()

    def do_convert(self, index=None, row=None):
        """ Execute convert in multithreading ways """
        assert row is not None, "row is not defined."
        assert index is not None, "index is not defined."

        product = Product(barcode=row["KDBR"])
        price = Price(value=row["HARGA"])
        suplier = Suplier(code=row["SUPL"])
        department = Department(code=row["DEPT"])
        customer = None

        if not customer:
            customer = Customer(code=row["CUST"])

        Sale(
            code=index,
            sales_date=row["TGBON"],
            product=product,
            qty=row["BANYAK"],
            price=price,
            department=department,
            suplier=suplier,
            discount_1=row["DISC1"],
            discount_2=row["DISC2"],
            discount_3=row["DIS"],
            disocunt_4=row["DISRP"],
            customer=customer
        ).save()

    def convert(self):
        """ Overiding `convert` function from parent.
            The logic is quite simple, you need to get latest index
            for last converted `sales`.
        """
        logger = logging.getLogger(__name__)

        # Get last converted index
        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "status"
        status = helper.get({"name": "sales"})[0]
        last_index = 0

        if status is not None:
            last_index = int(copy.copy(status["last_index"]))

        table = dbfread.DBF(self.cfg["dbf_path.penjualan"], load=True)
        total_row = len(table.records) - 1
        processed_index = 0
        try:
            for index, row in enumerate(table.records[last_index:]):
                logger.debug("%s of %s", index + last_index, total_row)
                if (index + last_index) >= last_index:
                    self.do_convert((index + last_index), row)
                processed_index = copy.copy((index + last_index))
        finally:
            status.update({"last_index": processed_index})
            helper.insert_one(status, upsert=True, key={"name": "sales"})
            del table
