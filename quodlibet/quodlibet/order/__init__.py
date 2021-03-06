# -*- coding: utf-8 -*-
# Copyright 2006 Joe Wreschnig
#           2016 Nick Boultbee
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from quodlibet import _


class Order(object):
    """Base class for all play orders"""
    name = "unknown_order"
    display_name = _("Unknown")
    accelerated_name = _("_Unknown")
    replaygain_profiles = ["track"]
    is_shuffle = False
    priority = 100

    def __init__(self):
        """Must have a zero-arg constructor"""
        pass

    def next(self, playlist, iter):
        """Not called directly, but the default implementation of
        `next_explicit` and `next_implicit` both just call this. """
        raise NotImplementedError

    def previous(self, playlist, iter):
        """Not called directly, but the default implementation of
        `previous_explicit` calls this.
        Right now there is no such thing as `previous_implicit`."""
        raise NotImplementedError

    def set(self, playlist, iter):
        """Not called directly, but the default implementations of
        `set_explicit` and `set_implicit` call this. """
        return iter

    def next_explicit(self, playlist, iter):
        """Not called directly, but the default implementations of
       `set_explicit` and `set_implicit` call this."""
        return self.next(playlist, iter)

    def next_implicit(self, playlist, iter):
        """Called when a song ends passively, e.g. it plays through."""
        return self.next(playlist, iter)

    def previous_explicit(self, playlist, iter):
        """Called when the user presses a "Previous" button."""
        return self.previous(playlist, iter)

    def set_explicit(self, playlist, iter):
        """Called when the user manually selects a song (at `iter`).
        If desired the play order can override that, or just
        log it and return the iter again.

        If the play order returns `None`,
        no action will be taken by the player."""
        return self.set(playlist, iter)

    def set_implicit(self, playlist, iter):
        """Called when the song is set by a means other than the UI."""
        return self.set(playlist, iter)

    def reset(self, playlist):
        """Called when there is no song ready to prepare for a new order.
        Implementations should reset the state of the current order,
        e.g. forgetting history / clearing pre-cached orders."""
        pass

    def __str__(self):
        """By default there is no interesting state"""
        return "<%s>" % self.display_name


class OrderRemembered(Order):
    """Shared class for all the shuffle modes that keep a memory
    of their previously played songs."""

    def __init__(self):
        super(OrderRemembered, self).__init__()
        self._played = []

    def next(self, playlist, iter):
        if iter is not None:
            self._played.append(playlist.get_path(iter).get_indices()[0])

    def previous(self, playlist, iter):
        try:
            path = self._played.pop()
        except IndexError:
            return None
        else:
            return playlist.get_iter(path)

    def set(self, playlist, iter):
        if iter is not None:
            self._played.append(playlist.get_path(iter).get_indices()[0])
        return iter

    def reset(self, playlist):
        del(self._played[:])


class OrderInOrder(Order):
    """Keep to the order of the supplied playlist"""
    name = "in_order"
    display_name = _("In Order")
    accelerated_name = _("_In Order")
    replaygain_profiles = ["album", "track"]
    priority = 0

    def next(self, playlist, iter):
        if iter is None:
            return playlist.get_iter_first()
        else:
            return playlist.iter_next(iter)

    def previous(self, playlist, iter):
        if len(playlist) == 0:
            return None
        elif iter is None:
            return playlist[(len(playlist) - 1,)].iter
        else:
            path = max(1, playlist.get_path(iter).get_indices()[0])
            try:
                return playlist.get_iter((path - 1,))
            except ValueError:
                return None
