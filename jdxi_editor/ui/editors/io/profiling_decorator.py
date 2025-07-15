import cProfile
import pstats
import io
from functools import wraps

def profiling_decorator(sortby='cumtime', top_n=50):
    """
    Decorator to profile a function and log its performance.

    :param sortby: str - Sorting criteria for profiling results ('cumtime' or 'tottime').
    :param top_n: int - Number of top entries to display in the profiling results.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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