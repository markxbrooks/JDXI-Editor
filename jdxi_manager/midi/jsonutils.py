import json
import logging


def log_json(data):
    """Helper function to log JSON data as a single line."""
    # Ensure `data` is a dictionary, if it's a string, try parsing it as JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            logging.error("Invalid JSON string provided.")
            return

    # Serialize the JSON into a single line string (compact form)
    compact_json = json.dumps(data)

    # Log the JSON in a single line
    logging.info(compact_json)


def log_changes(previous_data, current_data):
    """Log changes between previous and current JSON data at INFO level."""
    changes = []

    # Compare all keys in current data with previous data
    for key, current_value in current_data.items():
        previous_value = previous_data.get(key)
        if previous_value != current_value:
            changes.append({
                'parameter': key,
                'previous': previous_value,
                'current': current_value,
                'difference': current_value - previous_value if isinstance(current_value,
                                                                           (int, float)) and isinstance(
                    previous_value, (int, float)) else None
            })

    # If there are changes, log them
    if changes:
        logging.info("Parameter changes detected:")
        for change in changes:
            diff_str = f" (Δ: {change['difference']})" if change['difference'] is not None else ""
            logging.info(f"  {change['parameter']}: {change['previous']} → {change['current']}{diff_str}")
    else:
        logging.debug("No parameter changes detected")
