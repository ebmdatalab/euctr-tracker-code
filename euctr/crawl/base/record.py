# -*- coding: utf-8 -*-
import uuid
import scrapy
import logging
from abc import abstractmethod
from . import config
from . import fields
logger = logging.getLogger(__name__)


# Module API

class Record(scrapy.Item):

    # Public

    def __repr__(self):
        template = '<%s: %s>'
        text = template % (self.table.upper(), self.get(self.__primary_key))
        return text

    @property
    @abstractmethod
    def table(self):
        """Source name.
        """
        pass  # pragma: no cover

    @classmethod
    def create(cls, source, data):

        # Init dict
        self = cls()

        # Get primary_key
        self.__primary_key = None
        for key, field in self.fields.items():
            if field.primary_key:
                self.__primary_key = key
                break
        if self.__primary_key is None:
            raise TypeError('Record %s requires primary key' % cls)
        if not isinstance(self.fields[self.__primary_key], fields.Text):
            raise TypeError('Record %s requires text primary key' % cls)

        # Get column types
        self.__column_types = {}
        for key, field in self.fields.items():
            self.__column_types[key] = field.column_type

        # Add metadata
        ident = uuid.uuid1().hex
        self.fields['meta_id'] = fields.Text()
        self.fields['meta_source'] = fields.Text()
        self.fields['meta_created'] = fields.Datetime()
        self.fields['meta_updated'] = fields.Datetime()
        self['meta_id'] = ident
        self['meta_source'] = source

        # Check for existence of fields not defined in our schema
        undefined = []
        for key, value in data.items():
            field = self.fields.get(key)
            if field is None:
                undefined.append(key)
                continue

        # Set values for everything that is in our schema
        for key, value in self.fields.items():
            d = value.parse(data.get(key, None))
            self[key] = d

        for key in undefined:
            logger.warning('Undefined field: %s - %s' % (self, key))
        return self

    def write(self, conf, conn):
        """Write record to warehouse.

        Args:
            conf (dict): config dictionary
            conn (dict): connections dictionary

        """
        db = conn['warehouse']
        if self.table not in db.tables:
            if conf['ENV'] in ['development', 'testing']:
                table = db.create_table(
                        self.table,
                        primary_id=self.__primary_key,
                        primary_type=fields.Text.column_type)
                # work around a bug whereby the table is not persisted
                table.table
        table = db[self.table]
        action = 'created'
        if table.find_one(**{self.__primary_key: self[self.__primary_key]}):
            action = 'updated'
            del self['meta_id']

        ensure_fields = False
        if conf['ENV'] in ['development', 'testing']:
            ensure_fields = True
        table.upsert(self, [self.__primary_key], ensure=ensure_fields, types=self.__column_types)

        logger.debug('Record - %s: %s - %s fields', action, self, len(self))
