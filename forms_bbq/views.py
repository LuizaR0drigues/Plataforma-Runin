from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from django.conf import settings
from . import forms
from . import classes
from . import models as bd
from collections import defaultdict
import os
import csv
from itertools import cycle, islice
import uuid
import json
#Renderiza a home do formulario

def bbq_home(request):
    return render(request, 'home.html')

def bbq_fim(request):
    return render(request, 'fim.html')
def ex_validacao(request):
    return render(request, 'ex_validacao.html')
def ex_sugestao(request):
    return render(request, 'ex_sugestao.html')
def ex_cadastro(request):
    return render(request, 'ex_cadastro.html')
def bbq_sugerir(request):
    form_sugest  = forms.Submissao_sentenças(request.POST)
    return render(request, 'sugestoes.html', {'sent':form_sugest})

'''
def bbq_cadastro(request):
    
    Renderiza a pagina de cadastro do formulario e verifica se já houve resposta pelo usuário
    
    if 'cadastro_ok' in request.session:
        request.session.pop('token_pk', None)
        request.session.pop('perfil_user', None)
        request.session.pop('cadastro_ok', None)

    #obtem o identificador do usuário, se já existir
    id = request.session.get('token_pk')
    
    #gera um novo identificador
    if not id:
        id = str(uuid.uuid4())
        request.session['token_pk'] = id

    if request.method =='POST':
        form  = forms.perfil_bbq(request.POST, initial={'token_pk':id})
        
        if form.is_valid():
            perfil = form.cleaned_data #salva os dados, como um dict ,na memoria
            print("Uuid:" ,perfil)
            perfil_cpy = perfil.copy()
            if 'token_pk' in perfil_cpy:
                perfil_cpy['token_pk'] = str(perfil_cpy['token_pk']) #corrigindo o objt uuid
            #armazena o perfil e token na sessao
            request.session['perfil_user'] = perfil_cpy
            request.session['token_pk'] = id
            request.session['cadastro_ok'] = True
            return redirect('forms_bbq:iniciar_perguntas')
        else:
            
            print(form.errors)
    else:
        
        form = forms.perfil_bbq(initial={'token_pk': id})
        request.session['token_pk'] = id
    
    return render(request, 'cadastro.html', {'form': form})
'''
def render_termo(request):

    if request.method == "POST":
        if request.POST.get('termo') == "Sim":
                    return redirect('forms_bbq:cadastro') #redireciona o formulario de cadastro
        else:
            return render(request, 'fim.html') #encerra a sessão
    return render(request, 'termo.html')

def render_Cadastro(request):
     
    if 'cadastro_ok' in request.session:
        request.session.pop('token_pk', None)
        request.session.pop('perfil_user', None)
        request.session.pop('cadastro_ok', None)
    
    #recupera o id da sessao se ja exsitir ou cria um novo
    id_user = request.session.get('token_pk')
    
    user = classes.Avaliador(id=id_user)

    #senao houver um id
    if user.getId() is None:
        user.setId() #cria um id
        request.session['token_pk'] = user.getId() #salva na sessao


    if request.method == 'POST':

        formulario = forms.perfil_bbq(request.POST,
                                       initial={'token_pk':user.getId()})

        #se formulario for validado,
        if formulario.is_valid():
            respostas = formulario.cleaned_data #salva as respostas do user
            user.setRespostas(respostas)
            print(user.getRespostas())

            user.setId(respostas['token_pk'])
            #armazena o perfil e token na sessao 
            request.session['Avaliador'] = user.recupera_dados()
            request.session['cadastro_ok'] =  True

            salva_distribuicao_bd(request)
            
            return redirect('forms_bbq:iniciar_validacao')
        else:
            print(formulario.errors)
    else:
        
        formulario = forms.perfil_bbq(initial={'id': user.getId()})
        request.session['token_pk'] = user.getId()

    return render(request, 'cadastro.html', {'form': formulario})

