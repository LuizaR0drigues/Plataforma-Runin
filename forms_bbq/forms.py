from django import forms
from .models import perfil_bbq
from django.utils.safestring import mark_safe
import uuid

class perfil_bbq(forms.Form):
    
    #Idade
    AGE_CHOICES = [
        ('menos_18', 'Menos de 18 anos'),
        ('entre_18_24', 'Entre 18 a 24 anos'),
        ('entre_25_30', 'Entre 25 a 30 anos'),
        ('entre_31_40', 'Entre 31 a 40 anos'),
        ('entre_41_50', 'Entre 41 a 50 anos'),
        ('entre_51_60', 'Entre 51 a 60 anos'),
        ('mais_61', 'Mais de 61 anos'),
    ]

    #Genero
    GENDER_CHOICES = [
        ('h', 'Homem'),
        ('m', 'Mulher'),
        ('nb', 'Não-Binário'),
        ('none', 'Prefiro não dizer'),
        ('other', 'Outro')
    ]

    #identidade de genero
    IGENDER_CHOICES = [
        ('cis', 'Cisgênero'),
        ('trans', 'Transgênero'),
        ('nb', 'Identidade Não-Binária'),
        ('none', 'Prefiro não dizer'),
        ('other', 'Outro')
    ]

    #raça
    RACE_CHOICES =[
        ('branco', 'Branco'),
        ('preto', 'Preto'),
        ('pardo', 'Pardo'),
        ('indigena', 'Indígena'),
        ('amarelo', 'Amarelo'),
        ('other', 'Outro')
    ]
    
    #ses 1 e 2
    SES_CHOICES1 =[
        ('ses1', 'Até 1 salário mínimo'),
        ('ses2', 'Entre 1 e 2 salários minímos'),
        ('ses3', 'Entre 2 e 3 salários minímos'),
        ('ses4', 'Entre 3 e 4 salários minímos'),
        ('ses5', 'Entre 4 e 5 salários minímos'),
        ('ses6', 'Entre 5 e 6 salários minímos'),
        ('ses7', 'Entre 6 e 7 salários minímos'),
        ('ses8', 'Acima de 7 salários minímos')
    ]
    

    SES_CHOICES2 =[
        ('efi', 'Ensino Fundamental Incompleto'),
        ('efc', 'Ensino Fundamental Completo'),
        ('emi', 'Ensino Médio Incompleto'),
        ('emc', 'Ensino Médio Completo'),
        ('esi', 'Ensino Superior Incompleto'),
        ('esc', 'Ensino Superior Completo')
    ]
    

    
    #PCD
    DISAB_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não')
    ]
    
    #campos do modelo
    #gera um token baseado em numero aleatorios com 32 caracteres
    token_pk = forms.UUIDField(initial=uuid.uuid4,  widget=forms.HiddenInput())
    
    age = forms.ChoiceField(
        choices=AGE_CHOICES,
        widget=forms.RadioSelect,
        label="Selecione abaixo a sua faixa etária?",
        required=True
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect,
        label="Como você se identifica?",
        required=True
    )

    igender = forms.ChoiceField(
        choices=IGENDER_CHOICES,
        widget=forms.RadioSelect,
        label="Selecione abaixo a sua identidade de gênero:",
        required=True
    )

    race = forms.ChoiceField(required=True,
        widget=forms.RadioSelect,
        choices=RACE_CHOICES,
        label="Como você se autodeclara segundo a classificação do IBGE?",
        
    )

    ses1 = forms.ChoiceField(required=True,
        widget=forms.RadioSelect,
        choices=SES_CHOICES1,
        label="Selecione a sua renda familiar?"
    )

    ses2 = forms.ChoiceField(required=True,
        widget=forms.RadioSelect,
        choices=SES_CHOICES2,
        label="Qual é seu grau de escolaridade?"
    )

    pcd = forms.ChoiceField (required=True,
        widget=forms.RadioSelect,
        choices=DISAB_CHOICES,
        label='Você é um pessoa com deficiência?'
    )
     
    

class Validacao_perfil(forms.Form):
    VALID_CHOICES = [
            ('1', 'Sim'),
            ('0', 'Não')
    ]
    #id_perfil = forms.UUIDField(initial=uuid.uuid4, widget=forms.HiddenInput(), label="Identificacao do Usuario")
    #id_questao = forms.CharField()
    is_valid = forms.TypedChoiceField(required=True,
                                 widget=forms.RadioSelect,
                                 choices=VALID_CHOICES,
                                 coerce=lambda valor: valor == '1',
                                 label='Você concorda com as traduções acima?')
    adaptacao = forms.TypedChoiceField(required=True,
                                  widget=forms.RadioSelect,
                                  choices=VALID_CHOICES,
                                  coerce=lambda valor: valor == '1',
                                  label="Você considera que este template é adequado ao contexto brasileiro?")
    resposta = forms.CharField(label='Caso você considere necessário, sugira uma adaptação ou uma indicação para melhoria do template', required=False, widget=forms.Textarea(attrs={'class': 'commit'})) #opção em que o user pode adicionar sua opiniao
    
    
class Submissao_sentenças(forms.Form):
    CATEG_CHOICES = {
        ('age', 'Etarismo'),
        ('disability', 'Capacitismo'),
        ('race', 'Racismo'),
        ('nationality', 'Xenofobia'),
        ('physical', 'Aparência Física'),
        ('gender', 'Gênero/Identidade de Gênero'),
        ('ses','Status Socioecônomico/Elitismo'),
        ('religion','Intolerância Religiosa'),
        ('race_ses','Intersecção entre Racismo e Status Socioecônomico'),
        ('race_gender','Intersecção entre Racismo e Gênero/Identidade de Gênero'),
        ('sexual_orient','Orientação Sexual')
    }

    categoria = forms.ChoiceField(             
                                  choices=CATEG_CHOICES,
                                  label="Escolha uma categoria:", required=True)
    
    ctxt_ambiquo = forms.CharField(required=True,
                                   label="Contexto Ambíguo:" ,
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    ctxt_informativo = forms.CharField(required=True,
                                   label="Contexto Informativo",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    nomes = forms.CharField(
                                   label="Caso considere relevante, sugira nomes/nomenclaturas",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    diver_lexical = forms.CharField(
                                   label="Caso considere relevante, sugira palavras que podem se adpatar a situação sugerida:",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    categ_grupos = forms.CharField(required=True,
                                   label="Quais grupos são o foco desta sentença:",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    perg_ambiquo = forms.CharField(required=True,
                                   label="Pergunta Negativa",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    
    perg_informativa = forms.CharField(required=True,
                                   label="Pergunta Não-Negativa",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    resp_neg = forms.CharField(required=True,
                                   label="Resposta Negativa:",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    resp_n_neg = forms.CharField(required=True,
                                   label="Resposta Não Negativa:",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    relev_social = forms.CharField(required=True,
                                   label="Qual é a relevância social da sentença sugerida:",
                                   widget=forms.Textarea(attrs={'class': 'commit-sugestoes'}))
    