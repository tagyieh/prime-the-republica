import re

def split_interventions(text):
    # Currently, the interventions are in multiple lines. The goal of this
    # function is to make sure that each line contains only one intervention or
    # some other data
    
    split_text = text.splitlines()
    new_text, cur_line = '', ''
    for line in split_text:
        # There is an orator starting
        if (a := re.match(r"^(((O|Um) Sr. Deputado)|(O Sr. (?P<orator_name>[A-Za-zçáéíóúãõâêôà ()\S.]+))|(O Orador)) ?(:-|:—|: —|: -)",line)):
            new_text += cur_line + '\n\n'
            cur_line = line.strip('\n')
        else:
            cur_line += line.strip('\n')
    
    new_text += cur_line + '\n\n'

    print("\t✅ Lines split by intervention.")
    return new_text

def get_orators(text):
    intervention_dict = {}
    for line in text:
        regex = re.compile(r"^(((O|Um) Sr. (?P<anon_mp>Deputado))|(O Sr. (?P<orator_name>[A-Za-zçáéíóúãõâêôà ().]+))|(O (?P<orator>Orador))) ?(:-|:—|: —|: -|:—)(?P<intervention>.+)",flags=re.M)
        matches = [x.groupdict() for x in regex.finditer(line)]
            
        for match in matches:
            orator = ''
            if "orator_name" in match and match["orator_name"]!=None:
                orator = match["orator_name"]
            elif "anon_mp" in match and match["anon_mp"]!=None:
                orator = "Deputado"
            else:
                orator = "Orador"
                
            intervention_dict[orator] = match["intervention"]
    print("\t✅ Interventions sorted by orator.")
    return intervention_dict

def exec(text):
    print("➡️  Extracting interventions...")
    text = split_interventions(text)
    intervention_dict = get_orators(text.split('\n'))
    intervention_dict = {k: v for k, v in sorted(intervention_dict.items(), key=lambda item: len(item[1]))}
    #[print("Orator: ",y,"\nIntervention: ",x) for y,x in intervention_dict.items() if len(x)==663]
    print()
    return intervention_dict

'''
O Sr. Lúcio de Azevedo: — 
O Orador:—
O Sr. Gastão Rodigues: — 
O Sr. Presidente do Ministério e Ministro do Interior (Bernardino Machado): — 
'''