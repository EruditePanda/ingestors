#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='ingestors',
    version='0.6.2',
    description="Ingestors extract useful information in a structured standard format.",  # noqa
    author="Organized Crime and Corruption Reporting Project",
    author_email='tech@occrp.org',
    url='https://github.com/alephdata/ingestors',
    packages=find_packages(exclude=['tests']),
    package_dir={'ingestors': 'ingestors'},
    include_package_data=True,
    install_requires=[
        'banal >= 0.1',
        'normality >= 0.5.2',
        'urllib3 >= 1.21',
        'requests >= 2.18.4',
        'xlrd >= 1.1.0',
        'openpyxl >= 2.4.9',
        'odfpy >= 1.3.5',
        'backports.csv >= 1.0.5',
        'cchardet >= 2.1.1',
        'lxml >= 3.8.0',
        'pillow >= 4.0.0',
        'olefile >= 0.44',
        'tesserocr >= 2.2.2',
        'python-magic >= 0.4.12',
        'pypdf2 >= 1.26.0',
        'rarfile >= 3.0',
        'flanker >= 0.4.38',
        'imapclient >= 1.0.2',
        'dbf >= 0.96.8'
    ],
    extras_require={
        ':python_version<"3"': ['subprocess32']
    },
    license="MIT",
    zip_safe=False,
    keywords='ingestors',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=[],
    entry_points={
        'ingestors': [
            'ignore = ingestors.ignore:IgnoreIngestor',
            'html = ingestors.documents.html:HTMLIngestor',
            'xml = ingestors.documents.xml:XMLIngestor',
            'plain = ingestors.documents.plain:PlainTextIngestor',
            'office = ingestors.documents.office:DocumentIngestor',
            'opendoc = ingestors.documents.opendoc:OpenDocumentIngestor',
            'ooxml = ingestors.documents.ooxml:OfficeOpenXMLIngestor',
            'image = ingestors.documents.image:ImageIngestor',
            'svg = ingestors.documents.image:SVGIngestor',
            'djvu = ingestors.documents.djvu:DjVuIngestor',
            'pdf = ingestors.documents.pdf:PDFIngestor',
            'rar = ingestors.packages:RARIngestor',
            'zip = ingestors.packages:ZipIngestor',
            'tar = ingestors.packages:TarIngestor',
            '7z = ingestors.packages:SevenZipIngestor',
            'gz = ingestors.packages:GzipIngestor',
            'bz2 = ingestors.packages:BZ2Ingestor',
            'pst = ingestors.email.outlookpst:OutlookPSTIngestor',
            'olemsg = ingestors.email.outlookmsg:OutlookMsgIngestor',
            'msg = ingestors.email.msg:RFC822Ingestor',
            'csv = ingestors.tabular.csv:CSVIngestor',
            'access = ingestors.tabular.access:AccessIngestor',
            'xls = ingestors.tabular.xls:ExcelIngestor',
            'xlsx = ingestors.tabular.xlsx:ExcelXMLIngestor',
            'ods = ingestors.tabular.ods:OpenOfficeSpreadsheetIngestor',
            'mbox = ingestors.email.mbox:MboxFileIngestor',
            'dbf = ingestors.tabular.dbf:DBFIngestor',
        ]
    }
)
