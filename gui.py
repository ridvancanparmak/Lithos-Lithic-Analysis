# -*- coding: utf-8 -*-
"""Lithos v1.0.1; PyInstaller entry point and built executable smoke test."""
from __future__ import annotations
import sys

def main():
    if len(sys.argv)>1 and sys.argv[1]=='--self-test':
        # Also works in the PyInstaller --windowed executable; writes a log.
        from lithos.preflight import main as preflight_main
        if len(sys.argv)<3:
            sys.argv=[sys.argv[0]]
        else:
            sys.argv=[sys.argv[0],'--output',sys.argv[2]]
        return preflight_main()
    from lithos.app import launch
    return launch()

if __name__=='__main__':
    raise SystemExit(main())
