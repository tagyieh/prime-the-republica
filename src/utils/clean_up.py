import re
import unicodedata

# → Odd pages start with "Sessão de DD|D de MM de YYYY", where months are 
#   written in full
# → Even pages start with "Diário da Câmara dos Deputados"
# → Both are alone in their respective lines
# This function removes both
def remove_page_artifacts(text):
    odd_page_artifact_regex = r"^Sessão de [0-9]* de [A-Za-zç]* de [0-9]*$"
    text = re.sub(odd_page_artifact_regex,'',text,flags=re.MULTILINE)

    # Trailing characters are handled
    even_page_artifact_regex = r"^.*iário da Câmara dos Deputado.*$" 
    text = re.sub(even_page_artifact_regex,'',text,flags=re.MULTILINE)

    # Single 1-2 digit number in a line is likely the page number. Remove.
    text = re.sub(r"^[0-9]{1,2}$","",text,flags=re.MULTILINE)
    print("\t✅ Page artifacts removed.")

    return text

def normalize_text(text):
    # If the text is not NFC normalized (e.g. 'é' is actually a wrong byte
    # sequence), correct it
    if unicodedata.is_normalized("NFC", text) is not True:
        text = unicodedata.normalize('NFC', text)

    # Clean trailing white spaces 
    text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"(\n)+","\n",text)

    print("\t✅ Text normalized.")

    return text

def de_hyphenation(text):
    # Find words with the sequence "-\n" in them, indicating a word split
    # Only capture those that are preceeded and suceeded by lowercase letters
    # and avoid predictable patterns (pronomes)

    # Remove hyphens and concatenate for clear word separation
    text = re.sub(r"(?P<pre>[a-zçáéíóúãõâêôà]+)-\n(?!vos\s|me\s|te\s|lhes?\s|os?\s|as?\s|los?\s|las?\s|nos?\s|nas?\s|se\s)(?P<post>[a-zçáéíóúãõâêôà]+)",r"\g<pre>\g<post>",text) 

    # If it is followed by a pronoun, keep hyphen and delete newline
    text = re.sub(r"(?P<pre>[a-zçáéíóúãõâêôà]+)-\n(?P<post>vos\s|me\s|te\s|lhes?\s|os?\s|as?\s|los?\s|las?\s|nos?\s|nas?\s|se\s)",r"\g<pre>-\g<post>",text) 

    # Otherwise, replace with space
    text = re.sub(r"(?P<pre>[a-zçáéíóúãõâêôà]+)-\n(?P<post>\S+)",r"\g<pre> \g<post>",text) 
    
    print("\t✅ Hyphens handled.")

    return text

def remove_empty_lines(text):
    split_text = text.splitlines()
    text = ''
    for line in split_text:
        if len(line):
            text+=line+'\n'

    with open("test.txt",'w') as f:
        f.write(text)
    
    print("\t✅ Lines separated.")
    return text

# Cleans up the downloaded data
def exec(text):
    print("➡️  Starting clean-up...")

    # Normalize text
    text = normalize_text(text)

    # De-hyphenation
    text = de_hyphenation(text)

    # Remove page artifacts
    text = remove_page_artifacts(text)

    # Remove empty lines
    text = remove_empty_lines(text)

    print()
    return text



    