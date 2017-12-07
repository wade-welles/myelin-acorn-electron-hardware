#!/usr/bin/python

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --------------------------
# fx2_tube_cartridge_adapter
# --------------------------

# by Phillip Pearson

# Adapter board to make it easy to connect an LCSoft Mini board to either an
# Acorn Electron via a Plus 1 cartridge slot, or a BBC Micro or BBC Master via
# the Tube connector, to run Sigrok and David Banks' decode6502 software.

# This also allows connecting a Raspberry Pi running PiTubeDirect to a BBC or
# Electron.  When connected to an Electron, it drives the /TUBE line low on the
# Pi when &FCEx addresses are being accessed (i.e. nINFC='0' and A7:4 = x"E").
# When connected to a BBC, it just buffers the /TUBE line from the Tube
# connetor.


# DONE add a second tube header so BBC folks can pass signals through to a 5V
# tube device and debug the Tube connection.  DECISION: skip this, because a
# two-drive IDE cable will allow putting the board inline with a Tube device
# anyway.

# DONE hook up both bbc_nTUBE and tube_nTUBE to the CPLD, to allow using a Pi on
# a BBC or Master.

# DONE add jumpers from 3V3_PI and 3V3_FX2 to 3V3, to allow not populating the
# regulator

# DONE think about whether we can autodetect stuff (by averaging over a few
# clocks...).  if elk is connected, we'll get cpu_CLK and elk_16MHz, but if a
# beeb is connected, we'll only get cpu_CLK.  counting elk_16MHz crossings per
# cpu_CLK cycle might let us detect elk or bbc.  in fact we can safely say an
# elk is connected if we get *one* edge on elk_16MHz.  so no need for a series
# resistor or jumper on beeb_nTUBE.

# DONE remove /RESET from the CPLD and use a schottky diode + pullup to convert
# that down to 3v3.  It's a slow signal (generated by the keyboard) so it
# doesn't need to go through the CPLD.

# DONE figure out if it's easier to put the tube connector on the same side of
# the board as the cartridge interface -- if it makes the wiring easier or
# harder.  it probably looks nicest up top.  DECISION: next to the cartridge
# interface; otherwise this gets way too complicated.

# DONE Trivial, possibly pointless addition: This can also double as a very
# simple Tube adapter for the Electron, when logic is fitted to match the Tube
# addresses and generate the /TUBE signal).  DECISION: going a bit further and
# making it a PiTubeDirect adapter too.

# DONE check AP6 thread on stardot to see if external tube devices require a
# buffered clock.  If so, there's no point doing this simple option.  DECISION:
# adding a buffered clock because the logic analyzer needs it on the Electron.

# ARCHIVE: not doing this any more; just using a CPLD:

    # nTUBE <= '0' when nINFC = '0' and A(7 downto 4) = x"E" else '1'

    # i.e. nTUBE = !(!nINFC and A7 and A6 and A5 and !A4)
    #            = (((nINFC nand 1) and (A4 nand 1)) and (A7 and A6)) nand (A5)

    # A 74HCT00 for the nands and a 74HCT08 for the ands should do this nicely.

    # nand0 = nINFC nand 1 (= !nINFC)
    # nand1 = A4 nand 1 (= !A4)
    # and0 = nand0 and nand1 (= !nINFC and !A4)
    # and1 = A7 and A6
    # and2 = and0 and and1 (= !nINFC and A7 and A6 and !A4)
    # nTUBE = nand2 = and2 nand A5 (= !(!nINFC and A7 and A6 and A5 and !A4))
    # - 74hct00 + capacitor
    # - 74hct08 + capacitor
    # - 330R/1k output resistor on nTUBE to limit current if plugged into both
    # Electron and BBC for some reason.

import sys, os
here = os.path.dirname(sys.argv[0])
sys.path.insert(0, os.path.join(here, "../../third_party/myelin-kicad.pretty"))
import myelin_kicad_pcb
Pin = myelin_kicad_pcb.Pin


