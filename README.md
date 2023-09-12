# IndIE

This is the code for the paper titled "IndIE: A Multilingual Open Information Extraction Tool For Indic Languages" accepted in the Findings of IJCNLP-AACL 2023.

## Installation

* Git clone.
* Make a new virtual environment.
    * Upgrade pip by ```pip install -U pip```
* Install the necessary libraries by using the following command:
```pip install -r requirements.txt```
    * If you face any difficulty in installing any library then we recommend to install it without version number. Hence, pip will install from the latest version.
    * However, we do not recommend this for stanza library because a different version of stanza library will yield in different dependency parse trees [[source]](https://github.com/stanfordnlp/stanza/issues/990).

## Download Models

Download the relevant files from [here](https://drive.google.com/file/d/1UqOUdeK96m6EabI-cg2EeBz6p3IwrPZ6/view?usp=sharing).

Your directory structure should look like this:

```
.
├── chunking
│   ├── chunking_model.py
│   ├── crf_chunker.py
│   ├── data
│   │   └── my_tagset_BI.bin
│   └── state_dicts
│       └── model
│           ├── 26_epoch_4.pth.tar
│           └── sklearn_crf_model_v2_pos_mapped_2.pkl
├── main.py
├── README.md
├── requirements.txt
└── utils.py
```

## Extracting triples

Specify the language and list of strings in the ```main.py``` file. 

On GPU, make sure you have same device order on nvidia-smi and PCI bus. Command: ```export CUDA_DEVICE_ORDER=PCI_BUS_ID```

Run

```CUDA_VISIBLE_DEVICES=0 python main.py```

where ```0``` is your GPU ID. The code also runs in absence of GPU but takes a little longer. In order to run the code only on CPU, simply omit the GPU ID.

## Citation

```Will be updated```


