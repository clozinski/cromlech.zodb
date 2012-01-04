# -*- coding: utf-8 -*-

import zope.component.interfaces
import zope.component.persistentregistry
import zope.interface
import zope.location

from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from zope.cachedescriptors.property import Lazy

from cromlech.zodb import interfaces


class PossibleSite(object):
    """a base implementation of a possible site, to be used as
    a mixin
    """
    zope.interface.implements(zope.component.interfaces.IPossibleSite)

    _sm = None

    def getSiteManager(self):
        if self._sm is not None:
            return self._sm
        else:
            raise zope.component.interfaces.ComponentLookupError(
                'no site manager defined')

    def setSiteManager(self, sm):
        if zope.component.interfaces.ISite.providedBy(self):
            raise TypeError("Already a site")

        if zope.component.interfaces.IComponentLookup.providedBy(sm):
            self._sm = sm
        else:
            raise ValueError('setSiteManager requires an IComponentLookup')

        zope.interface.alsoProvides(self, zope.component.interfaces.ISite)


class _LocalAdapterRegistry(
    zope.component.persistentregistry.PersistentAdapterRegistry,
    zope.location.Location,
    ):
    """
    a location adapter registry used by LocalSiteManager
    """


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


class LocalSiteManager(
    PersitentOOBTree,
    zope.component.persistentregistry.PersistentComponents):
    """Local Site Manager implementation for zodb
    Use this to have an application with eg. local utility.
    """
    zope.interface.implements(interfaces.ILocalSiteManager)

    subs = ()

    def _setBases(self, bases):

        # Update base subs
        for base in self.__bases__:
            if ((base not in bases)
                 and interfaces.ILocalSiteManager.providedBy(base)):
                base.removeSub(self)

        for base in bases:
            if ((base not in self.__bases__)
                 and interfaces.ILocalSiteManager.providedBy(base)):
                base.addSub(self)

        super(LocalSiteManager, self)._setBases(bases)

    def __init__(self, site):
        PersitentOOBTree.__init__(self)
        zope.component.persistentregistry.PersistentComponents.__init__(self)

        # Set base site manager
        # ATM in cromlech we are always the root
        next = zope.component.getGlobalSiteManager()
        self.__bases__ = (next, )

        # Locate the site manager
        site.setSiteManager(self)
        self.__parent__ = site
        self.__name__ = '++etc++site'

    def _init_registries(self):
        self.adapters = _LocalAdapterRegistry()
        self.utilities = _LocalAdapterRegistry()
        self.adapters.__parent__ = self.utilities.__parent__ = self
        self.adapters.__name__ = u'adapters'
        self.utilities.__name__ = u'utilities'

    def addSub(self, sub):
        """See interfaces.registration.ILocatedRegistry"""
        self.subs += (sub, )

    def removeSub(self, sub):
        """See interfaces.registration.ILocatedRegistry"""
        self.subs = tuple([s for s in self.subs if s is not sub])


@zope.component.provideAdapter
@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zope.component.interfaces.IComponentLookup)
def SiteManagerAdapter(ob):
    """An adapter from ILocation to IComponentLookup.

    The ILocation is interpreted flexibly, we just check for
    ``__parent__``.
    """
    current = ob
    while True:
        if zope.component.interfaces.ISite.providedBy(current):
            return current.getSiteManager()
        current = getattr(current, '__parent__', None)
        if current is None:
            # It is not a location or has no parent, so we return the global
            # site manager
            return zope.component.getGlobalSiteManager()

# TODO :
#   zope.site propagate IObjectMovedEvent to LocalSiteManager, shall we ?
