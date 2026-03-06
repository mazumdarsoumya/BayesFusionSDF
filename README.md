<div align="center">

# BayesFusionSDF
### Probabilistic Signed Distance Fusion with View Planning on CPU

<p>
  <a href="https://arxiv.org/abs/2602.19697">
    <img src="https://img.shields.io/badge/arXiv-2602.19697-b31b1b.svg" alt="arXiv">
  </a>
  <a href="https://soumyamazumdar.com">
    <img src="https://img.shields.io/badge/Website-Main-informational.svg" alt="Website">
  </a>
  <img src="https://img.shields.io/badge/Platform-CPU--first-success.svg" alt="CPU-first">
  <img src="https://img.shields.io/badge/Task-3D%20Reconstruction-purple.svg" alt="3D Reconstruction">
  <img src="https://img.shields.io/badge/Focus-Uncertainty%20Aware-blue.svg" alt="Uncertainty Aware">
</p>

**Official repository for BayesFusionSDF.**

This repository provides the **research code, configuration files, and reproducibility utilities** accompanying the paper:

**"BayesFusion–SDF: Probabilistic Signed Distance Fusion with View Planning on CPU"**

Maintainer: **Soumya Mazumdar**  
Main website: **https://soumyamazumdar.com**

</div>

---

> **Repository Policy**
>
> This repository does **not** redistribute third-party datasets (such as CO3D or other restricted / terms-governed datasets).
> Instead, it provides scripts and instructions to obtain datasets from their official sources and generate the required preprocessing outputs.
>
> In brief: the code is here, the mathematics is here, the documentation is here, but the datasets remain respectfully where their licenses intended them to remain.

## Contents

