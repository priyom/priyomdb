"""
File name: Selectors.py
This file is part of: priyomdb

LICENSE

The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

Alternatively, the contents of this file may be used under the terms of
the GNU General Public license (the  "GPL License"), in which case  the
provisions of GPL License are applicable instead of those above.

FEEDBACK & QUESTIONS

For feedback and questions about priyomdb please e-mail one of the
authors:
    Jonas Wielicki <j.wielicki@sotecware.net>
"""
from storm.locals import *
from storm.variables import IntVariable, FloatVariable

class ObjectFinderError(Exception):
    pass

class ObjectFinder(object):
    def __init__(self, store, targetClass):
        self.store = store
        self.targetClass = targetClass
        
    @staticmethod
    def buildWhere_equals(field, operand):
        return (field == operand)
    
    @staticmethod
    def buildWhere_like(field, operand):
        return Like(field, operand)
    
    @staticmethod
    def buildWhere_null(field, operand):
        return (field == None)
    
    @staticmethod
    def buildWhere_greater(field, operand):
        return (field > operand)
    
    @staticmethod
    def buildWhere_less(field, operand):
        return (field < operand)
        
    @staticmethod
    def buildWhere_gequal(field, operand):
        return (field >= operand)
        
    @staticmethod
    def buildWhere_lequal(field, operand):
        return (field <= operand)
    
    def select(self, field, operator, operand, negate=False, offset=None, limit=None, distinct=False):
        try:
            func = getattr(ObjectFinder, "buildWhere_"+operator)
        except AttributeError:
            raise ObjectFinderError("Operator \"%s\" undefined" % operator)
        if func == ObjectFinder.buildWhere_null and (operand != "" and operand is not None):
            raise ObjectFinderError("Operator \"null\" requires empty operand")
        try:
            field = getattr(self.targetClass, field)
            fieldType = field.variable_factory.func
            if fieldType == IntVariable:
                operand = int(operand)
            elif fieldType == FloatVariable:
                operand = float(operand)
        except AttributeError:
            raise ObjectFinderError("Field \"%s\" undefined" % field)
        where = func(field, operand)
        if negate:
            where = Not(where)
        resultSet = self.store.find(self.targetClass, where)
        resultSet.config(distinct, offset, limit)
        return resultSet
