class EffectsData:
    """Collection of ui lists for Effects"""

    rate_note_states = ["RATE", "NOTE"]

    efx1_types = ["Thru", "DISTORTION", "FUZZ", "COMPRESSOR", "BIT CRUSHER"]
    efx1_type_values = [0, 1, 2, 3, 4]

    efx2_types = ["OFF", "FLANGER", "PHASER", "RING MOD", "SLICER"]
    efx2_type_values = [0, 5, 6, 7, 8]

    output_assignments = ["DIR", "EFX2"]

    effects_generic_types = ["0", "1", "2", "3", "4", "5"]

    switch_states = ["OFF", "ON"]

    flanger_notes = [
        "1/96",
        "1/64",
        "1/48",
        "1/32",
        "1/24",
        "3/64",
        "1/16",
        "1/12",
        "3/32",
        "1/8",
        "1/6",
        "3/16",
        "1/4",
        "1/3",
        "3/8",
        "1/2",
        "2/3",
        "3/4",
        "1",
        "4/3",
        "3/2",
        "2",
    ]

    # Compression ratios
    compression_ratios = [
        "  1:1",
        "  2:1",
        "  3:1",
        "  4:1",
        "  5:1",
        "  6:1",
        "  7:1",
        "  8:1",
        "  9:1",
        " 10:1",
        " 20:1",
        " 30:1",
        " 40:1",
        " 50:1",
        " 60:1",
        " 70:1",
        " 80:1",
        " 90:1",
        "100:1",
        " inf:1",
    ]
    # Compression attack times
    compression_attack_times = [
        "0.05",
        "0.06",
        "0.07",
        "0.08",
        "0.09",
        "0.10",
        "0.20",
        "0.30",
        "0.40",
        "0.50",
        "0.60",
        "0.70",
        "0.80",
        "0.90",
        "1.0",
        "2.0",
        "3.0",
        "4.0",
        "5.0",
        "6.0",
        "7.0",
        "8.0",
        "9.0",
        "10.0",
        "15.0",
        "20.0",
        "25.0",
        "30.0",
        "35.0",
        "40.0",
        "45.0",
        "50.0",
    ]

    # Compression release times
    compression_release_times = [
        "0.05",
        "0.07",
        "0.10",
        "0.50",
        "1",
        "5",
        "10",
        "17",
        "25",
        "50",
        "75",
        "100",
        "200",
        "300",
        "400",
        "500",
        "600",
        "700",
        "800",
        "900",
        "1000",
        "1200",
        "1500",
        "2000",
    ]
