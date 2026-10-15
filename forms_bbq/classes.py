import uuid
import json
from . import utils
from collections import defaultdict


NOMES_CATEGORIAS = {
    'genero':   'Gênero',
    'raca':     'Raça/Etnia',
    'pcd':      'Pessoa com deficiência',
    'raca_gen': 'Raça e gênero',
    'ses_raca': 'Raça e nível socioeconômico',
    'ses':      'Nível socioeconômico',
    'idade':    'Idade',
    'religiao': 'Religião',
    's_o':      'Orientação sexual',
    'ap_fis':   'Aparência física',
    'nascio':   'Nacionalidade',
}


class Classifica_perfil:
    def __init__(self, usuario):
        self.perfil = usuario
        
    
    def class_pcd(self):
        disab =  self.perfil['pcd']

        if 'sim' in disab:
            return 'pcd'
        else:
            return 'n-pcd'
    

    def class_faixa_eta(self):
        faixa = self.perfil['age']

        if 'menos_18' in faixa:
            return 'adolescente'
        elif 'entre_18_24' in faixa or 'entre_25_30' in faixa:
            return 'jovem adulto'
        elif 'entre_31_40' in faixa or 'entre_41_50' in faixa:
            return 'adulto'
        elif 'entre_51_60' in faixa:
            return 'adulto2'
        elif 'mais_61' in faixa:
            return 'idoso'
        else:
            return 'faixa_desconhecida'
    
    def class_genero(self):
        genero  =self.perfil['gender']
        ig = self.perfil['igender']
        
        #genero
        if 'm' in genero:
            aux = 'Mulher'
        elif 'h' in genero:
            aux =  'Homem'
        elif 'nb' in genero or 'nb' in ig:
            aux = 'Nao-binaria'
        elif 'none' in genero or 'other' in genero:
            aux = 'None'
        elif 'none' in genero or 'other' in ig:
            aux = 'None'
        #identidade de genero
        if 'Mulher' in aux or'Homem' in aux:
            if 'cis' in ig:
                aux += ' Cis'
            elif 'trans' in ig:
                aux += ' Trans'
        elif 'Nao-binaria' in aux:
            aux = 'Nao-binaria'
        
        return aux
    
    def class_raca(self):
        raca = self.perfil['race']

        if 'preto' in raca:
            return 'Preto'
        if 'pardo' in raca:
            return 'Pardo'
        elif 'branco' in raca:
            return 'Branco'
        elif 'indigena' in raca:
            return 'Indigena'
        elif 'amarelo' in  raca:
            return 'Amarelo'
        else:
            return 'Outro'
        
    def class_ses(self):
        ses1 = self.perfil['ses1']
        ses2 = self.perfil['ses2']

        if ses1 == 'ses1' or ses1 == 'ses2':
            renda_class = 'baixa'
        elif ses1 in ['ses3', 'ses4', 'ses5','ses6']:
            renda_class = 'media'
        elif ses1 in ['ses7', 'ses8']:
            renda_class = 'alta'
        else:
            renda_class = 'renda_desconhecida'

        # Escolaridade
        if ses2 in ['efi', 'efc', 'emi']:
            escolaridade_class = 'baixa'
        elif ses2 in ['emc', 'esi']:
            escolaridade_class = 'media'
        elif ses2 == 'esc':
            escolaridade_class = 'alta'
        else:
            escolaridade_class = 'escolaridade_desconhecida'

        #define o grau de vulnerabilidade
        if renda_class == 'baixa' and escolaridade_class =='baixa':
            ses_geral = 'vulneravel'
        elif renda_class == 'alta' and escolaridade_class =='alta':
            ses_geral = 'privilegiado'
        else:
            ses_geral = 'intermediario'
        
        return ses_geral
    
    def resumo(self):
        return {
            'pcd': self.class_pcd(),
            'genero': self.class_genero(),
            'raca' : self.class_raca(),
            'faixa_etaria': self.class_faixa_eta(),
            'ses': self.class_ses()
        }
    

