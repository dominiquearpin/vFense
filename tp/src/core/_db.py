from vFense.core._db_constants import DbInfoKeys
from vFense.core.customer import *
import logging
from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

@db_create_close
def retrieve_primary_key(collection, conn=None):
    """Retrieve the primary key for a collection.
    Args:
        collection (str):  The table aka collection you are doing the query against.

    Basic Usage:
        >>> from vFense._db import retrieve_primary_key
        >>> collection = 'users'
        >>> retrieve_primary_key(collection)

    Returns:
        String
    """
    data = {}
    try:
        data = (
            r
            .table(collection)
            .info()
            .pluck(DbInfoKeys.PRIMARY_KEY)
            .run(conn)
        )
        if data:
            data = data[DbInfoKeys.PRIMARY_KEY]

    except Exception as e:
        logger.exception(e)

    return(data)

@db_create_close
def retrieve_indexes(collection, conn=None):
    """Retrieve the list of indexes for a collection.
    Args:
        collection (str):  The table aka collection you are doing the query against.

    Basic Usage:
        >>> from vFense._db import retrieve_indexes
        >>> collection, = 'users'
        >>> retrieve_indexes(collection)

    Returns:
        List
    """
    data = {}
    try:
        data = (
            r
            .table(collection)
            .info()
            .pluck(DbInfoKeys.INDEXES)
            .run(conn)
        )
        if data:
            data = data[DbInfoKeys.INDEXES]

    except Exception as e:
        logger.exception(e)

    return(data)


@db_create_close
def retrieve_object(primary_key, collection, conn=None):
    """Retrieve object by primary key and collection.
    Args:
        primary_key (str):  The primary key that you are doing a get against.
        collection (str):  The table aka collection you are doing the query against.

    Basic Usage:
        >>> from vFense._db import retrieve_object
        >>> collection, = 'users'
        >>> primary_key = 'admin'
        >>> retrieve_object(primary_key, collection)

    Returns:
        Dictionary
    """
    data = {}
    try:
        data = (
            r
            .table(collection)
            .get(primary_key)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
