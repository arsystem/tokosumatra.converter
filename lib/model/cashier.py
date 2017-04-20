""" Cashier module """
import logging

from pymongo.errors import DuplicateKeyError
from ..helper.database import DatabaseHelper
from . import Model

class Cashier(Model):
    """ Class untuk cashier """
    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.name = kwargs.get("name", None)

    def to_dict(self):
        """ Convert to dictionary """
        return {
            "code": self.code,
            "name": self.name
        }

    def save(self):
        """ Save to database """
        logger = logging.getLogger(__name__)
        try:
            helper = DatabaseHelper()
            helper.dbase = "tokosumatra"
            helper.collection = "cashier"
            helper.indexes = [("code", "unique", )]
            helper.insert_one(self.to_dict(), upsert=True, key={"code": self.code})
            logger.debug("Inserted or updated on cashier")
        except DuplicateKeyError:
            logger.warning("Duplicate code: %s", self.code)