class Recomeda_questoes:

        def __init__(self, perfil):
            self.classificador = Classifica_perfil(perfil)
            self.dados_class  = self.classificador.resumo()
        
        def categ_prioritarias(self):
            #todas as categorias e pesos unitarios
            pesos = {'genero': 1, 'raca': 1, 'pcd': 1,'ses':1, 'idade':1, 
                    'raca_gen': 1,'ses_raca':1,'religiao':1,'s_o':1,
                     'ap_fis':1,'nascio':1 }
            
            #Regras de Atribuição de Pesos
            # peso 4 | nivel critico | Mulheres, pessoas trans e nb, não brancos e pcds
            # peso 3 | interseccao   |idosos nao brancos, raça_gen, raça_ses
            # peso 2 | contextual    | ses intermd/baixo, idosos brancos
            # peos 1  | base         | realiza um sorteio entre as categorias
            
            #nivel critico
            #PcD
            if self.dados_class['pcd'] == 'pcd':
                pesos['pcd'] = 4;
            #Genero : mulheres(cis/trans), homens trans e nao binarios
            if any(x in self.dados_class['genero'] for x in  ['Mulher','Trans', 'Não-binaia', 'None']):
                pesos['genero'] = 4;
            
            #Pessoas nao brancas
            if self.dados_class['raca'] != 'Branco':
                pesos['raca'] =  4;
            
            # nivel interseccional
            #Raca x Genero
            if pesos['raca'] == 4 and pesos['genero'] == 4:
                pesos['raca_gen'] = 3

            #Ses x Raca
            if pesos['raca'] == 4 and self.dados_class['ses'] in ['intermediario', 'vulneravel']:
                pesos['ses_raca'] = 3
            
            #idosos nao brancos
            if self.dados_class['faixa_etaria'] == 'idoso' and pesos['raca'] == 4:
                pesos['idade'] = 3
            
            #nivel contextual
            if self.dados_class['ses'] in ['intermediario', 'vulneravel'] and pesos['ses'] == 1:
                pesos['ses'] = 2

            if self.dados_class['faixa_etaria'] == 'idoso' and pesos['idade'] == 1:
                pesos['idade'] = 2
            # Adulto2 (51-60 anos)
            if self.dados_class['faixa_etaria'] == 'adulto2':
                 pesos['idade'] = 2
                 
            total = sum(pesos.values()) 
            print("Pesos: ", pesos, "Total: ", total)
            prob = {x: round(v/total,4)for x, v in pesos.items()}

            #ordena as categorias com peso maior
            categ = dict(sorted(prob.items(), key=lambda x: x[1], reverse=True))
            print('Categorias sugeridas: ', categ)
            return categ,total

