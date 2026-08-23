"""Tkinter GUI adapter, imported only through an explicit GUI entry point."""

from __future__ import annotations


def main() -> int:
    from .app import main as app_main

    return app_main()


__all__ = ["main"]
