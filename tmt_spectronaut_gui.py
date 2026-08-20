#!/usr/bin/env python3
#
# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#   "imp-read",
#   "gooey",
# ]
# ///

# DIA TMT QUANTIFICATION SPECTRONAUT
# 2025 (c) Micha Johannes Birklbauer
# https://github.com/michabirklbauer/
# micha.birklbauer@gmail.com

import warnings
import pandas as pd

from gooey import Gooey
from gooey import GooeyParser

from imp_read.tmt_chimerys import __get_bool_from_value
from imp_read.tmt_chimerys import __read_settings
from imp_read.tmt_chimerys import __get_consensusXML_df
from imp_read.tmt_chimerys import __get_consensusXML_map
from imp_read.tmt_chimerys import __get_resolution_gui_map
from imp_read.tmt_chimerys import __annotate_result_conditions
from imp_read.tmt_chimerys import __convert
from imp_read.tmt_spectronaut import __version
from imp_read.tmt_spectronaut import __remove_ambiguous_pg
from imp_read.tmt_spectronaut import __annotate_spectronaut_pgs
from imp_read.tmt_spectronaut import __read_spectra
from imp_read.tmt_spectronaut import __annotate_spectronaut_result


@Gooey(
    encoding="utf-8",
    program_name=f"READ for Spectronaut {__version}",
    default_size=(700, 800),
    menu=[
        {
            "name": "Help",
            "items": [
                {
                    "type": "Link",
                    "menuTitle": "Project Page",
                    "url": "https://github.com/hgb-bin-proteomics/READ/",
                }
            ],
        }
    ],
)
def main(argv=None) -> pd.DataFrame:
    parser = GooeyParser(  # pyright: ignore[reportOptionalCall]
        prog="tmt_spectronaut.py",
        description="Calculates co-isolation purity for Spectronaut DIA TMT peptide matches and quantifies them.",
        epilog="(c) Research Institute of Molecular Pathology, 2025",
    )
    req = parser.add_argument_group("Required", "Required Arguments.")
    req.add_argument(
        "-i",
        "--spectronaut",
        dest="spectronaut",
        required=True,
        help="Path/name of the Spectronaut result file.",
        type=str,
        widget="FileChooser",
    )
    req.add_argument(
        "-s",
        "--spectra",
        dest="spectra",
        required=True,
        help="Path/name of the mass spectra file in mzML format.",
        type=str,
        widget="FileChooser",
    )
    req.add_argument(
        "-c",
        "--config",
        dest="config",
        required=True,
        help="Path/name of the config file.",
        type=str,
        widget="FileChooser",
    )
    opt = parser.add_argument_group("Optional", "Optional Arguments.")
    opt.add_argument(
        "-t",
        "--ini",
        dest="ini_file",
        required=False,
        default=None,
        help="Path/name of the INI configuration file for the OpenMS IsobaricAnalyzer.",
        type=str,
        widget="FileChooser",
    )
    opt.add_argument(
        "-r",
        "--resolution",
        dest="resolution",
        required=False,
        default=None,
        help="Path/name of the resolution.csv file from the Resolution GUI file.",
        type=str,
        widget="FileChooser",
    )
    opt.add_argument(
        "-w",
        "--window",
        dest="window_file",
        default=None,
        help="Window file, overrides config file!",
        type=str,
        widget="FileChooser",
    )
    opt.add_argument(
        "-d",
        "--delimiter",
        dest="spectronaut_sep",
        default=";",
        help="Delimiter in the Spectronaut result file, by default ';' is used.",
        type=str,
    )
    opt.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        default=2,
        help="Verbose level where 0: ignore all warnings and errors, 1: raise warnings, and >= 2: raise errors!",
        type=int,
        widget="IntegerField",
        gooey_options={"initial_value": 1, "min": 0, "max": 2, "increment": 1},
    )
    args = parser.parse_args(argv)
    settings = __read_settings(args.config)
    print("Read settings:")
    print(settings)
    if args.window_file is not None:
        print(f"Using windows from given windows file: {args.window_file}")
    args_spectra = __convert(args.spectra)
    spectra = __read_spectra(args_spectra)
    quantification_method = int(settings["quantification_method"])
    consensusXML_map = None
    if quantification_method != 1 and quantification_method != 3:
        if args.ini_file is None:
            raise RuntimeError(
                "Quantification with OpenMS was selected but no OpenMS IsobaricAnalyzer "
                "configuration file was given! Please select one with -t or --ini, or "
                "select a different quantification approach!"
            )
        consensusXML_df = __get_consensusXML_df(args_spectra, args.ini_file)
        consensusXML_map = __get_consensusXML_map(consensusXML_df)
    resolution_gui_map = None
    if args.resolution is not None:
        resolution_gui_map = __get_resolution_gui_map(args.resolution)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=pd.errors.PerformanceWarning)
        df = __annotate_spectronaut_result(
            spectronaut_filename=args.spectronaut,
            spectrum_filename=args_spectra,
            spectra=spectra,
            settings=settings,
            consensusXML_map=consensusXML_map,
            resolution_gui_map=resolution_gui_map,
            window_file=args.window_file,
            verbose=int(args.verbose),
            spectronaut_sep=str(args.spectronaut_sep).strip(),
        )
        df = __annotate_result_conditions(df, settings["conditions"])
        df = __annotate_spectronaut_pgs(df, settings)
        if not __get_bool_from_value(settings["keep_pg"]):
            df = __remove_ambiguous_pg(df)
    df.to_csv(
        args.spectronaut.split(".csv")[0] + "_purity_tmt_quant.csv",
        sep=",",
        index=False,
    )
    df.to_parquet(
        args.spectronaut.split(".csv")[0] + "_purity_tmt_quant.parquet",
        index=False,
    )
    print("Script finished successfully!")
    return df


if __name__ == "__main__":
    _ = main()
