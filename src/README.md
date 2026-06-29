# Proof-of-Concept (PoC)

The main purpose of this module was to test the tractibility of the project.
Before diving all in and implementing all the pipelines that would actually
result in a useful end-product, it was decided that some preliminary tests
should be run to ensure that the project was indeed possibly and could be
fruitful.

Therefore, the main point of this component was to implement some very 
rudimentary stages of the pipeline and output a dictionary containing the
debate sorted by MPs and respective intervention.

The stages implemented were:
1. Download: obtain a single parliamentary session. No enhanced crawler
functionality, very bare-bones
2. Clean up: de-hyphenation, removing irrelavant data, like page separators, 
etc.
3. Orator identification: capture which MP was speaking for a specific 
intervention
4. Comparison: contrast with original document to understand if the pipeline is
working properly and reliably

To run, first install the required dependencies. From the root directory:
```
pip install -r requirements.txt
```

Thereafter:
```
python3 proof-of-concept/PoC.py
```

If you want to see the end result printed in the terminal, uncomment the 
line that contains `print(intervention_dict)` in `PoC.py` (line 64)

