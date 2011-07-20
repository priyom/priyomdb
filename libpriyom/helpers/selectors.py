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