# Cartridge connector
cart_front = myelin_kicad_pcb.Component(
    footprint="myelin-kicad:acorn_electron_cartridge_edge_connector",
    identifier="CART",
    value="edge connector",
    pins=[
        # front of cartridge / bottom layer of PCB
        Pin( "B1", "5V",    "5V"),
        Pin( "B2", "A10"),
        Pin( "B3", "D3",    "cpu_D3"),
        Pin( "B4", "A11"),
        Pin( "B5", "A9"),
        Pin( "B6", "D7",    "cpu_D7"),
        Pin( "B7", "D6",    "cpu_D6"),
        Pin( "B8", "D5",    "cpu_D5"),
        Pin( "B9", "D4",    "cpu_D4"),
        Pin("B10", "nOE2"),
        Pin("B11", "BA7",   "cpu_A7"),
        Pin("B12", "BA6",   "cpu_A6"),
        Pin("B13", "BA5",   "cpu_A5"),
        Pin("B14", "BA4",   "cpu_A4"),
        Pin("B15", "BA3",   "cpu_A3"),
        Pin("B16", "BA2",   "cpu_A2"),
        Pin("B17", "BA1",   "cpu_A1"),
        Pin("B18", "BA0",   "cpu_A0"),
        Pin("B19", "D0",    "cpu_D0"),
        Pin("B20", "D2",    "cpu_D2"),
        Pin("B21", "D1",    "cpu_D1"),
        Pin("B22", "GND",   "GND"),
        # rear of cartridge / top layer of PCB
        Pin( "A1", "5V",    "5V"),
        Pin( "A2", "nOE"),
        Pin( "A3", "nRST",  "cpu_nRST"),
        # A4 is RnW on the Elk, and on the master for &FCxx, so it's safe to use
        # this for the Tube, but not for the logic analyzer.
        Pin( "A4", "RnW",   "cpu_RnW"),
        Pin( "A5", "A8"),
        Pin( "A6", "A13"),
        Pin( "A7", "A12"),
        Pin( "A8", "PHI0",  "cpu_CLK"),
        Pin( "A9", "-5V"),
        Pin("A10", "NC"),
        Pin("A11", "READY", "elk_READY_master_RnW"),
        Pin("A12", "nNMI",  "cpu_nNMI"),
        Pin("A13", "nIRQ",  "cpu_nIRQ"),
        Pin("A14", "nINFC", "elk_nINFC"),
        Pin("A15", "nINFD"),
        Pin("A16", "ROMQA"),
        Pin("A17", "16MHZ", "elk_16MHz"),
        Pin("A18", "nROMSTB"),
        Pin("A19", "ADOUT"),
        Pin("A20", "ADGND"),
        Pin("A21", "ADIN"),
        Pin("A22", "GND",   "GND"),
    ],
)

tube = myelin_kicad_pcb.Component(
    footprint="myelin-kicad:header_2x20_100mil",
    identifier="TUBE",
    value="tube",
    pins=[
        Pin( 1, "0V", "GND"),
        Pin( 2, "RnW", "cpu_RnW"),
        Pin( 3, "0V", "GND"),
        Pin( 4, "2MHzE", "cpu_CLK"),
        Pin( 5, "0V", "GND"),
        Pin( 6, "/IRQ", "cpu_nIRQ"),
        Pin( 7, "0V", "GND"),
        Pin( 8, "/TUBE", "bbc_nTUBE"),
        Pin( 9, "0V", "GND"),
        Pin(10, "/RST", "cpu_nRST"),
        Pin(11, "0V", "GND"),
        Pin(12, "D0", "cpu_D0"),
        Pin(13, "0V", "GND"),
        Pin(14, "D1", "cpu_D1"),
        Pin(15, "0V", "GND"),
        Pin(16, "D2", "cpu_D2"),
        Pin(17, "0V", "GND"),
        Pin(18, "D3", "cpu_D3"),
        Pin(19, "0V", "GND"),
        Pin(20, "D4", "cpu_D4"),
        Pin(21, "0V", "GND"),
        Pin(22, "D5", "cpu_D5"),
        Pin(23, "0V", "GND"),
        Pin(24, "D6", "cpu_D6"),
        Pin(25, "0V", "GND"),
        Pin(26, "D7", "cpu_D7"),
        Pin(27, "0V", "GND"),
        Pin(28, "A0", "cpu_A0"),
        Pin(29, "0V", "GND"),
        Pin(30, "A1", "cpu_A1"),
        Pin(31, "+5V", "5V"),
        Pin(32, "A2", "cpu_A2"),
        Pin(33, "+5V", "5V"),
        Pin(34, "A3", "cpu_A3"),
        Pin(35, "+5V", "5V"),
        Pin(36, "A4", "cpu_A4"),
        Pin(37, "+5V", "5V"),
        Pin(38, "A5", "cpu_A5"),
        Pin(39, "+5V", "5V"),
        Pin(40, "A6", "cpu_A6"),
    ],
)

# 25 pins from the cartridge + tube port
# minus IRQ, NMI, READY, /RESET, /TUBE = 20
# 14 pins to the Raspberry Pi
# total 34, which is exactly what we have

