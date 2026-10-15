import os
import csv
from collections import defaultdict
from django.conf import settings

def readGerenciador(categorias):
   
    lista_ids = {}
    #path_gerenciador = os.path.join(settings.BASE_DIR, 'forms_bbq/data/gerenciador4.csv')
    
    path_gerenciador = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
     'data',
    'gerenciador_4.csv'
)
    aux_categoria = dict(list(categorias.items()))

    #agrupando as categorias de acordo com os pesos
    agrupado = defaultdict(list)
    for categoria, peso in aux_categoria.items():
        agrupado[peso].append(categoria)
        
        #ordena por peso de forma descrente
    grupos =  dict(sorted(agrupado.items())) 
    print("Grupos",grupos)
                
    pesos = {i: v for i,v in enumerate(grupos.values(), start=1) }
                   
    aux_pesos =dict(sorted(pesos.items(), reverse=True))
    
    list_pesos = {}
    for peso, grupos in aux_pesos.items():
        
        for cat in grupos:
           
            list_pesos[cat] = peso
    print(list_pesos)
    MAX_PERGUNTAS = 20
    qtd_perguntas = 0
    qtd_categoria = 0

    with open(path_gerenciador, mode='r', newline='', encoding='utf-8') as csv_file:
            leitor = csv.DictReader(csv_file)
            campos = leitor.fieldnames
            tupla = list(leitor)
    
    for cat, peso in list_pesos.items():
            
        if qtd_perguntas >= MAX_PERGUNTAS:
            break

        print(f"Categoria: {cat} | Peso: {peso}")

        linhas_categoria = [linha for linha in tupla if linha['Categoria'] == cat]
        escolha = None

        linhas_categoria.sort(key=lambda l: int(l['Contador']))

        for escolha in linhas_categoria[:peso]:
                lista_ids.setdefault(cat, []).append([escolha['Q_id'], escolha['Arquivo']])
                escolha['Contador'] = str(int(escolha['Contador']) + 1)
                
    with open(path_gerenciador, mode='w', newline='', encoding='utf-8') as csv_file:
        escritor = csv.DictWriter(csv_file, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(tupla)
    print(lista_ids)

    return lista_ids



#aux = {'genero': 0.16, 'raca': 0.16, 'pcd': 0.16, 'raca_gen': 0.12, 'ses_raca': 0.12, 'ses': 0.08, 'idade': 0.04, 'religiao': 0.04, 's_o': 0.04, 'ap_fis': 0.04, 'nascio': 0.04}

#readGerenciador(aux)