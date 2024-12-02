"""
ENUM_DICT contains all the builtin enumerated fields for SampleSetLines, and their
allowed values.

SYNONYMS contains the hard-coded synonyms for sampleset line fields.

RUN_MODES contains the allowed values for the RunMode when starting a run in Empower.
"""

from types import MappingProxyType  # Pythons name for a frozen dict
from typing import Mapping

# The allowed values for builtin SampleSetLine fields
BUILTIN_ALLOWED_VALUES: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "Blank": ("Yes", "No"),
        "ColumnPosition": (
            "No Change",
            "Position 1",
            "Position 2",
            "Position 3",
            "Position 4",
            "Position 5",
            "Position 6",
            "Position 7",
            "Position 8",
            "Position 9",
            "Position 10",
            "Position 11",
            "Position 12",
            "Position 13",
            "Position 14",
            "Position 15",
            "Position 16",
            "Position 17",
            "Position 18",
            "Position 19",
            "Position 20",
            "Position 21",
            "Position 22",
            "Position 23",
            "Position 24",
        ),
        "Function": (
            "Inject Standards",
            "Inject Narrow Standards",
            "Inject Broad Standards",
            "Inject Samples",
            "Inject Narrow Samples",
            "Inject Broad Samples",
            "Inject Controls",
            "Inject RF Internal Standards",
            "Inject Immediate Standards",
            "Inject Immediate Samples",
            "Clear Calibration",
            "Equilibrate",
            "Report",
            "Quantitate",
            "Calibrate",
            "Condition Column",
            "Purge Inj",
            "Purge Det",
            "EasyTune",
            "Compute Dissolution",
            "Dissolution Wait",
            "Refresh Syringe",
            "Wash Needle",
            "Wet Prime",
            "Sys Prep",
            "Summarize Custom Fields",
            "Pause",
            "Summarize Custom Fields (Exclude Faulted)",
            "Summarize Custom Fields Incrementally",
            "Summarize Custom Fields Incrementally (Exclude Faulted)",
            "Export",
        ),
        "PeakRatioReference": ("Yes", "No"),
        "Processing": (
            "No Set",
            "Don't Process or Report",
            "Don't Report",
            "Normal",
            "Ignore Faults",
            "No Sys Suit",
        ),
        "SampleMatrix": (
            "",
            "Sample",
            "Diluent Blank",
            "Mobile Phase Blank",
            "Plasma Blank",
            "Bile Blank",
            "Urine Blank",
            "Formulation Blank",
            "Extraction Blank",
            "Filtrate",
            "Excipient",
            "Working Standard",
            "Stock Standard",
            "Placebo",
        ),
        "ColumnName": tuple(),
        # ColumnName is a string field masquerading as an enum, so we don't want
        # validation.
        "ColumnSerialNumber": tuple(),
        # ColumnSerialNumber is also a string field masquerading as an enum
    }
)

SYNONYMS: Mapping[str, str] = MappingProxyType(
    {
        "Method": "MethodSetOrReportMethod",
        "SamplePos": "Vial",
        "InjectionVolume": "InjVol",
    }  # Key are "human readable" names, values are the names used in Empower.
)

RUN_MODES: tuple[str, ...] = ("RunOnly", "RunAndProcess", "RunAndReport")
