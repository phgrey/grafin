# cython: language_level=3
"""Cython accelerated core helpers for event bus dispatching and service lookups."""

cdef class FastEventRouter:
    cdef public dict listeners

    def __init__(self):
        self.listeners = {}

    cpdef list emit_fast(self, str event, list args):
        cdef list results = []
        cdef list target_listeners = self.listeners.get(event, [])
        for listener in target_listeners:
            res = listener(*args)
            if res is not None:
                results.append(res)
        return results
