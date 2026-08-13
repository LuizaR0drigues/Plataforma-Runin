from django.db import models
import uuid
# Create your models here.
class perfil_bbq(models.Model):
    
    #gera um token baseado em numero aleatorios com 32 caracteres
    token_pk = models.UUIDField(primary_key=True,default=uuid.uuid4, unique=True, editable=False)
    age = models.FloatField()
    gender = models.FloatField()
    raca = models.FloatField()
    pcd = models.FloatField()
    raca_gen = models.FloatField()
    raca_ses = models.FloatField()
    s_o = models.FloatField()
    ap_fis = models.FloatField()
    nascio = models.FloatField()
    total_pesos = models.IntegerField()
    data = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.token_pk)

class opiniao_perfil(models.Model):
    #relaciona a opniao com um perfil do usuario e caso este venha a ser deletado, suas respostas tbm serao
    id_perfil = models.ForeignKey(perfil_bbq, on_delete=models.CASCADE, related_name="respostas")

    #campo que relaciona a resposta de acordo com o codigo do csv e o usuario
    id_questao = models.CharField(blank=False,max_length=8, db_index=True)
    y_n_valid = models.CharField(blank=False) #define se é ou nao valido
    #campo apara as respostas/sugestoes
    resposta = models.TextField()

    #data de submissao
    data_resp = models.DateTimeField(auto_now_add=True)

    class Meta:
        
        verbose_name = "Opiniao por perfil"

        #uma usuer so pode responder uma vez cada setença
        unique_together = ('id_perfil', 'id_questao')

        indexes = [
            models.Index(fields=['id_perfil']),
            models.Index(fields=['id_perfil', 'id_questao']),
            models.Index(fields=['data_resp']),
        ]
    
    def __str__(self):
        return f'{self.id_perfil.token_pk} - Setença {self.id_questao}'

class Sentencas_sugeridas(models.Model):
   
    #relaciona a opniao com um perfil do usuario e caso este venha a ser deletado, suas respostas tbm serao
    id_perfil = models.ForeignKey(perfil_bbq, on_delete=models.CASCADE, related_name="sugestoes")
    
    #colunas
    categoria = models.CharField()
    Amb_ctxt = models.CharField()
    Infor_ctxt = models.CharField()
    nomes = models.CharField()
    div_lexical = models.CharField()
    grupos = models.CharField()
    q_neg = models.CharField()
    q_n_neg = models.CharField()
    a_neg = models.CharField()
    a_n_neg = models.CharField()
    relev = models.CharField()
    
    data = models.DateTimeField(auto_now_add=True)

    #data de submissao
    data_resp = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):
        return f'{self.id_perfil.token_pk} - Setença {self.id}'