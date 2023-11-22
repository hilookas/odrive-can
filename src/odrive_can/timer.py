#!/usr/bin/env python3
"""
 Timing utilities

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""

import time


class Timer:
    """Timer class, including timeout"""

    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = time.time()

    def is_timeout(self):
        """Check if timeout has expired"""
        return time.time() - self.start_time > self.timeout

    def reset(self):
        """Reset timer"""
        self.start_time = time.time()

    def elapsed(self):
        """Return elapsed time since timer was started"""
        return time.time() - self.start_time