cpld = myelin_kicad_pcb.Component(
    footprint="myelin-kicad:xilinx_vqg44",
    identifier="PL1",
    value="XC9572XL",
    buses=["cpu_A", "cpu_D", "tube_D"],
    pins=[
        Pin(39, "P1.2", "cpu_D4"),
        Pin(40, "P1.5", "cpu_D5"),
        Pin(41, "P1.6", "cpu_D6"),
        Pin(42, "P1.8", "elk_nINFC"),
        Pin(43, "P1.9-GCK1", "cpu_D7"),
        Pin(44, "P1.11-GCK2", "cpu_A0"),
        Pin( 1, "P1.14-GCK3", "elk_16MHz"),
        Pin( 2, "P1.15", "cpu_A1"),
        Pin( 3, "P1.17", "cpu_A2"),
        Pin( 4, "GND", "GND"),
        Pin( 5, "P3.2", "cpu_A4"),
        Pin( 6, "P3.5", "cpu_A5"),
        Pin( 7, "P3.8", "cpu_A6"),
        Pin( 8, "P3.9", "tube_CLK"),
        Pin( 9, "TDI", "cpld_TDI"),
        Pin(10, "TMS", "cpld_TMS"),
        Pin(11, "TCK", "cpld_TCK"),
        Pin(12, "P3.11", "tube_D0"),
        Pin(13, "P3.14", "tube_D3"),
        Pin(14, "P3.15", "tube_D1"),
        Pin(15, "VCCINT_3V3", "3V3"),
        Pin(16, "P3.17", "tube_D7"),
        Pin(17, "GND", "GND"),
        Pin(18, "P3.16", "tube_D2"),
        Pin(19, "P4.2", "tube_D6"),
        Pin(20, "P4.5", "tube_D4"),
        Pin(21, "P4.8", "tube_D5"),
        Pin(22, "P4.11", "tube_A0"),
        Pin(23, "P4.14", "tube_nTUBE"),
        Pin(24, "TDO", "cpld_TDO"),
        Pin(25, "GND", "GND"),
        Pin(26, "VCCIO_2V5_3V3", "3V3"),
        Pin(27, "P4.15", "tube_RnW"),
        Pin(28, "P4.17", "tube_A2"),
        Pin(29, "P2.2", "tube_A1"),
        Pin(30, "P2.5", "cpu_RnW"),
        Pin(31, "P2.6", "cpu_CLK"),
        Pin(32, "P2.8", "bbc_nTUBE"),
        Pin(33, "P2.9-GSR", "cpu_D0"),
        Pin(34, "P2.11-GTS2", "cpu_D1"),
        Pin(35, "VCCINT_3V3", "3V3"),
        Pin(36, "P2.14-GTS1", "cpu_A7"),
        Pin(37, "P2.15", "cpu_D2"),
        Pin(38, "P2.17", "cpu_D3"),
    ],
)
cpld_cap1 = myelin_kicad_pcb.C0805("100n", "3V3", "GND", ref="C1", handsoldering=False)
cpld_cap2 = myelin_kicad_pcb.C0805("100n", "3V3", "GND", ref="C2", handsoldering=False)
cpld_cap3 = myelin_kicad_pcb.C0805("1u", "3V3", "GND", ref="C3", handsoldering=False)
myelin_kicad_pcb.update_xilinx_constraints(cpld, os.path.join(here, "../cpld/constraints.ucf"))

regulator = myelin_kicad_pcb.Component(
    footprint="TO_SOT_Packages_SMD:SOT-89-3",
    identifier="U1",
    value="MCP1700T-3302E/MB",
    pins=[
        Pin(2, "VIN", ["5V"]),
        Pin(3, "VOUT", ["3V3"]),
        Pin(1, "GND", ["GND"]),
    ],
)
reg_in_cap = myelin_kicad_pcb.C0805("1u", "GND", "5V", ref="C4")
reg_out_cap = myelin_kicad_pcb.C0805("1u", "3V3", "GND", ref="C5")

pi_power_jumper = myelin_kicad_pcb.Component(
	footprint="Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm",
	identifier="PIPWR",
	value="Power from Pi",
	pins=[
		Pin(1, "", "3V3_PI"),
		Pin(2, "", "3V3"),
	],
)

fx2_power_jumper = myelin_kicad_pcb.Component(
	footprint="Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm",
	identifier="FX2PWR",
	value="Power from FX2",
	pins=[
		Pin(1, "", "3V3_FX2"),
		Pin(2, "", "3V3"),
	],
)

