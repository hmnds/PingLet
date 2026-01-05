#!/usr/bin/env python3
"""Worker entry point for PingLet scheduler service."""
from app.worker.scheduler import start_scheduler

if __name__ == "__main__":
    start_scheduler()

