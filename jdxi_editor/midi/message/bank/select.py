"""
JDXI Bank Select values
"""


class JDXiCCBankSelect:
    """
    Represents the Bank Select values for the Roland JD-Xi synthesizer.

    # Note: JD-Xi uses CC#85 for Bank Select MSB instead of standard CC#0
    - MSB (Most Significant Byte): CC#85 (non-standard)
    - LSB (Least Significant Byte): Specific values for bank selection.
    """

    MSB = 85

    class LSB:
        """LSB values for Bank selection."""

        BANK_E_AND_F = 0  # User Banks
        BANK_G_AND_H = 1  # User Banks
        BANK_A_AND_B = 64  # ROM banks
        BANK_C_AND_D = 65  # ROM banks