class Perguntas:
    #inicializando os atributos da pergunta
    def __init__(self, linha, arquivo, categoria, sect_eng, sect_pt): #inicializando com os atributos da instancia
        self.arquivo = arquivo
        self.categ = categoria
        self.identificador = linha['Q_id'] #carrega a categoria, numero e variação
        
        self.sect_eng = sect_eng
        self.sect_pt = sect_pt
        self.linha = linha
    
    #definindo o getters e setters
    def get_categ(self): return self.categ
    def get_arquivo(self): return self.arquivo
    def get_id(self): return self.identificador
    
    def get_eng(self): return self.sect_eng
    def get_ptbr(self): return self.sect_pt
    def get_linha(self): return self.linha

    
    def perg_format(self): #formato de visualização
        return({
                'Id': self.identificador,
                'Categoria':NOMES_CATEGORIAS.get(self.categ, self.categ), 
                'Eng':self.sect_eng, 
                'Ptbr': self.sect_pt})
    def resumo(self):
        return ({'Id': self.identificador,'Categoria':self.categ})

    @classmethod
    def criarLinha(cls, linha, arq, cat, info_names):
        colunas = [
        'Contador','Q_id','Ambiguous_Context','Disambiguating_Context',
        'Names', 'Lexical_diversity','Question_negative_stereotype',
        'Question_non_negative','Answer_negative','Answer_non_negative',
        'Relevant_social_values','Known_stereotyped_groups','Contexto_Ambiguous',
        'Contexto_Disambiguating','Nomes','Diversidade_lexical',
        'Questao_negativa','Questao_nao_negativa','Resposta_negativa',
        'Resposta_nao_negativa','Relevancia_social', 'grupos_estereotipado'
        ]
        
        col_eng = colunas[2:11]
        col_pt = colunas[12:21]
        str_replace = ['Contexto_Ambiguous','Contexto_Disambiguating','Questao_negativa','Questao_nao_negativa','Resposta_negativa','Resposta_nao_negativa']

        section_eng = {col: linha[col] for col in col_eng if col in linha}
        section_pt = {col: linha[col] for col in col_pt if col in linha}
        if section_eng.get('Names', '') != '':
            dado_pt1, dado_eng1 = {}, {}
            str_tst1 = section_eng.get('Names', '').strip()
            str_tst2 = section_pt.get('Nomes', '').strip()
            try:
                dado_eng1 = json.loads(str_tst1)
                dado_pt1 = json.loads(str_tst2)
            except json.JSONDecodeError:
                # Parsing manual caso falhe o JSON
                temp_eng = {item.split(':', 1)[0].strip(): item.split(':', 1)[1].strip() for item in str_tst1.split('; ') if ':' in item}
                temp_pt = {item.split(':', 1)[0].strip(): item.split(':', 1)[1].strip() for item in str_tst2.split('; ') if ':' in item}
                dado_eng1, dado_pt1 = temp_eng, temp_pt
            except TypeError:
                pass
                
            section_eng['Names'] = {'NAME1': dado_eng1.get('NAME1', []), 'NAME2': dado_eng1.get('NAME2', [])}
            section_pt['Nomes'] = {'NOME1': dado_pt1.get('NOME1', []), 'NOME2': dado_pt1.get('NOME2', [])}
        else:
            # Fallback para o info_names pré-carregado
            dado_eng1 = info_names[cat].get('Eng', [])
            dado_pt1 = info_names[cat].get('Ptbr', [])
            
            section_eng['Names'] = {'NAME1': dado_eng1.get('NAME1', []), 'NAME2': dado_eng1.get('NAME2', [])}
            section_pt['Nomes'] = {'NOME1': dado_pt1.get('NOME1', []), 'NOME2': dado_pt1.get('NOME2', [])}
            
            if 'OCC1' in section_eng.get('Ambiguous_Context', ''):
                dado_eng = info_names['ses'].get('Eng', [])
                dado_pt = info_names['ses'].get('Ptbr', [])
                
                section_eng['Names'].update({'OCC1_eng': dado_eng.get('NAME1', []), 'OCC2_eng': dado_eng.get('NAME2', [])})
                section_pt['Nomes'].update({'OCC1_ptbr': dado_pt.get('NOME1', []), 'OCC2_ptbr': dado_pt.get('NOME2', [])})
                
        # tratamento de Lexical Diversity
        if isinstance(section_eng.get('Lexical_diversity', ''), str) and section_eng.get('Lexical_diversity', '') != '':
            sub1_eng = section_eng['Lexical_diversity'].split('; ')
            sub2_pt = section_pt['Diversidade_lexical'].split('; ') 
            aux_lex = {}

            for i, item in enumerate(sub1_eng):
                tag_word = f'WORD{i+1}'
                tag_pal = f'PALAVRA{i+1}'
                if tag_word in item:
                    string = item.replace(f'{tag_word}: ', '')
                    string2 = sub2_pt[i].replace(f'{tag_pal}: ', '') if i < len(sub2_pt) else ''
                    aux_lex[i] = {tag_word: string, tag_pal: string2}
                   
            tam_lex = len(aux_lex)
            if tam_lex == 1:
                section_eng['Lexical_diversity'] = {'WORD1: ': aux_lex[0].get('WORD1', '')}
                section_pt['Diversidade_lexical'] = {'PALAVRA1: ': aux_lex[0].get('PALAVRA1', '')}
            elif tam_lex > 1:
                section_eng['Lexical_diversity'] = {'WORD1: ': aux_lex[0].get('WORD1', ''), 'WORD2: ': aux_lex[1].get('WORD2', '')}
                section_pt['Diversidade_lexical'] = {'PALAVRA1: ': aux_lex[0].get('PALAVRA1', ''), 'PALAVRA2: ': aux_lex[1].get('PALAVRA2', '')}
        else:
            section_eng['Lexical_diversity'] = {}
            section_pt['Diversidade_lexical'] = {}
                    
        # substituição de tags nas strings traduzidas
        for chave in str_replace:
            if chave in section_pt and isinstance(section_pt[chave], str):
                section_pt[chave] = section_pt[chave].replace('{{NAME1}}', '{{NOME1}}').replace('{{NAME2}}', '{{NOME2}}')
                if '{{WORD1}}' in section_pt[chave]:
                    section_pt[chave] = section_pt[chave].replace('{{WORD1}}', '{{PALAVRA1}}')
                if '{{WORD2}}' in section_pt[chave]:
                    section_pt[chave] = section_pt[chave].replace('{{WORD2}}', '{{PALAVRA2}}')
        print(linha)
        # Retorna a instância da classe criada com os dados limpos
        return cls(linha, arq, cat, section_eng, section_pt)
    
    def from_dict(cls, dados):
        obj = cls()
        obj.set_categoria(dados['Categoria'])
        obj.set_template(dados['Template'])
        

        return obj