def salva_distribuicao_bd(request):
    '''
    puxa o perfil do usuário, verifica a sua integridade e puxa um resumo das respostas,
    sua categorias prioritarias e salva resultados numéricos no banco de dados
    retorna as categorias 
    '''
    print("aqui aqui")
    user = None
    try:
        user = classes.Avaliador.transfere_dados_sessao(
            request.session['Avaliador'])
        token_uuid = user.getId()
        request.session['token_pk'] = token_uuid
        if not token_uuid:
            raise ValueError("Identificador nâo encontrado na sessâo")
    except token_uuid.DoesNotExist:
        raise Http404("Perfil não encontrado")
    except Exception as e:
        print("Erro ao buscar perfil:", e)
        return {}
    
    
    categorias =  user.getCategorias()
    #salvando os dados prob no bd
    cat_bd = categorias.copy()
   
    request.session['token_pk'] = user.getId()
    bd.perfil_bbq.objects.create(token_pk = user.getId(),
                                 age = cat_bd['idade'],
                                 raca = cat_bd['raca'],
                                 gender = cat_bd['genero'],
                                 pcd = cat_bd['pcd'],
                                 raca_gen = cat_bd['raca_gen'],
                                 raca_ses = cat_bd['ses_raca'],
                                 s_o = cat_bd['s_o'],
                                 nascio = cat_bd['nascio'],
                                 ap_fis = cat_bd['ap_fis'],
                                 total_pesos = user.getTotal())
    return categorias


def select_perguntas(dados, quant):
    '''
    Seleciona X perguntas por categorias e transfroma em uma lista circular 
    '''
    if not dados:
        raise ValueError("Lista de dados vazia")
    #print("Dados: ", len(dados), "Quant: ", quant)
    iterador  = cycle(dados)
    while True:
        prox = list(islice(iterador,quant )) # pega os n elemts
        yield prox

    
def adicicao_elem(atual, anterior):
    menor_valor = 0
    if atual.get_categ() != anterior.get_categ():
        return False
    cont_atual = atual.get_cont()
    cont_anterior = anterior.get_cont()

    if cont_anterior == 0:
        return True
    if cont_atual < cont_anterior:
        menor_valor = cont_atual
        return True
    if cont_anterior == cont_atual:
        if cont_atual > menor_valor:
            return False
        else:
            return  True
    

    
def cap_perguntas(request):
    #acessa as informações id e respostas ao forms
    #print( request.session['Avaliador'])
    user = classes.Avaliador.transfere_dados_sessao(request.session['Avaliador'])
    print(user.recupera_dados())
    print("ID ANTES:", user.getId())
    user.vinculaPerguntas() #encontras os templates e suas informações recomendados 

    print("ID DEPOIS:", user.getId())
    #salva os estados atuais
    request.session['Avaliador'] = user.recupera_dados()
    print("SALVO:", request.session['Avaliador'])
    request.session['aviso'] = user.getTabAvisos()

    request.session['perguntas'] = [p.perg_format() for p in user.getTemplates()]

    request.session['index_perg'] = 0

    return redirect('forms_bbq:mostrar_template') #avança pra imprimir esse conjunto
    

def mostrar_perguntas(request):
    user =  classes.Avaliador.transfere_dados_sessao(request.session['Avaliador'])
    id =  user.getId()
    
    perguntas  = request.session.get('perguntas', [])
    index = request.session.get('index_perg', 0)
    print("Mostrar Perguntas: ",len(perguntas), index)
    print("INDEX0:" ,index)


    if not perguntas:
        raise Http404("Nenhuma pergunta disponivel")
    
    if index >= len(perguntas):
        return render(request, "decisao.html")
    
    pergunta_atual = perguntas[index]
    request.session['id_questao'] = pergunta_atual['Id']
    #instacia o forms
    formulario = forms.Validacao_perfil()
    #Renderiza a pergunta atual no html
    #print(pergunta_atual)
    #print(pergunta_atual)
    aux =[(pergunta_atual.get('Eng', [])).get('Names', []), (pergunta_atual.get('Ptbr', [])).get('Nomes', []), (pergunta_atual.get('Eng', [])).get('Lexical_diversity', []), (pergunta_atual.get('Ptbr', [])).get('Diversidade_lexical', [])]
    info = {}
    print(aux)
    for elem in aux:
        #print(type(elem))
        if isinstance(elem, dict) or isinstance(elem, list):
            info.update(elem)
    #print(info)
    aviso = request.session.get('aviso') #dict com indice e conteudo do aviso
    if aviso['aviso'][index] != '0':
        return render(request, 'question.html', {'info': info, 'pergunta': pergunta_atual, 'forms':formulario, 'id':id, 'pagina': index+1, 'aviso': aviso['aviso'][index] })
    else:   
        return render(request, 'question.html', {'info': info, 'pergunta': pergunta_atual, 'forms':formulario, 'id':id, 'pagina': index+1})
    
