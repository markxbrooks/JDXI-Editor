"""
Profiling decorator
"""

import cProfile
import io
import logging
import pstats
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

_log = logging.getLogger(__name__)


def profiling_decorator(
    sortby: str = "cumtime", top_n: int = 50
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to profile a function and log its performance.

    Output is written to the module logger and to stdout (flushed) so it appears
    in log files and in the terminal when the function returns (e.g. after
    closing the app when used on main()).

    :param sortby: str - Sorting criteria for profiling results ('cumtime' or 'tottime').
    :param top_n: int - Number of top entries to show in the profiling results.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            profiler = cProfile.Profile()
            profiler.enable()  # Start profiling

            # Execute the wrapped function
            result = func(*args, **kwargs)

            profiler.disable()  # Stop profiling

            # Process profiling results
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
            ps.print_stats(top_n)  # Print the top N entries
            report = s.getvalue()

            # Log so it appears in log files (visible even if terminal is closed)
            _log.info("Profiling results for %s:\n%s", func.__name__, report)
            # Also print and flush so terminal users see it when the function returns
            print(f"Profiling results for {func.__name__}:\n{report}", flush=True)

            return result

        return wrapper

    return decorator
