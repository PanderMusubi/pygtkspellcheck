# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
# Copyright (C) 2012, Carlos Jenkins <carlos@jenkins.co.cr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Query the ISO 639/3166 database about a country or a language. The locales
database contains ISO 639 languages definitions and ISO 3166 countries
definitions. This package provides translation for countries and languages names
if iso-codes package is installed (Ubuntu/Debian).

@see utils/locales/build.py to know the database tables and structure.
"""

import gettext
import os
import os.path
import sqlite3
import sys

# Public Objects
__all__ = ['Country', 'Language', 'LanguageNotFound',
           'CountryNotFound', 'code_to_name']

# Translation
_translator_language = gettext.translation('iso_639').gettext
_translator_country = gettext.translation('iso_3166').gettext

# Decides where the database is located. If an application provides an
# os.path.get_data_path monkey patch to determine the path where resources
# are located it uses this. If not it searches in the directory of this source
# code file.
__path__ = None
if hasattr(os.path, 'get_data_path'):
    __path__ = os.path.get_data_path(__file__)
    if not os.path.isfile(os.path.join(__path__, 'locales.db')):
        __path__ = None
if __path__ is None:
    __path__ = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

# Loading the Database
_database = sqlite3.connect(os.path.join(__path__, 'locales.db'))

# Exceptions
class LanguageNotFound(Exception):
    """
    The specified language wasn't found in the database.
    """
    
class CountryNotFound(Exception):
    """
    The specified country wasn't found in the database.
    """

class Country(object):
    def __init__(self, rowid):
        country = _database.execute('SELECT * FROM countries WHERE rowid == ?', (rowid,)).fetchone()
        self.name = country[0]
        self.official_name = country[1]
        self.alpha_2 = country[2]
        self.alpha_3 = country[3]
        self.numeric = country[4]
        self.translation = _translator_country(self.name)
        
    @classmethod
    def get_country(cls, code, codec):
        country = _database.execute('SELECT rowid FROM countries WHERE %s == ?' % (codec), (code,)).fetchone()
        if country:
            return cls(country[0])
        raise CountryNotFound('code: %s, codec: %s' % (code, codec))
    
    @classmethod
    def by_alpha_2(cls, code):
        return Country.get_country(code, 'alpha_2')
    
    @classmethod
    def by_alpha_3(cls, code):
        return Country.get_country(code, 'alpha_3')
    
    @classmethod
    def by_numeric(cls, code):
        return Country.get_country(code, 'numeric')
   
class Language(object):
    def __init__(self, rowid):
        language = _database.execute('SELECT * FROM languages WHERE rowid == ?', (rowid,)).fetchone()
        self.name = language[0]
        self.iso_639_2B = language[1]
        self.iso_639_2T = language[2]
        self.iso_639_1 = language[3]
        self.translation = _translator_language(self.name)
        
    @classmethod
    def get_language(cls, code, codec):
        language = _database.execute('SELECT rowid FROM languages WHERE %s == ?' % (codec), (code,)).fetchone()
        if language:
            return cls(language[0])
        raise LanguageNotFound('code: %s, codec: %s' % (code, codec))
        
    @classmethod
    def by_iso_639_2B(cls, code):
        return Language.get_language(code, 'iso_639_2B')
    
    @classmethod
    def by_iso_639_2T(cls, code):
        return Language.get_language(code, 'iso_639_2T')
    
    @classmethod
    def by_iso_639_1(cls, code):
        return Language.get_language(code, 'iso_639_1')


def code_to_name(code, separator='_'):
    """
    Get the natural name of a language based on it's code.
    """
    code = code.split(separator)
    if len(code) > 1:
        print(code)
        lang = Language.by_iso_639_1(code[0]).translation
        country = Country.by_alpha_2(code[1]).translation
        return '{lang} ({country})'.format(lang=lang, country=country)
    else:
        return Language.by_iso_639_1(code[0]).translation