- [Overview](#overview)
- [Installation](#installation)
- [Data](#data)
- [Training](#training)
- [Evaluation](#evaluation)
- [Reproducibility](#reproducibility)
- [Directory Structure](#directory-structure)
- [Citation](#citation)
- [License](#license)
- [Contact](#contact)
- [Recommended Repository Checklist](#recommended-repository-checklist)
- [What Not to Include](#what-not-to-include)

## Overview

**BayesFusionSDF** is a CPU-first probabilistic 3D reconstruction framework for dense geometry fusion from depth observations.

The method combines:

- a **coarse TSDF bootstrap** for initialization,
- an **adaptive sparse voxel domain** near the surface,
- a **probabilistic signed distance formulation** based on a sparse Gaussian random field,
- **MAP inference** using sparse linear algebra and preconditioned conjugate gradients,
- **approximate posterior uncertainty estimation** via randomized diagonal probes, and
- **uncertainty-driven next-best-view planning** for active sensing.

This repository contains:

- the core implementation of the reconstruction pipeline,
- experiment and solver configuration files,
- scripts for preprocessing, training, and evaluation,
- utilities for reproducible experiments and reporting.

The practical objective is to retain the interpretability and deployment simplicity of classical volumetric fusion while adding principled uncertainty estimates that are directly useful for reconstruction and view planning.

## Installation

### Option A — Conda (recommended)

```bash
conda create -n bayesfusionsdf python=3.10 -y
conda activate bayesfusionsdf
pip install -r requirements.txt
```

### Option B — `venv` + pip

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Notes

* Keep package versions pinned where possible for reproducibility.
* If a future version of the code introduces optional acceleration backends, list them separately in environment-specific requirements files.
* For scientific software, dependency calmness is a virtue.

## Data

### Policy

This repository must **not** include:

* full copies of third-party datasets (for example, CO3D),
* dataset files that violate licensing or terms of use,
* personal, private, or sensitive data.

Instead, the repository should provide:

* dataset setup instructions,
* preprocessing scripts,
* path configuration files,
* optional tiny permissively licensed examples if appropriate.

### What should be provided in GitHub

Recommended artifacts:

* `scripts/download_<dataset>.sh` or `scripts/download_<dataset>.py`

  * downloads from the official source, or
  * prints official manual steps if the source requires an approval flow
* `scripts/preprocess_<dataset>.py`

  * converts raw data into the directory layout required by the code
* `configs/data/<dataset>.yaml`

  * expected paths, splits, and preprocessing options
* `DATASETS.md`

  * dataset setup guide, official source links, and terms reminder

### Example dataset layout

```text
data/
  <dataset_name>/
    raw/
    processed/
      train/
      val/
      test/
```

### Guidance for restricted datasets

For restricted datasets such as **CO3D**, provide:

* official source references,
* a local path checker,
* preprocessing instructions,
* no redistributed raw content.

### Large files

If you need to distribute non-dataset large files such as:

* small checkpoints,
* demo media,
* supplementary assets,

prefer:

* **GitHub Releases** for versioned artifacts, or
* **Git LFS** for limited large assets.

## Training

Below is a template training command for the package layout:

```bash
python -m bayesfusionsdf.train \
  --config configs/train.yaml \
  --data_root ./data/<dataset_name>/processed \
  --output_dir ./outputs/exp01
```

Recommended training outputs:

* checkpoints,
* logs,
* configuration snapshots,
* evaluation summaries,
* run metadata.

Suggested practice:

* save the exact command line used,
* store the resolved config,
* write outputs to versioned experiment folders.

## Evaluation

A typical evaluation command may follow this structure:

```bash
python -m bayesfusionsdf.eval \
  --config configs/eval.yaml \
  --checkpoint ./outputs/exp01/checkpoints/latest.pt \
  --data_root ./data/<dataset_name>/processed \
  --output_dir ./outputs/exp01_eval
```

Recommended evaluation reports include:

* Chamfer distance,
* accuracy,
* completeness,
* F-score at selected thresholds,
* optional uncertainty and NBV summaries.

## Reproducibility

Recommended practices:

* keep fixed random seeds in configs,
* log the exact command used for each run,
* record environment details:

  * Python version,
  * package versions,
  * operating system,
  * CPU information when relevant,
* keep preprocessing deterministic where possible,
* provide at least one minimal smoke test.

Optional but strongly recommended files:

```text
scripts/reproduce_main_results.sh
scripts/smoke_test.sh
```

The aim is not merely that the code runs once, but that it runs again with approximately the same scientific dignity.

## Directory Structure

Suggested repository structure:

```text
BayesFusionSDF/
  bayesfusionsdf/              # Python package / core code
    __init__.py
    ...

  configs/
    train.yaml
    eval.yaml
    data/

  scripts/
    download_*.sh
    download_*.py
    preprocess_*.py
    reproduce_*.sh
    smoke_test.sh

  assets/                      # Small, permissive media only
  tests/                       # Optional unit / integration tests

  docs/                        # Optional documentation / figures
  outputs/                     # Generated locally, usually gitignored
  requirements.txt
  README.md
  LICENSE
  .gitignore
  DATASETS.md
  CITATION.cff                # Optional but recommended
```

## Citation

If you use this repository in academic work, please cite:

```bibtex
@article{mazumdar2026bayesfusionsdf,
  title={BayesFusion--SDF: Probabilistic Signed Distance Fusion with View Planning on CPU},
  author={Mazumdar, Soumya and Rakesh, Vineet Kumar and Samanta, Tapas},
  journal={arXiv preprint arXiv:2602.19697},
  year={2026}
}
```

## License

Specify the license intended for the codebase, for example:

* MIT
* Apache-2.0
* BSD-3-Clause

If the repository depends on third-party software with additional license obligations, document them in:

* `NOTICE`, or
* this section of the README.

## Contact

**Maintainer:** Soumya Mazumdar  
**Website:** [https://soumyamazumdar.com](https://soumyamazumdar.com)

For repository-related communication, please use the issue tracker when appropriate so that questions, fixes, and clarifications remain visible to future travelers.

## Recommended Repository Checklist

### Must have

* `README.md`
* `LICENSE`
* `.gitignore`
* `requirements.txt` or `environment.yml`

### Strongly recommended

* `DATASETS.md`
* `configs/`
* `scripts/preprocess_*.py`
* `scripts/download_*.py` or `scripts/download_*.sh`
* `scripts/smoke_test.sh`

### Optional but useful

* `tests/`
* `CHANGELOG.md`
* `CITATION.cff`

## What Not to Include

Do **not** commit:

* third-party dataset contents,
* large raw archives such as `.zip`, `.tar`, `.mp4` dumps unless you explicitly own the rights and intend to distribute them,
* secrets such as API keys, tokens, credentials, private URLs, or personal environment files.

Use:

* `.gitignore`
* `.env.example`
* release artifacts
* external storage links where appropriate

to keep the repository clean, lawful, and pleasantly uneventful.
