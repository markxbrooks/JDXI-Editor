from jdxi_editor.midi.sysex.sections import SysExSection


def log_changes(previous_data, current_data):
    """Log changes between previous and current JSON data."""
    changes = []
    if not current_data or not previous_data:
        return
    for key, current_value in current_data.items():
        previous_value = previous_data.get(key)
        if previous_value != current_value:
            changes.append((key, previous_value, current_value))

    changes = [
        change
        for change in changes
        if change[0]
        not in [
            SysExSection.JD_XI_HEADER,
            SysExSection.ADDRESS,
            SysExSection.TEMPORARY_AREA,
            SysExSection.TONE_NAME,
        ]
    ]

    if changes:
        # log.message("Changes detected:")
        for key, prev, curr in changes:
            pass
            # log.message(
            #     f"\n===> Changed Parameter: {key}, Previous: {prev}, Current: {curr}"
            # )
    else:
        pass
        # --- log.message("No changes detected.")
