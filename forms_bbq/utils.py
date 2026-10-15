import os
import csv
import random
from collections import defaultdict

from django.conf import settings

from django.db.models import Count

from . import classes
from .models import ContadorPergunta
MAX_PERGUNTAS = 20
DATA_DIR = os.path.join(settings.BASE_DIR,'forms_bbq/data/')

CATEGORIAS_COM_VOCAB = {'nascio', 'ses_raca','raca_gen', 'raca', 'religiao', 'genero', 'ses', 's_o'}


def read_vocab_csv(categoria):
    vet_names = defaultdict(list)
    
    
    if categoria == 'ses_raca' or categoria == 'raca_gen':
        categoria = 'raca'

    csv_path_vocab = os.path.join(DATA_DIR, 'vocabulary.csv')
    
    with open(csv_path_vocab, mode="r", newline='', encoding='utf-8') as csv_file:
        #vocab = csv.DictReader(csv_file)
        #leitor_vocab = list(vocab)
        for elem in csv.DictReader(csv_file):
            if elem['Category'] == categoria:
                vet_names['Eng'].append(elem['Name'])
                vet_names['Ptbr'].append(elem['Nomes'])
                
    tam = len(vet_names['Eng'])
    meio = tam // 2

    if tam > 10:
        step = max(1, meio // 6)
        eng_m1 = ', '.join(vet_names['Eng'][0:meio:step])
        eng_m2 = ', '.join(vet_names['Eng'][meio:tam:step])
        
        pt_m1 = ', '.join(vet_names['Ptbr'][0:meio:step])
        pt_m2 = ', '.join(vet_names['Ptbr'][meio:tam:step])
    else: 
        eng_m1 = ', '.join(vet_names['Eng'][:meio])
        eng_m2 = ', '.join(vet_names['Eng'][meio:])
        
        pt_m1 = ', '.join(vet_names['Ptbr'][:meio])
        pt_m2 = ', '.join(vet_names['Ptbr'][meio:])
        
    return {
        'Eng': {'NAME1': eng_m1, 'NAME2': eng_m2},
        'Ptbr': {'NOME1': pt_m1, 'NOME2': pt_m2},
    }



def readCSV(lista_ids):
    '''
    A partir dos ids, verifica os arquivos csv e guarda na memoria
    como um objeto da classe Perguntas
    '''

    #procura os vocabularios das categorias sorteadas
    info_names = {
        cat: read_vocab_csv(cat)
        for cat in lista_ids if cat in CATEGORIAS_COM_VOCAB
    }

    #agrupa os ids por arquivos vindos da lista de sorteados
    ids_per_arq = defaultdict(set)
    for itens in lista_ids.values():
        for id, arquivo in itens:
            ids_per_arq[arquivo].add(str(id))

    sent_encontradas = {}
    for arquivo, ids in ids_per_arq.items():
        csv_path = os.path.join(DATA_DIR, arquivo)
        try:
            with open(csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
                for linha in csv.DictReader(csv_file):
                    if linha['Q_id'] in ids:
                        sent_encontradas[(arquivo,linha['Q_id'])] = linha
        
        except FileNotFoundError:
            print(f"Aviso: O arquivo {csv_path} não foi encontrado! \n")

    #montando o objeto Pergunta
    dados = []
    
    for cat,itens in lista_ids.items():
        for q_id, arquivo in itens:
            linha = sent_encontradas.get((arquivo,str(q_id)))

            if linha is None:
                print(f'Aviso: Q_id {q_id} não encontrada!\n')
                continue

            dados.append(classes.Perguntas.criarLinha(linha, arquivo, cat, info_names))
            
    return dados

def readGerenciador(categorias):
   
    lista_ids = {}
    #path_gerenciador = os.path.join(settings.BASE_DIR, 'forms_bbq/data/gerenciador4.csv')
    
    path_gerenciador = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),'data','gerenciador_4.csv')
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

    with open(path_gerenciador, mode='r', newline='', encoding='utf-8') as f:
            tupla = list(csv.DictReader(f))

    ContadorPergunta.objects.bulk_create([ContadorPergunta(q_id=linha['Q_id']) for linha in tupla], ignore_conflicts=True,)
        
    #lendo o contador
    contadores = dict(ContadorPergunta.objects.values_list('q_id','contador'))
    

    for cat, peso in list_pesos.items():
        if qtd_perguntas >= MAX_PERGUNTAS:
            break

        qtd = min(peso, MAX_PERGUNTAS - qtd_perguntas)

        print(f"Categoria: {cat} | Peso: {peso}")

        linhas_categoria = [linha for linha in tupla if linha['Categoria'] == cat]


        #sorteado 
        random.shuffle(linhas_categoria)
        linhas_categoria.sort(key=lambda l: contadores.get(l['Q_id'], 0))

            
        for escolha in linhas_categoria[:qtd]:
                    lista_ids.setdefault(cat, []).append([escolha['Q_id'], escolha['Arquivo']])
                    #escolhidos.append(escolha['Q_id'])
                    qtd_perguntas += 1
                  
    
    print(lista_ids)

    return lista_ids
