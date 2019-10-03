"""Setup script."""

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    "SQLAlchemy==1.2.7",
    "transaction",
    "zope.sqlalchemy",
    "Click",
    "colorama",
]

open(os.path.join(here, "requirements.txt"), "w").writelines(
    [line + "\n" for line in requires]
)

setup(
    name="record_keeper",
    version="20190922",
    description="Record Keeper",
    long_description="Record Keeper",
    classifiers=["Programming Language :: Python"],
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points="""\
    [console_scripts]
    record_keeper = record_keeper.scripts.record_keeper_main:cli
    """,
)
