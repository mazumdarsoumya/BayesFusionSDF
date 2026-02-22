# BayesFusionSDF

**BayesFusionSDF** provides research code, configuration, and reproducibility utilities for our paper.  
A lightweight project page is hosted at: **https://bayesfusionsdf.soumyamazumdar.com**  
Main website: **https://soumyamazumdar.com**

> **Repository policy (important):** This repository does **not** redistribute third-party datasets (e.g., CO3D or other restricted/terms-governed datasets). Instead, we provide scripts and clear instructions to obtain datasets from their official sources and to generate the required preprocessing outputs.

---

## Contents

- [Overview](#overview)
- [Project Page (GitHub Pages)](#project-page-github-pages)
- [Installation](#installation)
- [Data](#data)
- [Training](#training)
- [Evaluation](#evaluation)
- [Reproducibility](#reproducibility)
- [Directory Structure](#directory-structure)
- [Citation](#citation)
- [License](#license)
- [Contact](#contact)

---

## Overview

This repository contains:
- core implementation (models / pipeline / utilities),
- configuration files for experiments,
- scripts for dataset preparation, training, and evaluation,
- documentation and a GitHub Pages project page.

**Replace this section with a short formal abstract of your method and the primary contributions.**

---

## Project Page (GitHub Pages)

The project page is served from the **`/docs`** directory via GitHub Pages and is configured for the custom domain:

- `bayesfusionsdf.soumyamazumdar.com`

Recommended contents:
- `docs/index.html` (single-file page)
- `docs/CNAME` (contains the domain)
- `docs/paper.pdf` (optional, if you want the paper hosted on the same subdomain)

---

## Installation

### Option A — Conda (recommended)

```bash
conda create -n bayesfusionsdf python=3.10 -y
conda activate bayesfusionsdf
pip install -r requirements.txt
```

### Option B — pip + venv

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

> If your code requires CUDA / PyTorch versions, specify them explicitly in `requirements.txt` or provide a separate `requirements-cuda.txt`.

---

## Data

### Policy

This repository **must not** include:

* full copies of third-party datasets (e.g., **CO3D**),
* any dataset files that violate licensing / terms,
* any personal or sensitive data.

Instead, include:

* a **download guide** (links to official dataset instructions),
* a **preprocessing script** that produces the exact directory layout expected by the training code,
* a small **toy/example sample** that you created or that is permissively licensed (optional).

### What you SHOULD provide in GitHub

**Provide instructions + scripts, not the dataset.**

Recommended:

1. `scripts/download_<dataset>.sh` or `scripts/download_<dataset>.py`

   * downloads from the official source (or prints the official steps if manual acceptance is required)
2. `scripts/preprocess_<dataset>.py`

   * converts raw dataset to your required format
3. `configs/data/<dataset>.yaml`

   * describes expected paths, splits, and preprocessing options
4. `DATASETS.md` (recommended)

   * a single page listing supported datasets, licenses/terms pointers, and step-by-step setup

### Example dataset layout (you define yours)

```text
data/
  <dataset_name>/
    raw/
    processed/
      train/
      val/
      test/
```

### Dataset examples you can reference without redistributing

* For restricted datasets like CO3D: include only **official links** and a script that checks for user-provided paths.
* For open datasets: still prefer scripts + instructions, and avoid committing large archives.

### Large files

If you must ship large *non-dataset* artifacts (e.g., small checkpoints, demo media):

* use **GitHub Releases** for versioned artifacts, or
* use **Git LFS** for limited large assets.

---

## Training

```bash
python -m bayesfusionsdf.train   --config configs/train.yaml   --data_root ./data/<dataset_name>/processed   --output_dir ./outputs/exp01
```

---

## Evaluation

```bash
python -m bayesfusionsdf.eval   --config configs/eval.yaml   --checkpoint ./outputs/exp01/checkpoints/latest.pt   --data_root ./data/<dataset_name>/processed   --output_dir ./outputs/exp01_eval
```

---

## Reproducibility

Recommended practices:

* keep fixed random seeds in configs,
* log the exact command used for each run,
* store environment details (Python version, package versions),
* provide at least one minimal “smoke test” experiment that runs quickly.

Optional but recommended:

* `scripts/reproduce_main_results.sh`
* `scripts/smoke_test.sh`

---

## Directory Structure

Suggested repository structure:

```text
BayesFusionSDF/
  docs/                       # GitHub Pages site (custom domain)
    index.html
    CNAME
    paper.pdf                 # optional

  src/ or bayesfusionsdf/     # python package / core code
    __init__.py
    ...

  configs/
    train.yaml
    eval.yaml
    data/

  scripts/
    preprocess_*.py
    reproduce_*.sh
    smoke_test.sh

  assets/                     # small, permissive media only (figures, icons)
  tests/                      # optional unit/integration tests

  requirements.txt
  README.md
  LICENSE
  .gitignore
  DATASETS.md                 # recommended
```

---

## Citation

If you use this repository in academic work, please cite:

```bibtex
@inproceedings{bayesfusionsdf2026,
  title     = {BayesFusionSDF},
  author    = {Mazumdar, Soumya and ...},
  booktitle = {Your Conference Name},
  year      = {2026}
}
```

---

## License

Specify the license you intend to use (e.g., MIT, Apache-2.0).
If your code depends on third-party libraries with additional requirements, list them in `NOTICE` or in this section.

---

## Contact

Maintainer: **Soumya Mazumdar**  
Website: https://soumyamazumdar.com

---

## What files you should include (recommended checklist)

**Must have**
- `README.md` (this file)
- `LICENSE`
- `.gitignore`
- `requirements.txt` (or `environment.yml`)
- `docs/index.html` and `docs/CNAME` (for the subdomain project page)

**Strongly recommended**
- `DATASETS.md` (dataset setup + links + terms reminder)
- `scripts/preprocess_*.py` (and optionally `scripts/download_*.py`)
- `configs/` for reproducible runs
- `scripts/smoke_test.sh` (quick sanity run)

**Optional**
- `tests/`
- `CHANGELOG.md`
- `CITATION.cff` (nice for GitHub “Cite this repository” button)

---

## What you should NOT include
- Any third-party dataset content (CO3D etc.)
- Large raw data archives (`.zip`, `.tar`, `.mp4` dumps) unless you own the rights and it’s intended
- Secrets: API keys, tokens, private URLs (use `.env.example` instead)
