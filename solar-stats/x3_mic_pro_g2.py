import voluptuous as vol


from utils import div10, div100, to_signed, to_signed32, twoway_div10, u16_packer3


class X3MicProG2():
    """X3MicProG2 v3.008.10"""

    def _decode_run_mode(run_mode):
        return {
            0: "Wait",
            1: "Check",
            2: "Normal",
            3: "Fault",
            4: "Permanent Fault",
            5: "Update",
        }.get(run_mode)


    def response_decoder(data):
        return {
            "Grid 1 Voltage (V)": (div10(data[0])),
            "Grid 2 Voltage (V)": (div10(data[1])),
            "Grid 3 Voltage (V)": (div10(data[2])),
            "Grid 1 Current (A)": (twoway_div10(data[3])),
            "Grid 2 Current (A)": (twoway_div10(data[4])),
            "Grid 3 Current (A)": (twoway_div10(data[5])),
            "Grid 1 Power (W)": (to_signed(data[6])),
            "Grid 2 Power (W)": (to_signed(data[7])),
            "Grid 3 Power (W)": (to_signed(data[8])),
            "PV1 Voltage (V)": (div10(data[9])),
            "PV2 Voltage (V)": (div10(data[10])),
            "PV3 Voltage (V)": (div10(data[11])),
            "PV1 Current (A)": (div10(data[12])),
            "PV2 Current (A)": (div10(data[13])),
            "PV3 Current (A)": (div10(data[14])),
            "PV1 Power (W)": (data[15]),
            "PV2 Power (W)": (data[16]),
            "PV3 Power (W)": (data[17]),
            "Grid 1 Frequency (HZ)": (div100(data[18])),
            "Grid 2 Frequency (HZ)": (div100(data[19])),
            "Grid 3 Frequency (HZ)": (div100(data[20])),
            # "Run Mode": (21, Units.NONE),
            # "Total Yield": (pack_u16(22, 23), Total(Units.KWH), div10),
            # "Daily Yield": (24, Units.KWH, div10),
            # "Feed-in Power ": (pack_u16(72, 73), Units.W, to_signed32),
            # "Total Feed-in Energy": (pack_u16(74, 75), Total(Units.KWH), div100),
            # "Total Consumption": (pack_u16(76, 77), Total(Units.KWH), div100),
            "Run Mode": (X3MicProG2._decode_run_mode(21)),
            "Total Yield (KWH)": (div10(u16_packer3(data[22],data[23]))),
            "Daily Yield (KWH)": (div10(data[24])),
            "Feed-in Power (W)": (to_signed32(u16_packer3(data[72], data[73]))),
            "Total Feed-in Energy (KWH)": (div100(u16_packer3(data[74], data[75]))),
            "Total Consumption (KWH)": (div100(u16_packer3(data[77],data[77]))),
        }

    # pylint: enable=duplicate-code