import os
from sqlalchemy import create_engine, Column, Boolean, BigInteger, Integer, SmallInteger, Numeric, String, Float, text, \
    Date, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


db_url = 'postgresql://postgres:fred@localhost:5432'
engine = create_engine(db_url)


db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class Category(Base):
    __tablename__ = 'flaemi_category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class Property(Base):
    __tablename__ = 'flaemi_property'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('flaemi_category.id'))
    type = Column(String(10), nullable=False)  # int, float, percent, bool
    note = Column(String)  # of GDP, annual change
    name = Column(String(50), nullable=False)
    description = Column(String)
    year_cia = Column(SmallInteger, nullable=False)

'''
class PropertyToValue(Base):
    __tablename__ = 'flaemi_p2v'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('flaemi_property.id'))
    nblv_id = Column(Integer, ForeignKey('flaemi_normalboolvalues.id'))
    float_id = Column(Integer, ForeignKey('flaemi_floatvalues.id'))
    int_id = Column(Integer,  ForeignKey('flaemi_intvalues.id'))


class IntegerValue(Base):
    __tablename__ = 'flaemi_intvalues'

    id = Column(Integer, primary_key=True)
    p2v_id = Column(Integer)
    country = Column(String)
    year_est = Column(SmallInteger)
    value = Column(Integer)


class NormalBoolValues(Base):
    __tablename__ = 'flaemi_normalboolvalues'

    id = Column(Integer, primary_key=True)
    p2v_id = Column(Integer, ForeignKey('flaemi_p2v.id'))
    bool_id = Column(Integer, ForeignKey('flaemi_boolvalues.id'))
    value = Column(String)


class BoolValue(Base):
    __tablename__ = 'flaemi_boolvalues'farið með 

    id = Column(Integer, primary_key=True)
    nbv_id = Column(Integer, ForeignKey('flaemi_normalboolvalues.id'))
    country = Column(String)
    value = Column(Boolean)
'''


class FloatValue(Base):
    __tablename__ = 'flaemi_floatvalues'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('flaemi_property.id'))
    country = Column(String)
    year_est = Column(SmallInteger)
    value = Column(Float)


class IntegerValue(Base):
    __tablename__ = 'flaemi_intvalues'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('flaemi_property.id'), nullable=False)
    country = Column(String(2), nullable=False)
    year_est = Column(SmallInteger)
    value = Column(BigInteger, nullable=False)
    note = Column(String)


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    print('Initialising DB')
    Base.metadata.create_all(bind=engine)


init_db()