pi_zero = myelin_kicad_pcb.Component(
	footprint="myelin-kicad:raspberry_pi_zero_flipped",
	identifier="PI1",
	value="Raspberry Pi Zero",
	pins=[
		Pin(1, "3V3", "3V3_PI"),  # for when we want the Pi to power the CPLD
		Pin(2, "5V"),
		Pin(3, "GPIO0-2", ["tube_A1"]),
		Pin(4, "5V"),
		Pin(5, "GPIO1-3", ["tube_A2"]),
		Pin(6, "ser_GND", ["pi_serial_GND"]),
		Pin(7, "GPIO4", ["tube_nRST"]),
		Pin(8, "ser_TX", ["pi_serial_TX"]),
		Pin(9, "GND", ["GND"]),
		Pin(10, "ser_RX", ["pi_serial_RX"]),
		Pin(11, "GPIO17", ["tube_nTUBE"]),
		Pin(12, "GPIO18", ["tube_RnW"]),
		Pin(13, "GPIO21-27", ["tube_A0"]),
		Pin(14, "GND", ["GND"]),
		Pin(15, "GPIO22", ["tube_D4"]),
		Pin(16, "GPIO23", ["tube_D5"]),
		Pin(17, "3V3"),
		Pin(18, "GPIO24", ["tube_D6"]),
		Pin(19, "GPIO10", ["tube_D2"]),
		Pin(20, "GND", ["GND"]),
		Pin(21, "GPIO9", ["tube_D1"]),
		Pin(22, "GPIO25", ["tube_D7"]),
		Pin(23, "GPIO11", ["tube_D3"]),
		Pin(24, "GPIO8", ["tube_D0"]),
		Pin(25, "GND", ["GND"]),
		Pin(26, "GPIO7", ["tube_CLK"]),
	],
)

serial_port = myelin_kicad_pcb.Component(
	footprint="Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm",
	identifier="SERIAL1",
	value="Pi Serial",
	pins=[
		Pin(1, "GND", ["pi_serial_GND"]),
		Pin(2, "TX", ["pi_serial_TX"]),
		Pin(3, "RX", ["pi_serial_RX"]),
	],
)

# altera jtag header, like in the lc-electronics xc9572xl board
# left column: tck tdo tms nc tdi
# right column: gnd vcc nc nc gnd
cpld_jtag = myelin_kicad_pcb.Component(
    footprint="Pin_Headers:Pin_Header_Straight_2x05_Pitch2.54mm",
    identifier="JTAG1",
    value="jtag",
    pins=[
        Pin(1, "TCK", ["cpld_TCK"]), # top left
        Pin(2, "GND", ["GND"]), # top right
        Pin(3, "TDO", ["cpld_TDO"]),
        Pin(4, "3V3", ["3V3"]),
        Pin(5, "TMS", ["cpld_TMS"]),
        Pin(6, "NC"),
        Pin(7, "NC"),
        Pin(8, "NC"),
        Pin(9, "TDI", ["cpld_TDI"]),
        Pin(10, "GND", ["GND"]),
    ],
)

# Reset level conversion using diode + pullup
reset_3v3_pullup = myelin_kicad_pcb.R0805("10k", "3V3_PI", "tube_nRST", ref="R5")
reset_3v3_diode = myelin_kicad_pcb.DSOD323("BAT54", "cpu_nRST", "tube_nRST", ref="D1")

# DONE lcsoft mini footprint.  need to flip it to look like this, so the lcsoft
# mini board can plug in to the top of the cartridge.

#   R2 R1       L2 L1
#   R4 R3       L4 L3
#    ...         ...
#  R20 R19     L20 L19

# DONE double check against real lcsoft PCB