def proxima_perguntas(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    formulario = forms.Validacao_perfil(request.POST)

    #Passa para a proxima pergunta quando aciona o botao 'Continuar'
    
    if formulario.is_valid():
        #limpa os dados do forms
        valid_y_n = formulario.cleaned_data['is_valid']
        opiniao = formulario.cleaned_data['resposta']

        #salvando os dados do forms na memoria
        request.session['valid_y_n'] = valid_y_n
        request.session['opiniao'] = opiniao

        request.session['index_perg'] = request.session.get('index_perg', 0) + 1

        cadastro_validacao(request)

        return redirect('forms_bbq:mostrar_template')

    return render(request, 'question.html', {'forms': formulario})

def cadastro_validacao(request):
    user =  classes.Avaliador.transfere_dados_sessao(request.session['Avaliador'])
    id_user =  user.getId()
    
    resp_valid = request.session.get('valid_y_n')
    opiniao = request.session.get('opiniao')
    
    id_questao = request.session.get('id_questao')
    print("ID DO USUÁRIO:", id_user)
    print("Perfis existentes:")
    for p in bd.perfil_bbq.objects.all():
        print(p.token_pk)
    perfil = get_object_or_404(bd.perfil_bbq, token_pk=id_user)

    bd.opiniao_perfil.objects.update_or_create(id_perfil = perfil,
                                     id_questao = id_questao,
                                     y_n_valid = resp_valid,
                                     resposta = opiniao)
    print("Id_user: ", id_user, "Id_quest: ", id_questao)

def decisao_sugest(request):
    user =  classes.Avaliador.transfere_dados_sessao(request.session['Avaliador'])
    id_user =  user.getId()
        
    if request.method == "POST":
        if request.POST.get('decisao') == "Sim":
            return sugestao_setencas(request) #renderiza o formulario
        else:
            return render(request, 'fim.html')
    return render(request, 'decisao.html')


def cadastro_setencas(request):
    user =  classes.Avaliador.transfere_dados_sessao(request.session['Avaliador'])
        
    perfil = get_object_or_404(bd.perfil_bbq, token_pk=user.getId())
    dados_sugestao =  request.session.get('sugestao')
    
    bd.Sentencas_sugeridas.objects.create( id_perfil = perfil,
                                            categoria = dados_sugestao['categoria'],
                                            Amb_ctxt = dados_sugestao['ctxt_ambiquo'],
                                            Infor_ctxt = dados_sugestao['ctxt_informativo'],
                                            nomes = dados_sugestao['nomes'],
                                            div_lexical = dados_sugestao['diver_lexical'],
                                            grupos = dados_sugestao['categ_grupos'],
                                            q_neg = dados_sugestao['perg_ambiquo'],
                                            q_n_neg = dados_sugestao['resp_neg'],
                                            a_n_neg = dados_sugestao['resp_n_neg'],
                                            relev = dados_sugestao['relev_social']
                                            )

def sugestao_setencas(request):
    
    user =  classes.Avaliador.transfere_dados_sessao(request.session['Avaliador'])
    id_user =  user.getId()

    if request.method == "POST":
        if "Nao" in request.POST: #encaminha pra tela final
            return render(request,"fim.html")
        else:
            #caso sim, continua a receber sentenças
            form_sugest = forms.Submissao_sentenças(request.POST)
            if form_sugest.is_valid():
                sugestao =  form_sugest.cleaned_data #salva os dados do forms
                print(sugestao)
                request.session['sugestao'] = sugestao
                #Salvando os dados na tabela
                cadastro_setencas(request)

                #renderiza o formulario até que o usuario queira finalizar
                form_sugest = forms.Submissao_sentenças()
                return render(request, 'sugestao.html', {"id": id_user, "sent": form_sugest} )
            else:
                form_sugest = forms.Submissao_sentenças()
                return render(request,'sugestao.html', {"id": id_user, "sent": form_sugest})
    else:
        form_sugest = forms.Submissao_sentenças()
    
    return render(request,'sugestao.html', {"id": id_user, "sent": form_sugest})