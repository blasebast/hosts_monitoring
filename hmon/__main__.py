#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main entry point for hosts-monitoring CLI."""

import sys

# Import from justrun for compatibility
import sys
import os

# Add parent directory to path to allow importing justrun
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from justrun import main

if __name__ == '__main__':
    sys.exit(main())