class Avaliador():
    def __init__(self, id=None, resp_form=None, aval_perg=None, template_cad=None):
        self.id = self.id = str(id) if id is not None else None
        self.forms = resp_form
        self.templates_select = []
        self.tab_avisosTemplate = []
        self.aval_perg = aval_perg
        self.categorias = []
        self.total_pesos = []
        self.template_cad = template_cad

    def setId(self, id=None):
        self.id = str(id) if id else str(uuid.uuid4())

    def setRespostas(self, respostas):
        respostas = respostas.copy()

        if "token_pk" in respostas:
            respostas["token_pk"] = str(respostas["token_pk"])

        self.forms = respostas

    def getId(self):
        return str(self.id)

    def getRespostas(self):
        return self.forms
    def getTotal(self): return self.total_pesos
   
    def getCategorias(self):
        
        if not self.forms:
            print('aqui')
            return {}
        
        recomendador = Recomeda_questoes(self.forms)
        self.categorias, self.total_pesos = recomendador.categ_prioritarias()
        
        return self.categorias

    def getTemplates(self): return self.templates_select
    def getTabAvisos(self): return self.tab_avisosTemplate

    def vinculaPerguntas(self):
        
        categorias = self.getCategorias()

        #lista com os ids que devemos pegar para a leitura 
        lista_ids_perg = utils.readGerenciador(categorias)
        #perguntas sorteadas
        perguntas = utils.readCSV(lista_ids_perg)


        '''#agrupando as categorias de acordo com os pesos
        agrupado = defaultdict(list)
        for categoria, peso in categorias.items():
            agrupado[peso].append(categoria)

        #ordena por peso de forma descrente
        grupos =  dict(sorted(agrupado.items())) 
        print(grupos)
        
        #definindo os pesos de questoes a partir do tamanho do dicio - max 20 questoes
        pesos = {i: v for i,v in enumerate(grupos.values(), start=1) }
       
        aux_pesos =dict(sorted(pesos.items(), reverse=True)) #ordem decrescente
        
        perguntas = []
        
        
        MAX_PERGUNTAS = 20
        MIN_PERGUNTAS = 15

        aux = dados[0] if dados else None
        
        while len(perguntas) < MAX_PERGUNTAS:
            perguntas_antes_iteracao = len(perguntas)
            
            for num,cat_gp in  aux_pesos.items():
            #print(num, cat_gp)
                if len(perguntas) >= MAX_PERGUNTAS: #limite de 20 perguntas por usuario
                    break
                
                # Filtra os dados da categoria desejada
                for cat in cat_gp:
                    qtd_per_categ = 0
                    #print(num, cat)
                    #pega os menores valores de cont em cada categ
                    cont_categ = [int(e.get_cont()) for e in dados if e.get_categ() == cat]
                    if cont_categ:
                        min_valid = min(cont_categ)
                    else:
                        continue
                    aux  = None
                    for elem in dados:
                        if len(perguntas) >= MAX_PERGUNTAS or qtd_per_categ >= num: #limite de 20 perguntas por usuario
                            break
                        
                        if elem.get_categ() != cat:
                            continue

                        #pega os contadores 
                        cont_elem = int(elem.get_cont()) #atual
                        cont_aux = int(aux.get_cont()) if aux and aux.get_categ() == cat else None #anterior
                        
                        if cont_aux is None:
                            aux  = elem
                            continue
                        
                        #primeira verificação de contadores
                        #comparação de contador vale apenas para mesmas categorias
                        if  cont_aux == 0 : #amterior ainda nao foi verificado
                            aux.set_cont(cont_aux +1) #incrementa o contador atual
                            perguntas.append(aux) #adiciona no vetor
                            qtd_per_categ += 1 #atualiza o contador de perguntas
                                    

                        elif cont_elem < cont_aux: #se o anterior for maior que o anterior
                            elem.set_cont(cont_elem+1) #seto o contador atual em +1
                            perguntas.append(elem) #adicionoo atual no vetor de perguntas
                            qtd_per_categ += 1 #incremento no qtd de perguntas
                            aux = elem

                        elif cont_aux < cont_elem: #se o anterior for maior que o atual
                            aux.set_cont(cont_aux+1) #seto o contador atual em +1
                            perguntas.append(aux) #adicionoo atual no vetor de perguntas
                            qtd_per_categ += 1 #incremento no qtd de perguntas
                        
                        elif cont_elem == cont_aux : #se forem iguias, a operação acontece sob o anterior
                            #print(elem.resumo(), cont_elem, cont_aux,"Menor valor:", min_valid)
                            if cont_elem > min_valid: #se o menor que o menor_valid visto, então incrementa
                                aux = elem
                                continue
                                
                            else:
                                elem.set_cont(cont_elem+1)
                                perguntas.append(elem)
                                qtd_per_categ += 1
                                #aux  = elem #atauliza o comparador -> anterior recebe atual
                    
            if len(perguntas) >= MAX_PERGUNTAS:
                break
            if len(perguntas) >= MIN_PERGUNTAS and len(perguntas) == perguntas_antes_iteracao:
                break
        #realizando alguns tratamentos
        '''
        copia_perg = [x.perg_format() for x in perguntas]
        tab_avisos = defaultdict(list)
        
        for x in copia_perg:
            
            for chave, valor in x.items():
                
                if chave=='Eng':
                    for elem in valor:
                    
                        if '{{GEN1}}' in elem:
                            aviso = 'A sigla {GEN(num)} indica que a marcação de gênero do sujeito é importante pro contexto da setença'
                            tab_avisos['aviso' ].append(aviso)
                            #print('aviso:',aviso)
                            break
                
                        else:
                            tab_avisos['aviso' ].append('0')
                            #print('NAO TEM OCC1 ou GEN1')
                            break

        print("\nDados:", perguntas)
       
        
        self.templates_select = perguntas
        self.tab_avisosTemplate = tab_avisos
        return tab_avisos, perguntas

    
                            
    def recupera_dados(self):
        return {
            'token_pk': str(self.id),
            'form':self.forms,
            'categorias': self.categorias,
            'total_pesos': self.total_pesos,
            
        }

    
    @classmethod
    def transfere_dados_sessao(cls, dados):
        dados_transfer =  cls(
            id=dados['token_pk'],
            resp_form= dados['form']
        )

        dados_transfer.categorias = dados["categorias"]
        dados_transfer.total_pesos = dados["total_pesos"]

        return dados_transfer