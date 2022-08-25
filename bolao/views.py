from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Partida, Apostas, Resultado, Rodada, Time, Profile


from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.urls import reverse_lazy
from django.views import generic

# Create your views here.


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def troca_senha(request):
    form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change.html', {
        'form': form,
    })


@login_required
def dashboard(request):
    jogos = {}
    try:
        rodada = Rodada.objects.filter(permitirApostas=True)
        for r in rodada:
            partidas = Partida.objects.filter(
                partidaRealizada=False, rodada=r.id)

            for partida in partidas:
                aposta = Apostas.objects.filter(
                    partida=partida.id, usuario=request.user.id)
                if aposta.count() > 0:
                    partida.usuario_apostou = True
                    partida.usuario_apostou_em = (
                        'Empate' if aposta[0].aposta_empate else aposta[0].aposta_vencedor.nome)

            jogos[r.id] = {'rodada': r.nome,
                           'partidas': list(partidas),
                           'mostrar': len(list(partidas))}

        historico = Resultado.objects.get_queryset()[0:5]
        users = User.objects.order_by('-profile__credito')[0:5]

    except Rodada.DoesNotExist:
        rodada = "Sem partidas para apostar por enquanto!"
    return render(request, 'bolao/dashboard.html', {'jogos': jogos, 'historicowid': historico, 'userswid': users})


@login_required
def historico(request):
    historico = Resultado.objects.get_queryset()
    return render(request, 'bolao/historico.html', {'historico': historico})


# @login_required
# def aposta(request, pk):
#     partida = get_object_or_404(Partida, pk=pk)
#     return render(request, 'bolao/aposta.html', {'partida': partida})


@permission_required('bolao.change_profile')
def perfil(request):
    if (request.method == 'GET'):
        users = User.objects.all()
        return render(request, 'bolao/perfil.html', {'users': users})
    else:
        # POST
        profile = Profile.objects.get(user=request.POST.get('user-id'))
        profile.credito = request.POST.get('credito')
        profile.pix = request.POST.get('pix')
        profile.save()

        users = User.objects.all()
        return render(request, 'bolao/perfil.html', {'users': users})


@permission_required('bolao.add_resultado')
def resultado(request):
    if (request.method == 'GET'):
        partidas = Partida.objects.filter(premiacaoDistribuida=False)
        return render(request, 'bolao/novo-resultado.html', {'partidas': partidas})
    else:
        # POST
        resultado = Resultado()
        resultado.partida = Partida.objects.get(
            id=request.POST.get('partida-id'))
        if request.POST.get('vencedor') == '0':
            resultado.empate = True
            resultado.vencedorPartida = Time.objects.get(nome='Empate')
        else:
            resultado.vencedorPartida = Time.objects.get(
                id=int(request.POST.get('vencedor')))

        resultado.save()

        partidas = Partida.objects.filter(premiacaoDistribuida=False)
        return render(request, 'bolao/novo-resultado.html', {'partidas': partidas})


@login_required
def ranking(request):
    users = User.objects.order_by('-profile__credito')
    return render(request, 'bolao/ranking.html', {'users': users})


@login_required
def apostar(request):
    data = {}
    if (request.method == 'POST'):
        # data['placar-casa'] = request.POST.get('placar-casa')
        # data['placar-visitante'] = request.POST.get('placar-visitante')
        data['time-casa'] = request.POST.get('time-casa')
        data['time-visitante'] = request.POST.get('time-visitante')
        data['partidaID'] = request.POST.get('partidaID')
        data['casa-id'] = request.POST.get('casa-id')
        data['visitante-id'] = request.POST.get('visitante-id')
        data['aposta'] = request.POST.get('aposta')
        # if (data['placar-casa'] > data['placar-visitante']):
        #     data['time-vencedor'] = data['casa-id']
        # elif (data['placar-visitante'] > data['placar-casa']):
        #     data['time-vencedor'] = data['visitante-id']
        # else:
        #     data['time-vencedor'] = "EMPATE"
        partida = Partida.objects.get(id=data['partidaID'])
        if (data['aposta'] != "0"):
            time = Time.objects.get(id=data['aposta'])
        else:
            time = None

        aposta = Apostas()
        aposta.usuario = request.user
        #aposta.aposta_placar_casa = 0
        #aposta.aposta_placar_vistante = 0
        aposta.aposta_vencedor = time
        aposta.aposta_empate = (True if data['aposta'] == "0" else False)
        aposta.partida = partida
        aposta.save()
        aposta.atualizar(request.user.id)
    return redirect('/')
