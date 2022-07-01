#!/usr/bin/env bash

git clone https://github.com/HPI-Information-Systems/TimeEval-algorithms.git
git clone https://github.com/HPI-Information-Systems/S2Gpp.git

baseImages=(
  python3-base
  r4-base
  python3-torch
)

algorithms=(
    mstamp
    dbstream
    kmeans
    lstm_ad
    normalizing_flows
    torsk
    damp
)

for base in "${baseImages[@]}"; do
  docker build -t registry.gitlab.hpi.de/akita/i/$base ./TimeEval-algorithms/0-base-images/$base
done

for algorithm in "${algorithms[@]}"; do
  docker build -t registry.gitlab.hpi.de/akita/i/$algorithm ./TimeEval-algorithms/$algorithm
done

docker build -t registry.gitlab.hpi.de/akita/i/s2gpp ./S2Gpp
