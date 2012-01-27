# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------------
This source file is part of OSTIS (Open Semantic Technology for Intelligent Systems)
For the latest info, see http://www.ostis.net

Copyright (c) 2011 OSTIS

OSTIS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OSTIS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OSTIS.  If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
"""
from distutils.core import setup


#import srs
import sys
import sys
sys.path.append('./SCnML2SC')


from SCnML2SC import *
import py2exe
from lxml import etree 


py2exe_options = dict(
    includes = ['SCnML2SC.grammar','SCnML2SC.translator',]
)

setup(
    version = u"0.1.0",
    # targets to build
    description = u"SCnML2SC",
    name = u"SCnML2SC.exe",
    # targets to build
    console = ["./SCnML2SC/SCnML2SC.py"],
	options = dict(py2exe = py2exe_options)
)