analyzer = myelin_kicad_pcb.Component(
    footprint="myelin-kicad:lcsoft_mini_flipped",
    identifier="FX2",
    value="lcsoft mini",
    pins=[
        # left side, top to bottom, left to right, with board face up
        # and USB socket upward
        Pin( "L1", "PD5", "cpu_nNMI"),  # DONE add header for BBC test clip
        Pin( "L2", "PD6", "cpu_nRST"),
        Pin( "L3", "PD7", "tube_A0"),
        Pin( "L4", "GND", "GND"),
        Pin( "L5", "CLK"),
        Pin( "L6", "GND", "GND"),
        Pin( "L7", "RDY0", "analyzer_RDY0"),  # tie to 3V3 via 1k resistor
        Pin( "L8", "RDY1", "tube_CLK_jumper"),  # via jumper to tube_CLK
        Pin( "L9", "GND", "GND"),
        Pin("L10", "GND", "GND"),
        Pin("L11", "GND", "GND"),
        Pin("L12", "FCLK"),
        Pin("L13", "SCL"),
        Pin("L14", "SDA"),
        Pin("L15", "PB0", "tube_D0"),
        Pin("L16", "PB1", "tube_D1"),
        Pin("L17", "PB2", "tube_D2"),
        Pin("L18", "PB3", "tube_D3"),
        Pin("L19", "3V3", "3V3_FX2"),  # generated from USB
        Pin("L20", "3V3", "3V3_FX2"),  # generated from USB

        # right side, top to bottom, left to right
        Pin( "R1", "PD4", "cpu_nIRQ"),
        Pin( "R2", "PD3", "tube_CLK"),
        Pin( "R3", "PD2", "analyzer_PD2_READY"),  # DONE add header for BBC test clip
        Pin( "R4", "PD1", "cpu_SYNC"),  # DONE add header for test clip
        Pin( "R5", "PD0", "analyzer_PD0_RnW"),  # DONE add header to switch Elk pin A4/Master pin A11
        Pin( "R6", "PA7"),
        Pin( "R7", "PA6", "analyzer_PA6"),  # tie to 3V3 via 1k resistor
        Pin( "R8", "PA5", "analyzer_PA5"),  # tie to 3V3 via 1k resistor
        Pin( "R9", "PA4", "analyzer_PA4"),  # tie to GND via 1k resistor
        Pin("R10", "PA3"),
        Pin("R11", "PA2", "analyzer_PA2"),  # tie to 3V3 via 1k resistor
        Pin("R12", "PA1"),
        Pin("R13", "PA0"),
        Pin("R14", "CTL2"),
        Pin("R15", "CTL1"),
        Pin("R16", "CTL0"),
        Pin("R17", "PB7", "tube_D7"),
        Pin("R18", "PB6", "tube_D6"),
        Pin("R19", "PB5", "tube_D5"),
        Pin("R20", "PB4", "tube_D4"),
    ],
)
pull_resistors = [
    myelin_kicad_pcb.R0805("1k", "analyzer_PA6", "3V3_FX2", ref="R1"),
    myelin_kicad_pcb.R0805("1k", "analyzer_PA5", "3V3_FX2", ref="R2"),
    myelin_kicad_pcb.R0805("1k", "analyzer_PA4", "GND", ref="R3"),
    myelin_kicad_pcb.R0805("1k", "analyzer_PA2", "3V3_FX2", ref="R4"),
    myelin_kicad_pcb.R0805("1k", "analyzer_RDY0", "3V3_FX2", ref="R6"),
]

# DONE add headers and jumpers to select READY/RnW/nNMI/SYNC everywhere.

# Elk: elk_READY_master_RnW, tube_RnW, cpu_nNMI, test clip for SYNC
# Beeb: test clip for READY, tube_RnW, test clip for nNMI, test clip for SYNC
# Master: test clip for READY, elk_READY_master_RnW, cpu_nNMI, test clip for SYNC

# L8: capture clock
# L1/PD5/nNMI: 1-pin header (already connected for Elk/Master)
# R4/PD1/SYNC: 1-pin header
# R3/PD2/READY 2-pin header: bridge for Elk, add lead for everyone else
#   [PD2] [elk_READY_master_RnW]
# R5/PD0/RnW: 3-pin header: bridge left for Elk/Beeb, up for Master
#   [tube_RnW] [PD0]

sync_clk_jumper = myelin_kicad_pcb.Component(
	footprint="Pin_Headers:Pin_Header_Straight_2x04_Pitch2.54mm",
	identifier="LEADS",
	value="Options",
	pins=[
		Pin(1, "", "tube_CLK"),
		Pin(2, "", "tube_CLK_jumper"),
        Pin(3, "", "cpu_SYNC"),
		Pin(4, "", "cpu_nNMI"),
        Pin(5, "", "analyzer_PD2_READY"),
        Pin(6, "", "elk_READY_master_RnW"),
        Pin(7, "", "tube_RnW"),
        Pin(8, "", "analyzer_PD0_RnW"),
	],
)

# Just in case we want to connect up an ext PSU for CPLD programming
ext_power = myelin_kicad_pcb.Component(
    footprint="Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm",
    identifier="EXTPWR",
    value="ext pwr",
    pins=[
        Pin(1, "A", ["GND"]),
        Pin(2, "B", ["3V3"]),
        Pin(3, "C", ["5V"]),
    ],
)

for n in range(32):
    single_staple = myelin_kicad_pcb.Component(
        footprint="myelin-kicad:via_single",
        identifier="staple_single%d" % (n+1),
        value="",
        pins=[Pin(1, "GND", ["GND"])],
    )

myelin_kicad_pcb.dump_netlist("fx2_tube_cartridge_adapter.net")
