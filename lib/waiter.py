"""Generic wait/poll utilities for ACM switchover workflows."""

from __future__ import annotations

import logging
import time
from typing import Callable, Optional, Tuple

ConditionFn = Callable[[], Tuple[bool, str]]


def wait_for_condition(
    description: str,
    condition_fn: ConditionFn,
    *,
    timeout: int = 600,
    interval: int = 30,
    fast_interval: Optional[int] = None,
    fast_timeout: int = 0,
    allow_success_after_timeout: bool = False,
    logger: logging.Logger,
) -> bool:
    """Poll until a condition succeeds or timeout expires."""

    start_time = time.time()
    logger.info("Waiting for %s (timeout: %ss)...", description, timeout)

    while time.time() - start_time < timeout:
        done, detail = condition_fn()

        if done:
            if detail:
                logger.info("%s complete: %s", description, detail)
            else:
                logger.info("%s complete", description)
            return True

        elapsed = int(time.time() - start_time)
        if detail:
            logger.debug("%s in progress: %s (elapsed: %ss)", description, detail, elapsed)
        else:
            logger.debug("%s in progress (elapsed: %ss)", description, elapsed)

        sleep_interval = interval
        if fast_interval:
            if fast_timeout <= 0 or elapsed < fast_timeout:
                sleep_interval = fast_interval
        time.sleep(sleep_interval)

    if allow_success_after_timeout:
        done, detail = condition_fn()
        if done:
            if detail:
                logger.info("%s complete: %s", description, detail)
            else:
                logger.info("%s complete", description)
            return True
        elif detail:
            elapsed = int(time.time() - start_time)
            logger.debug("%s in progress: %s (elapsed: %ss)", description, detail, elapsed)

    logger.warning("%s not complete after %ss timeout", description, timeout)
    return False
