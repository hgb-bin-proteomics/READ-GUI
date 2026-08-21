# READ-GUI

Build scripts for the [Gooey](https://github.com/chriskiehl/Gooey)-based GUI version of
[READ](https://github.com/hgb-bin-proteomics/READ).

## Supported Operating Systems

The build scripts are only tested with Microsoft Windows 11.

## Usage

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run:
- READ Chimerys DDA:
  ```bash
  uv run pyinstaller tmt_chimerys_dda_gui.spec
  ```
- READ Chimerys DIA:
  ```bash
  uv run pyinstaller tmt_chimerys_gui.spec
  ```
- READ DIA-NN:
  ```bash
  uv run pyinstaller tmt_diann_gui.spec
  ```
- READ Spectronaut:
  ```bash
  uv run pyinstaller tmt_spectronaut_gui.spec
  ```

## Help

If you are experiencing issues or having any questions, please let us know in the
[READ repository](https://github.com/hgb-bin-proteomics/READ).

## Use of Generative-AI/LLMs

The READ logo was generated with [Lumo AI](https://proton.me/lumo). No Gen-AI/LLMs were used for anything else otherwise.

## Contact

In case of questions please contact:
- [micha.birklbauer@fh-hagenberg.at](mailto:micha.birklbauer@fh-hagenberg.at)
