import os
import csv
from collections import defaultdict
from django.conf import settings
import json
from . import classes


def read_vocab_csv(categoria):
    vet_names = defaultdict(list)
    occ = defaultdict(list)
    
    if categoria == 'ses_raca' or categoria == 'raca_gen':
        categoria = 'raca'

    csv_path_vocab = os.path.join(settings.BASE_DIR, 'forms_bbq/data/', 'vocabulary.csv')
    with open(csv_path_vocab, mode="r", newline='', encoding='utf-8') as csv_file:
        vocab = csv.DictReader(csv_file)
        leitor_vocab = list(vocab)
        for elem in leitor_vocab:
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
        
    eng = {'NAME1': eng_m1, 'NAME2': eng_m2}
    pt = {'NOME1': pt_m1, 'NOME2': pt_m2}
        
    resultado_dict = {'Eng': eng, 'Ptbr': pt}
    return resultado_dict



def readCSV(categorias):
    '''
    A partir das categorias, verifica os arquivos csv e guarda na memoria
    como um objeto da classe Perguntas
    '''
    dados = []
    namefile = {
        'idade':'age_unique.csv', 
        'pcd': 'disability_unique.csv', 
        'religiao':'religion_unique.csv',
        'genero': 'gender_unique.csv',
        'ap_fis':'physical_unique.csv',
        'ses':'ses_unique.csv',
        'nascio': 'nationality_unique.csv',
        's_o': 'sexual_orient_unique.csv',
        'raca_gen':'race_gender_unique.csv',
        'ses_raca':'race_ses_unique.csv',
        'raca': 'race_unique.csv'
    }
    colunas = [
        'Contador','Q_id','Ambiguous_Context','Disambiguating_Context',
        'Names', 'Lexical_diversity','Question_negative_stereotype',
        'Question_non_negative','Answer_negative','Answer_non_negative',
        'Relevant_social_values','Known_stereotyped_groups','Contexto_Ambiguous',
        'Contexto_Disambiguating','Nomes','Diversidade_lexical',
        'Questao_negativa_stereotype','Questao_nao_negativa','Resposta_negativa',
        'Resposta_nao_negativa','Relevancia_social', 'grupos_esteriotipado'
    ]

    #pre-carregamento das informações faltantes das categorias nascionalidade, raca-ses, raca_ses, raça, religiao e genero
    info_names = {
        'nascio': read_vocab_csv('nascio'),
        'ses_raca': read_vocab_csv('raca'),
        'raca_gen': read_vocab_csv('raca'),
        'raca': read_vocab_csv('raca'),
        'religiao': read_vocab_csv('religiao'),
        'genero': read_vocab_csv('genero'),
        'ses': read_vocab_csv('ses'),
        's_o': read_vocab_csv('s_o'),
        'idade': read_vocab_csv('idade')
    }
    #recebe o dicionario de categorias por parametro
    aux_categoria = dict(list(categorias.items()))
    print(aux_categoria)
    str_replace = ['Contexto_Ambiguous','Contexto_Disambiguating','Questao_negativa_stereotype','Questao_nao_negativa','Resposta_negativa','Resposta_nao_negativa']

    for cat in aux_categoria:
        if cat in namefile:
            arquivo = namefile.get(cat)
            #obtendo as perguntas de todos os arquivos obtidos pelas categorias selecionadas
            if arquivo:
                print("ARQUIVO: ", arquivo)
                csv_path = os.path.join(settings.BASE_DIR, 'forms_bbq/data/', arquivo)
                
                try:                    
                    with open(csv_path,mode="r", newline='', encoding='utf-8') as csv_file:
                        leitor = csv.DictReader(csv_file)
                        aux_linhas  = list(leitor)

                        #definindo as colunas
                        col_eng = colunas[2:11]
                        col_pt = colunas[12:21]

                        #acessando as colunas do csv
                        for linha in aux_linhas:
                            elem = classes.Perguntas.criarLinha(linha, arquivo, cat, info_names)
                            dados.append(elem)
                except FileNotFoundError:
                    print(f'Aviso: Arquivo não encontrado em {csv_path}! :(')     
                    continue
    return dados

def writeCSV(dados):
    colunas = ['Contador','Q_id','Ambiguous_Context','Disambiguating_Context','Names', 'Lexical_diversity','Question_negative_stereotype','Question_non_negative','Answer_negative','Answer_non_negative','Relevant_social_values','Known_stereotyped_groups','Contexto_Ambiguous','Contexto_Disambiguating','Nomes','Diversidade_lexical','Questao_negativa_stereotype','Questao_nao_negativa','Resposta_negativa','Resposta_nao_negativa','Relevancia_social', 'grupos_esteriotipado']
    arq_lidos = {} #guarda dict com files, escritor
    try:
        for linha in dados:
            arquivo_atual = linha.get_arquivo()

            if arquivo_atual not in arq_lidos:
                csv_path = os.path.join(settings.BASE_DIR,'forms_bbq/data/', arquivo_atual)
                file =  open(csv_path, mode="w", newline="") 
                escritor = csv.DictWriter(file, fieldnames=colunas)
                escritor.writeheader()
                arq_lidos[arquivo_atual] = {'file': file, 'escritor': escritor}
            
            escritor_atual = arq_lidos[arquivo_atual]['escritor']
            escritor_atual.writerow(linha.get_linha())
            
    finally:
        for gerenciador in arq_lidos.values():
            gerenciador['file'].close()
    