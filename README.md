# ProKnow Renaming Rules Synchronization Tool

The ProKnow Renaming Rules Synchronization Tool provides a Python script that can automatically synchronize synonym renaming rules from an Excel workbook to a ProKnow domain. This tool is focused on supporting large-scale implementations of ProKnow where managing the various permutations of synonym renaming rules can be challenging.


## Getting Started

### Installing Python

Before you can run the synchronization script, you must first ensure that you have a recent version of [Python 3](https://www.python.org/downloads/) installed on your system. You can check the current version of Python by running the following command in a terminal:

```
$ python --version
```

If this command reports a version starting with "3" (e.g., "Python 3.9.5"), you have a suitable version of Python installed. Please note that in some older systems, the main `python` executable may be version "2". In that case, you may want to try to run the following command instead:

```
$ python3 --version
```

If command reports a version starting with "3" you should substitute any `python` calls in this document with `python3` instead.

### Installing Python Requirements

The synchronization scripts utilize several packages and modules that must be installed prior to executing the script. The easiest way to install these packages and modules in an isolated way is to utilize a [Python Virtual Environment](https://docs.python.org/3/tutorial/venv.html). Begin my running the following command from within the source directory:

```
$ python3 -m venv .venv
```

This will create a virtual environment in the `.venv` folder. Once you’ve created a virtual environment, you may activate it.

On Windows, run:
```
.venv\Scripts\activate.bat
```

On Unix or MacOS, run:
```
$ source .venv/bin/activate
```

Once activated, you may install the necessary packages and modules in the virtual environment by running the following command (note that the command is run from within the virtual environment):

```
(.venv) $ pip install -r requirements.txt
```

Once installed, you can then run the script as described below.

Please note that in most systems, activating a virtualenv gives you a shell function named:
```
$ deactivate
```
which you can run in order to exit the virtual environment and put things back to normal.


## Renaming Rule Data

Before running the synchronization script, you must first create the necessary Excel workbook which contain the desired synonym renaming rules. You provide the path to the workbook containing the synonym renaming rules as an argument to the script.

An example Excel workbook has been provided in the `examples` directory. The format is very simple, with each column in the sheet representing a single structure. The first row represents the desired name of the structure, and all subsequent rows represent the synonyms.


## Synchronization

Once you have installed the prerequisites and created the necessary Excel workbook containing the desired synonym renaming rules, you may run the synchronization script by running the following command (substituting proper values for the url, credentials, and location of the file):

```
(.venv) $ python renaming-rules-sync.py --url https://example.proknow.com --credentials /path/to/credentials.json ./examples/renaming_rules.xlsx
```

Please note that you will be prompted each time before creating or updating renaming rules, and the script never deletes any renaming rules (however, it will list any renaming rules that were not defined in the workbook at the end of the script).

You may run access the help information for the script by running the following command:

```
(.venv) $ python renaming-rules-sync.py --help
```
