#!/usr/bin/env python3
#
# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = [
#   "imp-read",
#   "gooey",
# ]
# ///

# DIA TMT QUANTIFICATION CHIMERYS
# 2025 (c) Micha Johannes Birklbauer
# https://github.com/michabirklbauer/
# micha.birklbauer@gmail.com

import warnings
import pandas as pd

from gooey import Gooey
from gooey import GooeyParser
from gooey import local_resource_path

from imp_read.tmt_chimerys import __version
from imp_read.tmt_chimerys import __convert
from imp_read.tmt_chimerys import __annotate_result_conditions
from imp_read.tmt_chimerys import __annotate_chimerys_protein_table
from imp_read.tmt_chimerys import __read_settings
from imp_read.tmt_chimerys import __get_consensusXML_df
from imp_read.tmt_chimerys import __get_consensusXML_map
from imp_read.tmt_chimerys import __get_resolution_gui_map
from imp_read.tmt_chimerys import __read_spectra_by_scannumber
from imp_read.tmt_chimerys import __annotate_chimerys_result


@Gooey(
    encoding="utf-8",
    program_name=f"READ for Chimerys DIA {__version}",
    default_size=(700, 800),
    image_dir=local_resource_path("img"),
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
        prog="tmt_chimerys.py",
        description="Calculates co-isolation purity for Chimerys DIA TMT PSMs and optionally quantifies them.",
        epilog="(c) Research Institute of Molecular Pathology, 2025",
    )
    req = parser.add_argument_group("Required", "Required Arguments.")
    req.add_argument(
        "-i",
        "--chimerys",
        dest="chimerys",
        required=True,
        help="Path/name of the Chimerys PSM result file in tab-separated .txt format.",
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
        "-p",
        "--proteins",
        dest="proteins",
        required=False,
        default=None,
        help="Path/name of the Chimerys protein result file in tab-separated .txt format.",
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
    args = parser.parse_args(argv)
    settings = __read_settings(args.config)
    print("Read settings:")
    print(settings)
    if args.window_file is not None:
        print(f"Using windows from given windows file: {args.window_file}")
    args_spectra = __convert(args.spectra)
    spectra = __read_spectra_by_scannumber(args_spectra)
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
        df = __annotate_chimerys_result(
            filename=args.chimerys,
            spectrum_filename=args_spectra,
            spectra=spectra,
            settings=settings,
            consensusXML_map=consensusXML_map,
            resolution_gui_map=resolution_gui_map,
            window_file=args.window_file,
        )
    df.to_csv(
        args.chimerys.split(".txt")[0] + "_purity_tmt_quant.txt",
        sep="\t",
        index=False,
    )
    df.to_parquet(
        args.chimerys.split(".txt")[0] + "_purity_tmt_quant.parquet",
        index=False,
    )
    df = __annotate_result_conditions(df, settings["conditions"])
    df.to_csv(
        args.chimerys.split(".txt")[0] + "_purity_tmt_quant_conditions.txt",
        sep="\t",
        index=False,
    )
    df.to_parquet(
        args.chimerys.split(".txt")[0] + "_purity_tmt_quant_conditions.parquet",
        index=False,
    )
    if args.proteins is not None:
        proteins_df = __annotate_chimerys_protein_table(args.proteins, df, settings)
        proteins_df.to_csv(
            args.proteins.split(".txt")[0] + "_purity_tmt_quant.txt",
            sep="\t",
            index=False,
        )
        proteins_df.to_parquet(
            args.proteins.split(".txt")[0] + "_purity_tmt_quant.parquet",
            index=False,
        )
    print("Script finished successfully!")
    return df


if __name__ == "__main__":
    _ = main()
