import cProfile
import io
import pstats
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def profiling_decorator(
    sortby: str = "cumtime", top_n: int = 50
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to profile a function and log its performance.

    :param sortby: str - Sorting criteria for profiling results ('cumtime' or 'tottime').
    :param top_n: int - Number of top entries to display in the profiling results.
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

            # Log the profiling results (replace with your logging mechanism)
            print(f"Profiling results for {func.__name__}:\n{s.getvalue()}")

            return result

        return wrapper

    return decorator
