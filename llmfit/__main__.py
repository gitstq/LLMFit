"""
__main__.py - 支持 python -m llmfit 运行

作为包的入口点，将调用转发到cli.main()。
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
