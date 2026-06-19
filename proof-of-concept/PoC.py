import httpx
import re
import utils.clean_up as clean_up
import utils.segmentation as segmentation

'''
Proof-of-Concept (PoC)

The goal is to test whether the project is tractable, i.e., understand if it is
possible to sort a parliamentary debate by speaker and identify interjections.

To do this, only very rudimentary steps are implemented. Concretely:
1. Download: obtain a single parliamentary session. No enhanced crawler
functionality, very bare-bones
2. Clean up: de-hyphenation, removing irrelavant data, like page separators, 
etc.
3. Orator identification: capture which MP was speaking for a specific 
intervention
4. Comparison: contrast with original document to understand if the pipeline is
working properly and reliably
'''

# Downloads session from official website
def download_session():
    # Parameters obtained from the Parlamento website
    session_n = "137"
    session_date = "1914-07-29"
    data = {
        'exportType':'txt',
        'exportControl':'documentoCompleto',
        'periodo':'r1',
        'publicacao':'cd',
        'serie':'01',
        'legis':'01',
        'sessao':'04',
        'numero':session_n,
        'data':session_date,
        'exportar':'Exportar',
    }

    # Make request
    r = httpx.post('https://debates.parlamento.pt/pagina/export', data=data)

    # Save to file
    file_name = session_n + "_" + session_date
    with open('./data/raw/'+file_name+".txt",'w') as file:
        file.write(r.text)
    print("\t✅ Parliament Session Download complete.\n")
    return r.text


def poc():
    # Runs the pipeline

    # 1. Download the session
    text = download_session()

    # 2. Clean up data
    text = clean_up.exec(text)

    # 3. Segmentation
    intervention_dict = segmentation.exec(text)

    #print(intervention_dict)

    print("✅ Proof-of-Concept (PoC) complete.\n")


if __name__=="__main__":
    print("➡️  Starting proof-of-concept (PoC)...\n")
    poc()


# ^O Sra?\. Deputad[oa] (?P<mp_name>.*): -$