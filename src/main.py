import httpx
import re
import utils.clean_up as clean_up
import utils.segmentation as segmentation
from rapidfuzz import process, fuzz

'''
Full pipeline

1. Download: obtain a single parliamentary session. No enhanced crawler
functionality, very bare-bones
2. Clean up: de-hyphenation, removing irrelavant data, like page separators, 
etc.
3. Orator identification: capture which MP was speaking for a specific 
intervention
4. Speaker resolution: identify the speaker, if possible, by name and/or party.
Unknown speakers are flagged for later resolution.
5. Comparison: contrast with original document to understand if the pipeline is
working properly and reliably
'''

PRESIDENT = ''

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

def extract_mp_roster(text):
    text_split = text.splitlines()
    mps_present_flag, mps_absent_flag = False, False
    mps_present, mps_absent = [], []
    for line in text_split:
        if (pres:=re.search(r"Presidência do Ex\.mo Sr.(?P<president_name>[A-Za-zçáéíóúãõâêôà ()\S.]+)",line)):
            global PRESIDENT
            PRESIDENT = pres.group("president_name").strip()
            continue
        if re.match(r"^São os seguintes:$",line,flags=re.M):
            mps_present_flag = True
            continue
        elif re.match(r"Não compareceram.*",line):
            mps_present_flag = False
            mps_absent_flag = True
            continue
        elif re.match(r"(A|À)s \d.*",line):
            break

        if mps_present_flag and "Entraram" not in line:
            line = line.replace(',', '.')
            line = line.split('.')
            mps_present += [re.sub(r"^.*?(?P<char>\w)",r"\g<char>",x) for x in line if x!='']
        elif mps_absent_flag:
            line = line.replace(',', '.')
            line = line.split('.')
            mps_absent += [re.sub(r"^.*?(?P<char>\w)",r"\g<char>",x) for x in line if x!='']
        
    #print(mps_present+mps_absent)
    #[print(x) for x in mps_present+mps_absent if ',' in x]
    #print("Number of MPs (total): ",len(mps_present+mps_absent))

    return mps_present+mps_absent

def normalize_name(name):
    # Remove trailing white spaces
    name = name.strip()

    return name
    


def match_speaker(raw, roster, threshold=90):
    # Normalize
    name = normalize_name(raw)

    # Obtain MP name if Minister
    if ("Ministro" in name or "ministro" in name):
        if ('(' in name and ')' in name):
            name = re.search(r"\(\s*(?P<mp_name>.*?)\s*\)",name).group("mp_name").strip()
            return {
                "speaker_raw": raw,
                "match": name,
                "score": 100,
                "needs_review": False,
            }
        else: # no parenthesis, cannot extract name
            return {
                "speaker_raw": raw,
                "match": "Unknown Minister",
                "score": 100,
                "needs_review": False,
            }

    # If Presidente or Orador, match directly for the session
    if (("Presidente" in name or "presidente" in name) and 'vice' not in name and 'Vice' not in name):
        return {
            "speaker_raw": raw,
            "match": PRESIDENT,
            "score": 100,
            "needs_review": False,
        }
    if ("Orador" in name or "orador" in name):
        return {
            "speaker_raw": raw,
            "match": "Orador",
            "score": 100,
            "needs_review": False,
        }

    # If unknown MP ("Um Deputado"), store as unknown
    if ("Deputado" in name or "deputado" in name):
        return {
            "speaker_raw": raw,
            "match": "Unknown MP",
            "score": 100,
            "needs_review": False,
        }


    # Otherwise, fuzzy match

    # If needed, remove everything inside the parenthesis
    if ('(' in name and ')' in name):
        name = re.sub(r"\(.*?\)","",name).strip()

    best, score, _ = process.extractOne(
        name, roster, scorer=fuzz.token_set_ratio
    )
    return {
        "speaker_raw": raw,
        "match": best,
        "score": score,
        "needs_review": score < threshold,
    }

def poc():
    # Runs the pipeline

    # 0. Download the session
    #text = download_session()
    text = open('./data/raw/137_1914-07-29.txt','r').read()


    # 1. Clean up data
    text = clean_up.exec(text)


    # 2. Segmentation
    intervention_dict = segmentation.exec(text)

    # 3. Speaker resolution
    mps =extract_mp_roster(text)
    for intervention in intervention_dict.items():
        if intervention[0]:
            matched_speaker = match_speaker(intervention[0], mps)
            print(matched_speaker)
            #intervention['matched_speaker'] = matched_speaker

    print("✅ Proof-of-Concept (PoC) complete.\n")


if __name__=="__main__":
    print("➡️  Starting proof-of-concept (PoC)...\n")
    poc()


# ^O Sra?\. Deputad[oa] (?P<mp_name>.*): -$