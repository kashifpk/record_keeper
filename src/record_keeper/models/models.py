"""Database Models."""

import logging
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, Unicode, DateTime
from sqlalchemy.orm import backref, relationship

from ..app_objects import app


log = logging.getLogger(__name__)


class Catalog(app.DBBase):
    """Single catalog item (dvd/cdrom/etc.) representation."""

    __tablename__ = "catalogs"

    catalog_id = Column(Unicode(100), primary_key=True)  # e.g, TV-202
    catalog_type = Column(Unicode(50))  # M, TV, XF, etc
    catalog_number = Column(Integer)
    volume_label = Column(Unicode(100))  # e.g, supernatural_s15
    timestamp = Column(DateTime, default=datetime.now)


class Listing(app.DBBase):
    """Catalog file listings."""

    __tablename__ = "listings"

    listing_id = Column(Integer, primary_key=True)
    catalog_id = Column(Unicode(100), ForeignKey(Catalog.catalog_id))
    path = Column(Unicode(1000))

    catalog = relationship(
        Catalog, backref=backref("files", cascade="all, delete-orphan")
    )
