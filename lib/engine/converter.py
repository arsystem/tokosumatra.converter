""" Module for all converter """
import os
import copy
import logging
import glob
import hashlib
import ntpath

import profig
import arrow
import tablib
import dbfread

from ..helper.database import DatabaseHelper
from ..model.departments import Department
from ..model.supliers import Suplier
from ..model.prices import Price
from ..model.products import Product
from ..model.customers import Customer
from ..model.sales import Sale
from ..model.machine import Machine
from ..model.cashier import Cashier

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
    class FieldParser(dbfread.FieldParser):
        def parse(self, field, data):
            try:
                return dbfread.FieldParser.parse(self, field, data)
            except ValueError:
                return dbfread.InvalidValue(data)

    def __init__(self):
        super(SalesConverter, self).__init__()

    def convert(self, all_sales=False):
        """ Overiding `convert` function from parent.
        """

        path = os.path.join(self.cfg["eod_path.penjualan"], "*.dbf")
        if not all_sales:
            path = os.path.join(self.cfg["eod_path.penjualan"], "CP??%s%s.dbf" % (
                arrow.now().format("MM"),
                arrow.now().format("DD")
            ))
        eod_files = glob.iglob(path)
        for eod in eod_files:
            file_name = ntpath.basename(eod)

            machine = Machine()
            machine.code = file_name[2:4]
            machine.name = "Kasir %s" % machine.code
            machine.save()

            sales_id = None
            cashier = None

            table = dbfread.DBF(eod, parserclass=SalesConverter.FieldParser)
            for row in table:
                # Generate new ID if row["FLAG"] is NEW
                if row["FLAG"] == "NEW":
                    sales_id = "%s&%s&%s" % (row["CODE"], row["NORCP"], row["DDATE"])
                    sales_id = sales_id.encode("utf8")
                    sales_id = hashlib.sha256(sales_id).hexdigest()

                    cashier = Cashier()
                    cashier.code = row["DESC"][0:6].decode("utf8").strip()
                    cashier.name = row["DESC"][7:].decode("utf8").strip()
                    cashier.save()

                    # Check if new sales_id has been inserted into Database or not
                    helper = DatabaseHelper()
                    helper.dbase = "tokosumatra"
                    helper.collection = "sale"
                    document = helper.get({"code": sales_id}, {"code": 1})

                    can_insert = False
                    if document.count() == 0:
                        can_insert = True

                if (row["FLAG"] == "PLU" or row["FLAG"] == "RTN" or row["FLAG"] == "VOD") \
                    and can_insert:
                    assert sales_id is not None, "sales_id is not defined."
                    assert cashier is not None, "cashier is not defined."

                    sale = Sale(
                        code=sales_id,
                        sales_date=row["DDATE"],
                        product=Product(barcode=row["CODE"]),
                        qty=row["QTY"],
                        price=Price(value=row["PRICE"]),
                        department=Department(code=row["DEPT"]),
                        suplier=Suplier(code=row["SUPL"]),
                        machine=machine,
                        cashier=cashier
                    )
                    if row["FLAG"] == "RTN" or row["FLAG"] == "VOD":
                        sale.qty = sale.qty * -1
                    if "CUST" in row:
                        sale.customer = Customer(code=row["CUST"])
                    sale.save()

