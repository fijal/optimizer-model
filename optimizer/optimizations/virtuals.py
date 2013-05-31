from .base import BaseOptimization
from .utils import OpDispatcher
from .. import Operations, Types
from ..optimizer import BaseValue


class Virtualize(BaseOptimization):
    dispatcher = OpDispatcher()

    @dispatcher.register(Operations.NEW)
    def optimize_NEW(self, optimizer, operation):
        optimizer.make_equal_to(operation, VirtualValue(operation))

    @dispatcher.register(Operations.SETFIELD)
    def optimize_SETFIELD(self, optimizer, operation):
        value = optimizer.getvalue(operation.getarg(0))
        if value.is_virtual():
            value.setfield(optimizer, optimizer.getvalue(operation.getarg(1)))
        else:
            return self.prev.handle(optimizer, operation)

    def optimize_default(self, optimizer, operation):
        for arg in operation.getarglist():
            value = optimizer.getvalue(arg)
            if value.is_virtual():
                value.force(optimizer, self.prev)
        return self.prev.handle(optimizer, operation)

    handle = dispatcher.build_dispatcher(default=optimize_default)


class VirtualValue(BaseValue):
    def __init__(self, original_operation, setfield_val=None):
        super(VirtualValue, self).__init__()
        self.original_operation = original_operation
        self.setfield_val = setfield_val

    def is_virtual(self):
        return True

    def force(self, optimizer, optimization):
        p = optimizer.add_operation(Types.REF, Operations.NEW, [], optimizer=optimization)
        optimizer.make_equal_to(self.original_operation, p)

    def setfield(self, optimizer, value):
        optimizer.make_equal_to(self.original_operation, VirtualValue(self.original_operation, value))