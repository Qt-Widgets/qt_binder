#------------------------------------------------------------------------------
#
#  Copyright (c) 2014-2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

from collections import defaultdict


class abstractclassmethod(classmethod):
    """ A backport of the Python 3's abc.abstractclassmethod.

    """
    __isabstractmethod__ = True

    def __init__(self, func):
        func.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(func)


class LoopbackContext(object):
    """ A context manager generated by LoopbackGuard.

    Instances of this class manage acquiring and releasing the lock
    items for instances of LoopbackGuard.

    """
    __slots__ = ('_guard', '_items')

    def __init__(self, guard, items):
        """ Initialize a LoopbackContext

        Parameters
        ----------
        guard : LoopbackGuard
            The loopback guard instance for which we will acquire the
            lock for the items.

        items : iterable
            An iterable items which will be passed to the 'acquire'
            method on the loopback guard.

        """
        self._guard = guard
        self._items = tuple(items)

    def __enter__(self):
        """ Acquire the guard lock on the lock items.

        """
        self._guard.acquire(self._items)

    def __exit__(self, exc_type, exc_value, traceback):
        """ Release the guard lock on the lock items.

        """
        self._guard.release(self._items)


class LoopbackGuard(object):
    """ A guard object to protect against feedback loops.

    Instances of this class are used by objects to protect against
    loopback conditions while updating attributes. Instances of this
    class are callable and return a guarding context manager for the
    provided lock items. The guard can be tested for a locked item
    using the `in` keyword.

    """
    __slots__ = ('locked_items',)

    def __init__(self):
        """ Initialize a loopback guard.

        """
        self.locked_items = None

    def __call__(self, *items):
        """ Return a context manager which will guard the given items.

        Parameters
        ----------
        items
            The items for which to acquire the guard from within the
            returned context manager. These items must be hashable.

        Returns
        -------
        result : LoopbackContext
            A context manager which will acquire the guard for the
            provided items.

        """
        return LoopbackContext(self, items)

    def __contains__(self, item):
        """ Returns whether or not the given item is currently guarded.

        Parameters
        ----------
        item : object
            The item to check for guarded state.

        Returns
        -------
        result : bool
            True if the item is currently guarded, False otherwise.

        """
        locked_items = self.locked_items
        if locked_items is not None:
            return item in locked_items
        return False

    def __repr__(self):
        if self.locked_items is None:
            items = None
        else:
            items = dict(self.locked_items)
        return '<{0.__name__}: {1!r}>'.format(type(self), items)

    def acquire(self, items):
        """ Acquire the guard for the given items.

        This method is normally called by the LoopbackContext returned
        by calling this instance. User code should not typically call
        this method directly. It is safe to call this method multiple
        times for and item, provided it is paired with the same number
        of calls to release(...). The guard will be released when the
        acquired count on the item reaches zeros.

        Parameters
        ----------
        items : iterable
            An iterable of objects for which to acquire the guard. The
            items must be hashable.

        """
        locked_items = self.locked_items
        if locked_items is None:
            locked_items = self.locked_items = defaultdict(int)
        for item in items:
            locked_items[item] += 1

    def release(self, items):
        """ Release the guard for the given lock items.

        This method is normally called by the LoopbackContext returned
        by calling this instance. User code should not normally call
        this method directly. It is safe to call this method multiple
        times for and item, provided it is paired with the same number
        of calls to acquire(...). The guard will be released when the
        acquired count on the item reaches zeros.

        Parameters
        ----------
        items : iterable
            An iterable of objects for which to release the guard. The
            items must be hashable.

        """
        locked_items = self.locked_items
        if locked_items is not None:
            for item in items:
                locked_items[item] -= 1
                if locked_items[item] <= 0:
                    del locked_items[item]
            if not locked_items:
                self.locked_items = None
