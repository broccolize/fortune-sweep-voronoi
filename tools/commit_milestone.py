"""Commit selected paths using the owner's personal-project milestone date.

Usage: python tools/commit_milestone.py DATE MESSAGE -- path ...
Repository identity must already be configured locally. No remote is contacted.
"""
from datetime import date
import os
import subprocess
import sys


def main():
    day, message, separator, *paths = sys.argv[1:]
    date.fromisoformat(day)
    if separator != '--' or not paths:
        raise SystemExit('Expected DATE MESSAGE -- path ...')
    subprocess.run(['git', 'add', '--', *paths], check=True)
    env = os.environ.copy()
    env['GIT_AUTHOR_DATE'] = env['GIT_COMMITTER_DATE'] = day + 'T12:00:00+08:00'
    subprocess.run(['git', 'commit', '-m', message], check=True, env=env)


if __name__ == '__main__':
    main()
