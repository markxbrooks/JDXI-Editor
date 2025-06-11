from typing import Dict

from jdxi_editor.log.logger import Logger as log


def log_changes(previous_data: Dict, current_data: Dict) -> None:
    """
    Log changes between previous and current JSON data at INFO level.

    :param previous_data: Dict
    :param current_data: Dict
    :return: None
    """
    changes = []

    # Compare all keys in current data with previous data
    for key, current_value in current_data.items():
        previous_value = previous_data.get(key)
        if previous_value != current_value:
            changes.append(
                {
                    "parameter": key,
                    "previous": previous_value,
                    "current": current_value,
                    "difference": current_value - previous_value
                    if isinstance(current_value, (int, float))
                    and isinstance(previous_value, (int, float))
                    else None,
                }
            )

    # If there are changes, log them
    if changes:
        log.message("Parameter changes detected:")
        for change in changes:
            diff_str = (
                f" (Δ: {change['difference']})"
                if change["difference"] is not None
                else ""
            )
            log.message(
                f"  {change['parameter']}: {change['previous']} → {change['current']}{diff_str}"
            )
    else:
        log.message("No parameter changes detected")
