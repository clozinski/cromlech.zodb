cromelech.zodb
===============

This repository contains software for Cromlech applicatiions to work with the ZODB.   It includes cromlech.connection, initializing the ZODB,  and initializing the applications. 

The most important part for an experienced Zope developer is their replacement for zope.container, 

The Cromlech PersistentTree is basically a cleaned up version of Zope.container.  It is initialized with the line
 self._data = OOBTree()

whereas zope.container for legacy reasons is initialized with: 

 self._SampleContainer__data 

So they are not plug compatible. But doing the clean up is the right way to go.  It would be easy to add a method such that if there were no self._data, it would try to access _SampleContainer_data.
Then grok/zope applications would port over much more easily. And over time new items would have to clean and correct self._data. 

The other thing I like about this approach is that it gets rid of the huge complexity tied in with generating events on all tree accesses.  And it gets rid of trees based on integers, floats, and other indexes, which in reality no one ever uses. 

Great Work.  Thank you. 


 

