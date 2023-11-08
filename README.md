# S2G++ Experiments

This repository holds the experiment definitions for the _Series2Graph++_ paper. 
The code for the algorithm can be found [here](https://github.com/HPI-Information-Systems/S2Gpp).

The following experiments can be reproduced:

- [S2G++ Experiments](#s2g-experiments)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Build Docker Images](#build-docker-images)
  - [Generate Datasets](#generate-datasets)
  - [Download Exathlon Dataset](#download-exathlon-dataset)
- [Quality Experiment](#quality-experiment)
- [Correlation Anomaly Detection Experiment](#correlation-anomaly-detection-experiment)
- [Self-Correction Experiment](#self-correction-experiment)
- [Scalability Experiment](#scalability-experiment)
- [Explainability Experiment](#explainability-experiment)
- [Hyper-Parameter Optimization](#hyper-parameter-optimization)
- [Results](#results)
  - [Quality Haystack (AUROC)](#quality-haystack-auroc)
  - [Quality Exathlon (AUROC)](#quality-exathlon-auroc)
  - [Quality CoMuT (AUROC)](#quality-comut-auroc)
  - [Scalability Length (Seconds)](#scalability-length-seconds)
  - [Scalability Width (Seconds)](#scalability-width-seconds)
- [References](#references)

The results with the distributed version of S2G++ cannot be reproduced with this repository alone. 
Therefore, please [generate](#generate-datasets) the _scalability_ datasets and start S2G++ from multiple machines 
as described in [its repository](https://github.com/HPI-Information-Systems/S2Gpp).

## Requirements

- Python 3
- GutenTAG (will be installed with this repository)
- TimeEval (will be installed with this repository)
- Docker

## Installation

```shell
python setup.py install
```


## Build Docker Images

Uses images from [TimeEval-Algorithms repository](https://github.com/HPI-Information-Systems/TimeEval-algorithms).

```shell
./build-images.sh
```


## Generate Datasets

This repository contains the configurations for generating the following datasets:

- [haystack](dataset_configs/haystack.yaml) for [Quality Experiment](#quality-experiment) and [Self-Correction Experiment](#self-correction-experiment)
- [comut](dataset_configs/comut.yaml) (seed: 42) for [Correlation Anomaly Detection Experiment](#correlation-anomaly-detection-experiment)
- [scalability](dataset_configs/scalability.yaml) (seed: 42) for [Scalability Experiment](#scalability-experiment)
- [scalability_xl](dataset_configs/scalability_xl.yaml) (seed: 42) for [Scalability Experiment](#scalability-experiment)
- [haystack-explain](dataset_configs/haystack-explain.yaml) (seed: 421) for [Explainability Experiment](#explainability-experiment)

To generate the listed datasets, execute the command below with the corresponding variable values.

```shell
python -m gutenTAG --config-yaml <dataset-name>.yaml [--seed <dataset-seed>] --output-dir data/<dataset-name> --addons gutenTAG.addons.timeeval.TimeEvalAddOn
```

## Download Exathlon Dataset

The integrated [Exathlon](https://github.com/exathlonbenchmark/exathlon) [1] datasets can be downloaded [⬇ here](https://owncloud.hpi.de/s/o3U8VrNmC5EV2Sp/download).
Also download the [⬇ index file](https://owncloud.hpi.de/s/3Cp8Q5H9gn7EVK0/download) that holds the metadata for the datasets and rename it to `datasets.csv`.

Place the files in the data folder as follows:

```yaml
data:
  exathlon:
    multivariate: ...  # this will be extracted from the Exathlon.zip
    datasets.csv
```

# Quality Experiment

For this experiment, we use the [TimeEval](https://github.com/HPI-Information-Systems/TimeEval) evaluation 
tool with the script in [haystack-experiment.py](experiment_scripts/haystack-experiment.py). 
If you want to repeat this experiment on your machines, be aware to change the remote machines to your addresses in [this part of the script](experiment_scripts/haystack-experiment.py#L238) 

```shell
python experiment_scripts/haystack-experiment.py
python experiment_scripts/exathlon-experiment.py
```

# Correlation Anomaly Detection Experiment

For this experiment, we use the [TimeEval](https://github.com/HPI-Information-Systems/TimeEval) evaluation 
tool with the script in [comut-experiment.py](experiment_scripts/comut-experiment.py). 
If you want to repeat this experiment on your machines, be aware to change the remote machines to your addresses in [this part of the script](experiment_scripts/comut-experiment.py#L237) 

```shell
python experiment_scripts/comut-experiment.py
```

# Self-Correction Experiment

For this experiment, we use the [TimeEval](https://github.com/HPI-Information-Systems/TimeEval) evaluation 
tool with the script in [self-correction-experiment.py](experiment_scripts/self-correction-experiment.py). 
If you want to repeat this experiment on your machines, be aware to change the remote machines to your addresses in [this part of the script](experiment_scripts/self-correction-experiment.py#L241) 

```shell
python experiment_scripts/self-correction-experiment.py
```

# Scalability Experiment

For this experiment, we use the [TimeEval](https://github.com/HPI-Information-Systems/TimeEval) evaluation 
tool with the scripts in [scalability-experiment.py](experiment_scripts/scalability-experiment.py) and [scalability-xl-experiment.py](experiment_scripts/scalability-xl-experiment.py). 
If you want to repeat this experiment on your machines, be aware to change the remote machines to your addresses in [this part of the script](experiment_scripts/scalability-experiment.py#L264) and [this part of the other script](experiment_scripts/scalability-xl-experiment.py#L259).

```shell
python experiment_scripts/scalability-experiment.py
python experiment_scripts/scalability-xl-experiment.py
```

# Explainability Experiment

For this experiment, we do not use TimeEval. The script in [explainability-experiment.py](experiment_scripts/explainability-experiment.py) performs the experiment.
If you want to repeat this experiment on your machines, be aware to adapt the local docker image name [here](experiment_scripts/explainability-experiment.py#L25) and group [here](experiment_scripts/explainability-experiment.py#L119) that you have built before.

```shell
python experiment_scripts/explainability-experiment.py --datasets data/haystack-explain
```

# Hyper-Parameter Optimization

For this experiment, we do not use TimeEval. The scripts in [experiments/hyperopt](experiments/hyperopt) perform the optimization.
If you want to repeat this experiment on your machines, be aware to adapt the local docker image name [here](experiments/algorithms/s2gpp.py).

```shell
python -m hyperopt --algorithms <image-name> --hyperopt-calls 30 --training-type unsupervised --output-file results.json --dataset-dir data/hyperopt --mode whole_collection
```

# Results

## Quality Haystack (AUROC)

| **dataset_name**              | **DAMP**           | **DBStream**       | **LSTM-AD**        | **Normalizing Flows** | **S2G++20p-KDE**   | **Torsk**          | **k-Means**        | **mSTAMP**         |
| ----------------------------- | ------------------ | ------------------ | ------------------ | --------------------- | ------------------ | ------------------ | ------------------ | ------------------ |
| **haystack-ecg-10-pattern**   | 0.0151515151515151 | 0.9972070707070706 | 0.9999888888888888 |                       | 0.9999989898989898 | 155                | 0.999960606060606  | 0.9999939393939394 |
| **haystack-ecg-10-platform**  | 1.0                | 0.8624398989898989 | 0.2233696969696969 |                       | 0.8433080808080807 | 0.9436666666666668 | 0.5196828282828283 | 0.9998272727272728 |
| **haystack-ecg-20-pattern**   | 0.98929898989899   | 1.0                |                    |                       | 0.9998717171717172 | 0.9942292929292929 | 0.7543272727272727 | 1.0                |
| **haystack-ecg-20-platform**  | 0.9946262626262624 | 0.8395853535353536 |                    |                       | 0.8782464646464647 | 0.9963040404040404 | 0.8833626262626263 | 0.9998131313131312 |
| **haystack-ecg-3-pattern**    | 0.0151515151515151 | 0.5060181818181818 | 0.9993909090909092 | 0.9999161616161616    | 0.9996909090909092 | 0.2388383838383838 | 0.99999898989899   | 0.999940404040404  |
| **haystack-ecg-3-platform**   | 0.7982858585858585 | 0.7292272727272726 | 0.9997373737373736 | 0.9982080808080808    | 0.999618181818182  | 0.9745777777777778 | 0.999840404040404  | 0.9998272727272728 |
| **haystack-ecg-4-pattern**    | 0.9999838383838384 | 0.9674454545454544 | 0.9994565656565656 | 0.9998989898989898    | 0.99989898989899   | 0.913160606060606  | 1.0                | 0.99999898989899   |
| **haystack-ecg-4-platform**   | 0.9965535353535352 | 0.8991828282828283 | 0.9999848484848484 | 0.999880808080808     | 0.999539393939394  | 0.5734444444444444 | 0.9998545454545454 | 0.9998080808080808 |
| **haystack-ecg-5-pattern**    | 0.0151515151515151 | 0.9830858585858586 | 0.9993939393939394 |                       | 0.9975757575757576 | 0.1451010101010101 | 0.996989898989899  | 0.9982676767676768 |
| **haystack-ecg-5-platform**   | 0.9999969696969696 | 0.7311474747474748 | 0.9998838383838384 |                       | 0.8775575757575758 | 0.9668646464646466 | 0.8868979797979797 | 0.9998272727272728 |
| **haystack-ecg-8-pattern**    | 0.9915323232323232 | 0.4993474747474747 | 0.9995424242424242 |                       | 0.9986373737373736 | 0.1951515151515151 | 0.9456080808080808 | 0.99999898989899   |
| **haystack-ecg-8-platform**   | 0.9999282828282828 | 0.8235186868686868 | 0.2768828282828283 |                       | 0.9840535353535352 | 0.9335656565656568 | 0.443770707070707  | 0.9998080808080808 |
| **haystack-sine-10-pattern**  | 0.999990909090909  | 0.8429060606060607 |                    |                       | 0.9976242424242424 | 0.9595555555555556 | 0.9998919191919192 | 0.9999888888888888 |
| **haystack-sine-10-platform** | 0.99999898989899   | 0.99999898989899   |                    |                       | 0.99999898989899   | 0.9969111111111112 | 0.9999545454545454 | 1.0                |
| **haystack-sine-20-pattern**  | 0.8494010101010101 | 0.9998939393939394 |                    |                       | 0.9999969696969696 | 0.1115151515151515 | 0.9995252525252524 | 0.9999828282828284 |
| **haystack-sine-20-platform** | 0.9999939393939394 | 0.9999969696969696 |                    |                       | 0.9999565656565657 | 0.9958646464646465 | 0.9998929292929292 | 0.99999898989899   |
| **haystack-sine-3-pattern**   | 0.9999636363636364 | 0.4893323232323232 | 0.9965616161616162 | 0.3352161616161616    | 0.999960606060606  | 0.999650505050505  | 0.9999939393939394 | 0.9999929292929292 |
| **haystack-sine-3-platform**  | 0.997540404040404  | 0.99999898989899   | 0.9997161616161616 | 0.9999151515151516    | 0.9999333333333332 | 0.9968919191919192 | 1.0                | 1.0                |
| **haystack-sine-4-pattern**   | 0.9999939393939394 | 0.7308232323232322 | 0.991710101010101  |                       | 1.0                | 0.999441414141414  | 0.999980808080808  | 0.9999969696969696 |
| **haystack-sine-4-platform**  | 0.99999898989899   | 0.9999969696969696 | 0.9969363636363636 |                       | 0.99999898989899   | 0.996259595959596  | 1.0                | 1.0                |
| **haystack-sine-5-pattern**   | 0.999978787878788  | 0.999989898989899  | 0.9937858585858586 |                       | 0.9999939393939394 | 0.999540404040404  | 0.9999929292929292 | 0.99999898989899   |
| **haystack-sine-5-platform**  | 0.99999898989899   | 0.9999969696969696 | 0.997130303030303  |                       | 0.9999343434343436 | 0.9952929292929292 | 0.99999898989899   | 0.99999898989899   |
| **haystack-sine-8-pattern**   | 0.99980101010101   | 1.0                |                    |                       | 1.0                | 0.9940171717171716 | 0.9999262626262628 | 0.999978787878788  |
| **haystack-sine-8-platform**  | 0.99999898989899   | 0.9999989898989898 |                    |                       | 0.999849494949495  | 0.9949848484848484 | 1.0                | 1.0                |

## Quality Exathlon (AUROC)

| **dataset_name**      | **Normalizing Flows** | **k-Means**        | **S2G++**          | **S2G++SC**        | **LSTM-AD**        | **DBStream**       | **Torsk**          | **mSTAMP**         | **DAMP**           |
| --------------------- | --------------------- | ------------------ | ------------------ | ------------------ | ------------------ | ------------------ | ------------------ | ------------------ | ------------------ |
| **10_2_1000000_67**   |                       |                    |                    |                    |                    | 0.5247958573989245 | 0.4807613721356725 | 0.982134015905429  | 0.5                |
| **10_3_1000000_75**   |                       | 0.9874543212483856 | 0.9029944044501352 | 0.9028985960834262 |                    |                    | 0.3505108595863955 | 0.0080461903999536 | 0.8015511272318788 |
| **10_4_1000000_79**   |                       | 0.7615877866688937 | 0.7977926755922179 | 0.7977926755922179 |                    |                    | 0.6300916057068899 | 0.1995649791532564 | 0.4599119755715554 |
| **1_2_100000_68-15**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **1_2_100000_68-16**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **1_4_1000000_80-14** |                       |                    |                    |                    | 0.6787272058097961 |                    |                    |                    |                    |
| **2_1_100000_60-20**  |                       |                    |                    |                    | 0.0224730045974397 |                    |                    |                    |                    |
| **2_1_100000_60-22**  |                       |                    |                    |                    | 0.0225032960482284 |                    |                    |                    |                    |
| **2_2_200000_69**     |                       | 0.9847091997541976 |                    |                    |                    | 0.0023683271552322 | 0.7921739647550895 | 0.4864223838880409 | 0.5                |
| **3_2_1000000_71**    |                       | 0.9987722730316227 | 0.0                | 0.0                |                    | 0.006086205220461  | 0.5889577755859283 | 0.0                | 1.0                |
| **3_2_500000_70**     |                       | 0.8653065603499591 | 0.0                | 0.0                |                    | 0.0029763140772734 | 0.4276001218212274 | 0.0                | 0.5                |
| **4_1_100000_61-27**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **4_1_100000_61-28**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **4_1_100000_61-29**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **4_1_100000_61-30**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **4_1_100000_61-32**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_63-33**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_63-34**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_63-35**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_63-36**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_63-37**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_63-40**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_63-64**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_64-33**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_64-34**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_64-35**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_64-36**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_64-37**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_64-40**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_100000_64-63**  |                       |                    |                    |                    |                    |                    |                    |                    |                    |
| **5_1_500000_62**     |                       |                    | 0.9091261598211032 | 0.9091261598211032 |                    | 0.545655043189805  | 0.8549108629832907 | 0.0355722168535184 | 0.4127790046364749 |
| **5_2_1000000_72**    |                       | 0.0                |                    | 0.8769170332045589 |                    | 0.0023666568313285 | 0.4182707416988602 | 0.0                | 0.5                |
| **6_1_500000_65**     |                       |                    | 0.9369949587972825 | 0.93698642946875   |                    | 0.5795468140597708 | 0.5554898823538037 | 0.0449571988340905 | 0.5601654104360192 |
| **6_3_200000_76**     |                       | 0.4266442348694404 | 0.7026352076120903 | 0.7026352076120903 |                    |                    | 0.3962715506874961 | 0.0007092595837116 | 0.5215515535485845 |
| **8_3_200000_73**     |                       | 0.9227907936753496 | 0.962280275022022  | 0.9630030340180312 |                    |                    | 0.3056725277367201 | 0.0333016142990544 | 0.7071225623163423 |
| **8_4_1000000_77**    |                       | 0.8222085364815085 | 0.5832605430802428 | 0.7514107373863842 |                    |                    | 0.5439106577965742 | 0.412400892892084  | 0.5173432755878202 |
| **9_2_1000000_66**    |                       |                    |                    |                    |                    | 0.0005808887598024 | 0.5162493488737621 | 0.1796308579962905 | 0.5                |
| **9_3_500000_74**     |                       | 0.9924940346753098 | 0.9726515423395048 | 0.9856100908843608 |                    |                    | 0.2919681920995121 | 0.0001116512094114 | 0.7192167364730152 |
| **9_4_1000000_78**    |                       | 0.8943949675029209 | 0.729222723707749  | 0.7305068813583334 |                    |                    | 0.7253936833690697 | 0.1364997309795128 | 0.434416502183812  |

## Quality CoMuT (AUROC)

| **dataset_name**                                 | **DAMP**           | **DBStream**       | **LSTM-AD**        | **Normalizing Flows** | **S2G++20p-KDE**   | **S2G++20p-MeanShift** | **Torsk**          | **k-Means**        | **mSTAMP**         |
| ------------------------------------------------ | ------------------ | ------------------ | ------------------ | --------------------- | ------------------ | ---------------------- | ------------------ | ------------------ | ------------------ |
| **rmj-2-short-anomalies-on-2-different-channel** | 0.4830745967741936 | 0.4236391129032257 | 0.7055052923387097 | 0.9998941532258064    | 0.8806791834677419 | 0.6777457157258064     | 0.6269430443548387 | 0.975249495967742  | 0.5681955645161291 |
| **rmj-2-short-anomalies-on-2-same-channel**      | 0.5441885080645161 | 0.5094254032258064 | 0.9586076108870968 | 0.9999558971774192    | 0.7440877016129034 | 0.778210685483871      | 0.7420646421370969 | 0.9599357358870968 | 0.5855090725806451 |
| **rmj-3-short-anomalies-on-3-different-channel** | 0.5410509446693657 | 0.558502024291498  | 0.6400033738191633 | 0.8531604251012147    | 0.9451737516869096 | 0.9478213562753036     | 0.7709665991902833 | 0.9652732793522268 | 0.5916329284750338 |
| **rmj-3-short-anomalies-on-3-same-channel**      | 0.3049907219973009 | 0.5193657219973009 | 0.6989304993252361 | 0.9996339406207828    | 0.7962710863697706 | 0.8065435222672065     | 0.7560517881241564 | 0.9445428475033736 | 0.5477159244264508 |
| **rmj-large-mode-correlation-on-2**              | 0.024390243902439  | 0.9835365853658536 | 0.9995274390243902 | 0.9999993648373984    | 0.9379427083333334 | 0.9638401930894308     | 0.326930894308943  | 0.9269829776422764 | 0.9242644817073172 |
| **rmj-large-mode-correlation-on-3**              | 0.024390243902439  | 0.955081300813008  | 0.9606415142276424 | 0.9999771341463414    | 0.9887258638211384 | 0.9997345020325203     | 0.3340447154471544 | 0.7721176321138211 | 0.8943749999999999 |
| **rmj-large-mode-correlation-on-4**              | 0.9526829268292684 | 0.8819105691056911 | 0.9157590193089432 |                       | 0.993725863821138  | 0.99721481199187       | 0.6027686737804878 | 0.858009400406504  | 0.8800120680894309 |
| **rmj-medium-mode-correlation-on-2**             | 0.1904019657258064 | 0.93125            | 0.990616179435484  | 0.9999432963709678    | 0.6741456653225807 |                        | 0.3536290322580645 | 0.8032459677419355 | 0.7744833669354838 |
| **rmj-medium-mode-correlation-on-3**             | 0.2704133064516129 | 0.7215725806451613 | 0.9876247479838708 | 0.0                   | 0.9974722782258064 | 0.998773941532258      | 0.9487941028225808 | 0.7932850302419355 | 0.7959488407258064 |
| **rmj-medium-mode-correlation-on-4**             | 0.3802532762096774 | 0.6973790322580645 | 0.5820501512096774 |                       | 0.9991973286290322 | 0.999562752016129      | 0.9790221774193548 | 0.7643573588709678 | 0.7387323588709677 |
| **rmj-short-mode-correlation-on-2**              | 0.8868147590361446 | 0.6831325301204819 | 0.7083157630522088 | 0.999992469879518     | 0.9969176706827308 | 0.9993624497991968     | 0.94714859437751   | 0.9921812248995984 | 0.5696134538152611 |
| **rmj-short-mode-correlation-on-3**              | 0.0060240963855421 | 0.9877510040160644 | 0.3636295180722891 | 0.999984939759036     | 0.6640185742971888 | 0.4299623493975903     | 0.3183734939759036 | 0.977753514056225  | 0.629683734939759  |
| **rmj-short-mode-correlation-on-4**              | 0.1182856425702811 | 0.8753012048192771 | 0.9739984939759035 |                       | 0.517781124497992  | 0.5528815261044177     | 0.9295958835341364 | 0.9578338353413656 | 0.5565210843373494 |

## Scalability Length (Seconds)

| **dataset_length** | **DAMP**           | **DBStream**       | **LSTM-AD**        | **Normalizing Flows** | **S2G++1p-KDE**    | **S2G++20p-KDE**   | **S2G++20p-KDE-Distributed** | **Torsk**          | **k-Means**        | **mSTAMP**         |
| ------------------ | ------------------ | ------------------ | ------------------ | --------------------- | ------------------ | ------------------ | ---------------------------- | ------------------ | ------------------ | ------------------ |
| **10000.0**        | 12.075611035029093 | 9.348547538121542  | 3.2856557369232178 | 4.542788585027059     | 1.3018639087677002 | 1.2011919816335042 | 1.41                         | 16.68769347667694  | 4.743401845296224  | 19.197791973749798 |
| **20000.0**        | 13.092211564381918 | 11.285099744796753 | 4.064898570378621  | 4.829745769500732     | 1.6622765858968098 | 1.416413386662801  | 1.2533333333333332           | 32.92470562458038  | 15.050610621770224 | 29.169357538223267 |
| **40000.0**        | 15.649154980977377 | 16.905903339385986 | 5.791442632675171  | 5.314453999201457     | 2.397040049235026  | 1.6868778069814045 | 1.36                         |                    | 30.949349880218502 | 52.539663235346474 |
| **80000.0**        | 19.910025993982952 | 24.499158143997192 | 9.488367795944214  | 5.58642824490865      | 3.7058140436808267 | 2.347942670186361  | 1.6033333333333335           | 129.910418510437   | 49.090735832850136 | 105.27639039357503 |
| **160000.0**       | 29.01512058575948  | 45.515793800354004 | 16.417590618133545 | 6.769598404566447     | 6.730244716008504  | 3.7460657755533853 | 2.12                         | 261.6010913848877  | 87.97411902745564  | 246.97682166099548 |
| **320000.0**       | 48.28951462109884  | 75.81388735771179  | 30.331711053848267 | 9.351157426834106     | 12.616399049758911 | 6.75771164894104   | 3.0366666666666666           | 513.1366304556528  | 247.7031650543213  | 680.5834542910258  |
| **640000.0**       | 121.64392439524333 | 150.4646205107371  | 57.64446973800659  | 14.137539784113565    | 23.71082814534505  | 12.772179047266642 | 4.483333333333333            | 1016.2230826616288 | 350.16846052805585 | 2480.4266378084817 |
| **1280000.0**      | 354.952360312144   | 299.86670994758606 | 114.48484245936076 | 23.402103424072266    | 43.65340534845988  | 25.39780306816101  | 7.8                          | 2046.2930001020432 | 881.837824344635   | 10058.95285987854  |
| **2560000.0**      | 775.7102287610372  | 610.2582166989645  |                    | 42.55691782633463     | 85.1538044611613   | 51.89838910102844  | 14.386666666666665           | 4183.852019945781  | 1336.9886227846146 |                    |
| **5120000.0**      | 2599.2843623956046 | 1211.973451455434  |                    |                       | 168.20808506011963 | 106.54486052195232 | 28.30333333333333            | 8028.050092697144  | 2179.2367794513702 |                    |

## Scalability Width (Seconds)

| **dataset_width** | **DAMP**           | **DBStream**       | **LSTM-AD**        | **Normalizing Flows** | **S2G++1p-KDE**    | **S2G++20p-KDE**   | **S2G++20p-KDE-Distributed** | **Torsk**          | **k-Means**        | **mSTAMP**         |
| ----------------- | ------------------ | ------------------ | ------------------ | --------------------- | ------------------ | ------------------ | ---------------------------- | ------------------ | ------------------ | ------------------ |
| **1.0**           | 12.075611035029093 | 9.348547538121542  | 3.2856557369232178 | 4.542788585027059     | 1.3018639087677002 | 1.2011919816335042 | 1.41                         | 16.68769347667694  | 4.743401845296224  | 19.197791973749798 |
| **2.0**           | 17.467657407124836 | 20.218186060587566 | 3.3384247620900473 | 4.557957649230957     | 1.3639200528462727 | 1.48196013768514   | 1.18                         | 17.2236385345459   | 5.087292512257894  | 29.303621292114258 |
| **4.0**           | 32.91497882207235  | 121.27050550778706 | 3.611283302307129  | 4.59865125020345      | 1.8072455724080403 | 1.9404499530792234 | 1.2633333333333334           | 28.70516574382782  | 5.525273402531941  | 45.396846771240234 |
| **6.0**           | 42.82834680875143  | 480.99190560976666 | 3.601776917775472  | 4.6883517901102705    | 2.260209242502848  | 2.4166566530863443 | 1.4033333333333333           | 29.356188853581745 | 5.778182903925578  | 62.06157064437866  |
| **8.0**           | 55.562777280807495 | 844.2580451170603  | 3.6658533414204917 | 4.620950698852539     | 2.6820371945699057 | 2.6612462997436523 | 1.1866666666666668           | 36.36633038520813  | 6.244294166564941  | 80.52430327733357  |
| **10.0**          | 68.48312910397847  | 1062.2268037001293 | 3.743560314178467  | 4.535080591837565     | 3.060086170832316  | 3.3338159720102944 | 1.6033333333333335           | 35.71759879589081  | 6.863771756490071  | 98.25729060173035  |
| **12.0**          | 82.49880178769429  | 1312.9044578870137 | 3.793130874633789  | 4.525184551874797     | 3.4842395782470703 | 3.7656898498535156 | 1.7133333333333332           | 37.29258894920349  | 6.822491963704427  | 117.95340887705485 |
| **14.0**          | 90.51881257692973  | 1523.287297487259  | 3.9435561498006186 | 4.6252249876658125    | 4.003415425618489  | 4.3387344678243    | 1.8166666666666667           | 35.601834416389465 | 7.522425254185994  | 134.5978283882141  |
| **16.0**          | 116.64748032887776 | 1723.3104089895885 | 3.711128075917562  | 4.745351473490397     | 4.424281199773152  | 4.765927871068318  | 1.9233333333333331           | 31.660951137542725 | 7.638348420461019  | 152.87937259674072 |
| **18.0**          | 122.75802985827129 | 1955.4230727354686 | 3.9406041304270425 | 4.6945118109385175    | 4.802847385406494  | 5.183344999949138  | 2.0366666666666666           | 37.374690771102905 | 8.550241549809774  | 174.99589657783508 |
| **20.0**          | 128.34047985076904 | 2192.9152540365853 | 3.9133986632029214 | 4.856647888819377     | 5.674747069676717  | 6.041692574818929  | 2.1666666666666665           | 35.20727777481079  | 8.485737880071005  | 195.6306687196096  |
| **50.0**          | 344.4562503496806  | 5699.3187121550245 | 4.521922826766968  |                       | 14.541966756184896 | 15.162824233373007 | 4.086666666666667            | 46.64571273326874  | 14.823659499486288 | 520.5065803527832  |
| **100.0**         | 793.7266813119253  | 11255.891539176306 | 14.204445997873941 |                       | 29.790454308191936 | 31.270607630411785 | 7.446666666666666            | 63.95404569307963  | 22.300610780715942 | 1109.5663034121196 |
| **200.0**  | 1629.9643823305767 | 22596.336089611053 | 14.970733404159546 | | 75.0127313931783   | 75.78184668223064  | 16.456666666666667 | 269.0402355194092  | 44.739540576934814 | 2246.95068359375   |
| **500.0**  | 4056.7618872324624 |                    | 15.025033712387083 | |                    |                    | 51.10999999999999  | 1264.844603061676  | 98.53497529029846  | 5804.233536958695  |
| **1000.0** | 8153.6903151671095 |                    | 43.55677366256714 | |                    |                    | 194.0              | 4581.0699853897095 | 199.5178084373474  | 11967.08388543129  |


# References

[1] _Exathlon: A Benchmark for Explainable Anomaly Detection over Time Series._ Vincent Jacob, Fei Song, Arnaud Stiegler, Bijan Rad, Yanlei Diao, and Nesime Tatbul. Proceedings of the VLDB Endowment (PVLDB), 14(11): 2613 - 2626, 2021.
