# -*- coding: utf-8 -*-

from .interfaces import ILookupNode
from crom import implements, adapter, sources, target, implicit
from crom import IRegistry, ILookup, ComponentLookupError
from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from zope.interface import Interface
from zope.cachedescriptors.property import Lazy
from zope.location import ILocation, LocationProxy, locate


@implements(ILookupNode)
class LookupNode(object):
    """a base implementation of a site
    """
    implements(ILookupNode)
    _registry = None

    def getLocalRegistry(self):
        reg = self._registry
        if not ILocation.providedBy(reg):
            reg = LocationProxy(reg)
            locate(reg, self, '@registry')
        return reg

    def setLocalRegistry(self, reg, locate=locate):
        assert IRegistry.providedBy(reg)
        if locate is not None:
            if ILocation.providedBy(reg):
                locate(reg, self, '@registry')
            else:
                raise TypeError("Can't locate non ILocation registries.")
        self._registry = reg


class PersitentOOBTree(Persistent):
    """A persitent wrapper around a OOBTree"""

    def __init__(self):
        self._data = OOBTree()
        Persistent.__init__(self)
        self.__len = Length()

    @Lazy
    def _PersitentOOBTree__len(self):
        l = Length()
        ol = len(self._data)
        if ol > 0:
            l.change(ol)
        self._p_changed = True
        return l

    def __len__(self):
        return self.__len()

    def __setitem__(self, key, value):
        # make sure our lazy property gets set
        l = self.__len
        self._data[key] = value
        l.change(1)

    def __delitem__(self, key):
        # make sure our lazy property gets set
        l = self.__len
        del self._data[key]
        l.change(-1)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        """See interface `IReadContainer`.
        """
        return self._data[key]

    def get(self, key, default=None):
        """See interface `IReadContainer`.
        """
        return self._data.get(key, default)

    def __contains__(self, key):
        """See interface `IReadContainer`.
        """
        return key in self._data

    has_key = __contains__

    def items(self, key=None):
        return self._data.items(key)

    def keys(self, key=None):
        return self._data.keys(key)

    def values(self, key=None):
        return self._data.values(key)


@adapter
@sources(Interface)
@target(ILookup)
def ClosestLookup(ob):
    current = ob
    while True:
        if ILookupNode.providedBy(current):
            return current.getLocalLookup()
        current = getattr(current, '__parent__', None)
        if current is None:
            return implicit.lookup
