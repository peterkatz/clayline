#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
output_dir=${1:-"$script_dir/../../demo-out/weave-pete-job"}
mkdir -p "$output_dir"

clayline weave "$script_dir/pete-job.obj" \
  --profile potterbot-xl \
  --layer-height 2 \
  --sample-spacing 1 \
  --bead-width 5 \
  --wave "$script_dir/pete-job.pattern.json" \
  --extrusion pattern \
  --amplitude 3 \
  --wavelength 18 \
  --twist 0.5 \
  --z-blend \
  --level-rim \
  --bottom 3 \
  --seam chained \
  --overlap 0.2 \
  --prime-mm 0 \
  --end-early-mm 0 \
  --reproducible \
  -o "$output_dir/pete-job.gcode" \
  --preview "$output_dir/pete-job.html" \
  --report "$output_dir/pete-job-report.json"

clayline lint "$output_dir/pete-job.gcode"
