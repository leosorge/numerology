import os

file_path = 'numerology_api.py'
temp_path = 'numerology_api_fixed.py'

def clean_indentation(path):
    tab_count = 0
    new_lines = []
    
    if not os.path.exists(path):
        print(f"Errore: Il file {path} non esiste nella cartella corrente.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        # Conta i tab prima di sostituirli
        tab_count += line.count('\t')
        # Sostituisce i tab con 4 spazi
        clean_line = line.replace('\t', '    ')
        
        # Forza la rimozione di spazi bianchi a sinistra per le ultime righe specifiche
        if clean_line.strip().startswith('if __name__ == "__main__":'):
            new_lines.append('if __name__ == "__main__":\n')
        elif clean_line.strip().startswith('app.run(debug=True)'):
            new_lines.append('    app.run(debug=True)\n')
        else:
            new_lines.append(clean_line)

    with open(temp_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("-" * 30)
    print(f"RISULTATO ANALISI:")
    print(f"Tabulazioni (\t) trovate e rimosse: {tab_count}")
    print(f"File corretto salvato come: {temp_path}")
    print("-" * 30)

if __name__ == "__main__":
    clean_indentation(file_path)
