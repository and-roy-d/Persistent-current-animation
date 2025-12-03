# Superconducting Flux Tuning Visualization

A physics-accurate animation created with [Manim](https://www.manim.community/) illustrating the generation of persistent currents in superconducting quantum devices.

## Project Overview

This visualization demonstrates the "heat-switch" technique used to tune flux in superconducting loops. The animation sequence depicts:
1.  **Bias State:** External current flowing through the main bus.
2.  **Laser Heating:** A focused thermal spot drives a specific wire branch normal (resistive), diverting current.
3.  **Flux Trapping:** The wire cools (returns to superconducting state) while the bias is held, locking the flux quantum.
4.  **Persistent Current:** The external bias is removed, leaving a circulating persistent current loop and a "Tuned" state on the device readout.

## Installation

This project relies on the Manim Community library.

### 1. System Dependencies
Manim requires **FFmpeg** to render video and a LaTeX distribution (like MiKTeX or TeX Live) if you plan to render complex equations.

* **Windows:** [Install FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH.
* **MacOS:** `brew install ffmpeg`
* **Linux:** `sudo apt install ffmpeg`

### 2. Python Environment
It is recommended to use a virtual environment or Conda.

```bash
pip install manim
```

Running the Animation
Save the animation code as flux_tuning.py (or your preferred filename).

Open your Terminal or PowerShell and navigate to the directory.

Run the following command:
```
# -p plays the file immediately after rendering
# -ql renders in Low Quality (480p) for fast testing
# -qh renders in High Quality (1080p) for final export

manim -pql persistentcurrent_animation.py SuperconductingLoops
```
To render the final version in 4k at 60fps:
```
manim -pqk --fps 60 flux_tuning.py SuperconductingLoops
```
Output
The output video will be saved in the ```media/videos/persistentcurrent_animation/``` directory created automatically where you ran the script.
