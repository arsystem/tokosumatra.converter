""" Module for database helper """
import pymongo
import arrow

class DatabaseHelper:
    """ A helper class to save something into database
        This class will add some extra fields
    """
    def __init__(self, **kwargs):
        self.dbase = kwargs.get("dbase", None)
        self.collection = kwargs.get("collection", None)
        self.indexes = kwargs.get("indexes", [])

    def get(self, condition=None, field=None):
        """ get data from database  based on given condition and field.

            Exceptions:
            - AssertionError
        """
        assert self.dbase is not None, "dbase is not defined."
        assert self.collection is not None, "collection is not defined."

        if condition is None:
            condition = {}

        conn = pymongo.MongoClient(
            "mongodb://frans:a123456789b@localhost/?authSource=admin"
        )
        try:
            dbase = conn[self.dbase]
            return dbase[self.collection].find(condition, field)
        finally:
            conn.close()

    def insert_one(self, document=None, upsert=False, key=None):
        """ Save something to database """
        assert self.dbase is not None, "dbase is not defined."
        assert self.collection is not None, "collection is not defined."
        assert document is not None, "document is not defined."
        assert upsert is not None, "upsert is not defined."

        conn = pymongo.MongoClient(
            "mongodb://frans:a123456789b@localhost/?authSource=admin"
        )
        dbase = conn[self.dbase]
        try:
            for field, index_type in self.indexes:
                if index_type == "unique":
                    dbase[self.collection].create_index(field, unique=True)
                else:
                    dbase[self.collection].create_index(field)
            document.update({"insertTime": arrow.utcnow().datetime})
            if upsert:
                assert key is not None, "key is not defined."
                assert isinstance(key, dict), "incorrect data type for key. Found %s" % type(key)
                dbase[self.collection].update_one(key, {"$set": document}, upsert=True)
            else:
                dbase[self.collection].insert_one(document)
        finally:
            conn.close()
