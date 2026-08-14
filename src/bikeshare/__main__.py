"""Allow ``python -m bikeshare``."""

from __future__ import annotations

from .cli import main

raise SystemExit(main())
