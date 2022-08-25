from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import signals

from .utils import get_country_flag_class
# Create your models here.


class Time(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    nome = models.CharField("nome", max_length=255)
    brasao = models.CharField("brasao", max_length=255)

    def __str__(self):
        return self.nome

    def get_flag(self):
        return get_country_flag_class(self.nome)


class Rodada(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    rodada = models.IntegerField(blank=False, null=True)
    nome = models.TextField(blank=True, null=True)
    permitirApostas = models.BooleanField(default=True)

    def __str__(self):
        return "Rodada #" + str(self.rodada) + (' - ' + self.nome if self.nome else '')

    def rodadaNumber(self):
        return str(self.rodada)

    def rodadaNome(self):
        return str(self.nome)


class Partida(models.Model):
    id = models.AutoField(primary_key=True)
    rodada = models.ForeignKey(Rodada, on_delete=models.CASCADE, null=True)
    timeCasa = models.ForeignKey(
        Time, on_delete=models.CASCADE, null=False, related_name='partida_timecasa')
    timeVisitante = models.ForeignKey(
        Time, on_delete=models.CASCADE, null=False, related_name='partida_timevisitante')
    title = models.CharField(max_length=200)
    dataPartida = models.DateTimeField(blank=True, null=True)
    premiacao = models.FloatField(default=0.00)
    partidaRealizada = models.BooleanField(default=False)
    premiacaoDistribuida = models.BooleanField(default=False)

    usuario_apostou = False
    usuario_apostou_em = None

    def publish(self):
        self.save()

    def __str__(self):
        return f"{self.title} - {self.timeCasa} x {self.timeVisitante}"

    def get_premiacao(self):
        return f"{self.premiacao:,.2f}"


class Resultado(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    vencedorPartida = models.ForeignKey(
        Time, on_delete=models.CASCADE, null=True)
    #placarCasa = models.IntegerField()
    #placarVisitante = models.IntegerField()
    empate = models.BooleanField(default=False)

    def publish(self):
        self.save()

    def __str__(self):
        return self.partida.timeCasa.nome + ' x ' + self.partida.timeVisitante.nome

    def get_class_casa(self):
        if self.empate:
            return "vitoria"
        else:
            return "vitoria" if self.partida.timeCasa.nome == self.vencedorPartida.nome else ""

    def get_class_visitante(self):
        if self.empate:
            return "vitoria"
        else:
            return "vitoria" if self.partida.timeVisitante.nome == self.vencedorPartida.nome else ""


class Apostas(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    aposta_data = models.DateTimeField(default=timezone.now)
    valor_aposta = models.FloatField(default=5.00)
    #aposta_placar_casa = models.IntegerField()
    #aposta_placar_vistante = models.IntegerField()
    aposta_vencedor = models.ForeignKey(
        Time, on_delete=models.CASCADE, null=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    aposta_empate = models.BooleanField(default=False)

    def atualizar(self, userId):
        profile = Profile.objects.get(user=userId)
        profile.credito = profile.credito - 5
        profile.qtde_apostas = profile.qtde_apostas + 1
        #profile.apostou = True
        profile.save()
        partida = self.partida
        partida.premiacao = partida.premiacao + 5
        partida.save()

    def __str__(self):
        profile = Profile.objects.get(id=self.usuario.id)
        # + " com placar: " + str(self.aposta_placar_casa) + " x " + str(self.aposta_placar_vistante)
        return f"{profile.user.username} Apostou em: {('Empate' if self.aposta_empate else str(self.aposta_vencedor.nome))} na partida {self.partida}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credito = models.FloatField(default=0.00)
    pix = models.TextField(null=True, default='')
    qtde_apostas = models.IntegerField(default=0)
    qtde_vitorias = models.IntegerField(default=0)

    def get_creditos(self):
        return f"{self.credito:,.2f}"

    def get_ordem(self):
        return self.objects.order_by('credito')

    def pode_apostar(self):
        return self.credito >= 5


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(signals.post_save, sender=Resultado)
def create_resultado(sender, instance, created, **kwargs):
    partida = Partida.objects.get(id=instance.partida.id)
    partida.partidaRealizada = True
    #rodada = Rodada.objects.get(id=partida.rodada.id)
    # apostas = Apostas.objects.filter(
    #     partida=instance.partida.id, aposta_placar_casa=instance.placarCasa, aposta_placar_vistante=instance.placarVisitante)
    # if (apostas.count() == 1):
    #     for aposta in apostas:
    #         usuario = User.objects.get(id=aposta.usuario.id)
    #         usuario.profile.credito = usuario.profile.credito + partida.premiacao
    #         #usuario.profile.apostou = False
    #         usuario.save()
    # elif (apostas.count() > 1):
    #     premio = partida.premiacao
    #     premio = premio / apostas.count()
    #     for aposta in apostas:
    #         usuario = User.objects.get(id=aposta.usuario.id)
    #         usuario.profile.credito = usuario.profile.credito + premio
    #         #usuario.profile.apostou = False
    #         usuario.save()
    # else:
    if instance.empate:
        apostas = Apostas.objects.filter(
            partida=instance.partida.id, aposta_empate=True)
    else:
        apostas = Apostas.objects.filter(
            partida=instance.partida.id, aposta_vencedor=instance.vencedorPartida)

    if (apostas.count() == 1):
        for aposta in apostas:
            usuario = User.objects.get(id=aposta.usuario.id)
            usuario.profile.credito = usuario.profile.credito + partida.premiacao
            usuario.profile.qtde_vitorias = usuario.profile.qtde_vitorias + 1
            usuario.save()
    elif (apostas.count() > 1):
        premio = partida.premiacao
        premio = premio / apostas.count()
        for aposta in apostas:
            usuario = User.objects.get(id=aposta.usuario.id)
            usuario.profile.credito = usuario.profile.credito + premio
            usuario.profile.qtde_vitorias = usuario.profile.qtde_vitorias + 1
            usuario.save()
    else:
        apostas = Apostas.objects.filter(partida=instance.partida.id)
        for aposta in apostas:
            usuario = User.objects.get(id=aposta.usuario.id)
            usuario.profile.credito = usuario.profile.credito + aposta.valor_aposta
            usuario.save()
    partida.premiacaoDistribuida = True
    partida.save()
    # rodada.permitirApostas = False
    # rodada.save()
    # usuarios = User.objects.all()
    # for usuario in usuarios:
    #     usuario.profile.apostou = False
    #     usuario.save()


@receiver(signals.post_save, sender=Apostas)
def create_aposta(sender, instance, created, **kwargs):
    profile = Profile.objects.get(user=instance.usuario_id)
    profile.credito = profile.credito - 5
    profile.qtde_apostas = profile.qtde_apostas + 1
    #profile.apostou = True
    profile.save()
    partida = Partida.objects.get(id=instance.partida_id)
    partida = partida
    partida.premiacao = partida.premiacao + 5
    partida.save()
