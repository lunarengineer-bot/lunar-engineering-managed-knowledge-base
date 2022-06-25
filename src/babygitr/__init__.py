"""Expose the baby-gitr API."""

with open('../../VERSION') as verfile:
    __version__ = verfile.read()
__all__ = ["repowatcher"]
