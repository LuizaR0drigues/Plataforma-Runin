from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

import uuid
# Create your models here.
class perfil_bbq(models.Model):
    
    #gera um token baseado em numero aleatorios com 32 caracteres
    token_pk = models.UUIDField(primary_key=True,default=uuid.uuid4, unique=True, editable=False)
    
    idade = models.FloatField(default=0.0)
    genero = models.FloatField(default=0.0)
    raca = models.FloatField(default=0.0)
    pcd = models.FloatField(default=0.0)
    raca_gen = models.FloatField(default=0.0)
    ses_raca = models.FloatField(default=0.0)
    ses = models.FloatField(default=0.0)
    religiao = models.FloatField(default=0.0)
    s_o = models.FloatField(default=0.0)
    ap_fis = models.FloatField(default=0.0)
    nascio = models.FloatField(default=0.0)

    total_pesos = models.IntegerField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token_pk)

class opiniao_perfil(models.Model):
    #relaciona a opniao com um perfil do usuario e caso este venha a ser deletado, suas respostas tbm serao
    id_perfil = models.ForeignKey(perfil_bbq, on_delete=models.CASCADE, related_name="respostas")

    #campo que relaciona a resposta de acordo com o codigo do csv e o usuario
    id_questao = models.CharField(blank=False,max_length=8, db_index=True)
    y_n_valid = models.BooleanField() #define se é ou nao valido
    y_n_trad = models.BooleanField()

    #campo apara as respostas/sugestoes
    resposta = models.TextField()

    #data de submissao
    data_resp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Opiniao por perfil"

        #uma usuer so pode responder uma vez cada setença
        unique_together = ('id_perfil', 'id_questao')

        indexes = [
            models.Index(fields=['data_resp'])
        ]
    
    def __str__(self):
        return f'{self.id_perfil.token_pk} - Setença {self.id_questao}'

class Sentencas_sugeridas(models.Model):
   
    #relaciona a opniao com um perfil do usuario e caso este venha a ser deletado, suas respostas tbm serao
    id_perfil = models.ForeignKey(perfil_bbq, on_delete=models.CASCADE, related_name="sugestoes")
    
    #colunas
    categoria = models.CharField(max_length=50)
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

    

    def __str__(self):
        return f'{self.id_perfil.token_pk} - Setença {self.id}'


class ContadorPergunta(models.Model):
    q_id = models.CharField(max_length=8, unique=True)
    contador = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.q_id}: {self.contador}'

    @receiver(post_save, sender=opiniao_perfil)
    def incrementa_contador(sender, instance, created, **kwargs):
        #Sobe o contador só quando uma avaliação nova é salva (não em edições).
        if not created:
            return
        contador, _ = ContadorPergunta.objects.get_or_create(q_id=instance.id_questao)
        # incremento feito no banco: seguro com várias requisições ao mesmo tempo
        ContadorPergunta.objects.filter(pk=contador.pk).update(contador=F('contador') + 1)
