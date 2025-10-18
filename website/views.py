import datetime
from gc import get_objects
from django.contrib import messages
from re import purge, template
from statistics import pvariance
from xml.dom import NoModificationAllowedErr

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
# validação de usuarios

from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView

from django.http import HttpRequest, HttpResponseRedirect, Http404, HttpResponse
from django.db.models import Sum, Count, Max, Min

from django.contrib.auth import logout
from django.shortcuts import redirect

import datetime
from website.forms import TerceiroForm, EquipamentoForm, RefeicaoForm, FuncionarioForm, Grupo_RefeicaoForm, VisitanteForm, BuscaForm, EventoForm, ParametroForm
from website.models import Terceiro, Equipamento, Refeicao, Funcionario, Grupo_Refeicao, Inter_grup_ref, Visitante, Evento, Parametro, Empresa

# criação de logins

class MrLoginView(LoginView):
    template_name = 'website/login.html'
    success_url = reverse_lazy('home:home')
    redirect_authenticated_user = True

def logout_view(requisicao):
    logout(requisicao)
    return redirect('/login')

class MrDashboardView(TemplateView):
    template_name = '/website/home/home.html'


class HomeViewer(TemplateView):
    template_name = 'website/home/home.html'


status = ''

# Tela de Cadastro de Equipamentos
@login_required
def cria_equipamento(requisicao: HttpRequest):
    print(f'este é o GET = {requisicao.method == "GET"}')
    if requisicao.method == 'GET':
        print('entrou no get equipamento')
        form = EquipamentoForm()
        return render(requisicao, template_name='website/home/equipamento/equipamento.html', context={'form': form})

    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')

        form = EquipamentoForm(requisicao.POST)
        req = requisicao.POST
        for r in req.values():
            status = r
        print(f'este é o status =  {status}')

        if status == 'incluir':
            print('entrou no incluir')
            if form.is_valid():
                print('entrou no form.is_valid')
                equipamento = form.save(commit=False)
                equipamento.empresa = requisicao.user.profile.empresa
                equipamento.save()
                equipamento = Equipamento.objects.filter(empresa=requisicao.user.profile.empresa)
                empresa = requisicao.user.profile.empresa
                context = {'equipamento': equipamento, 'empresa': empresa}
                return render(requisicao, template_name='website/home/equipamento/salvo.html',context=context)


        if status == 'alterar':
            print('entrou no alterar')
            id_equip = requisicao.POST['id_equip']
            empresa_usuario = requisicao.user.profile.empresa

            try:
                # Busca registro de equipamento pertencente a mesma empresa
                equipamento = Equipamento.objects.get(id_equip=id_equip, empresa=empresa_usuario)
            except Equipamento.DoesNotExist:
                messages.error(requisicao, 'Equipamento não encontrado para esta empresa.')
                equipamento = Equipamento.objects.filter(empresa=empresa_usuario)
                return render(requisicao, template_name='website/home/equipamento/salvo.html', context={'equipamento': equipamento})

            form = EquipamentoForm(requisicao.POST, instance=equipamento)

            if form.is_valid():
                form.save()
            return render(requisicao, template_name='website/home/equipamento/salvo.html', context={'equipamento': equipamento})



            equipamento = Equipamento.objects.get(id_equip=id_equip, empresa=empresa)
            form = EquipamentoForm(requisicao.POST, instance=equipamento)
            if form.is_valid():
                form.save()
            equipamento = Equipamento.objects.filter(empresa=empresa)
            return render(requisicao, template_name='website/home/equipamento/salvo.html',
                              context={'equipamento': equipamento})


        if status == 'excluir':
            print('entrou no excluir ')
            print(f"este é a requisicao.POST = {requisicao.POST}")
            id_equip = requisicao.POST['id_equip']
            empresa_usuario = requisicao.user.profile.empresa

            if not id_equip:
                messages.error(requisicao, 'ID do Equipamento não fornecido.')
                equipamentos = Equipamento.objects.filter(empresa=empresa_usuario)
                return render(requisicao, template_name='website/home/equipamento/salvo.html', context={'equipamento': equipamentos})

            try:
                #Busca apenas o equipamento pertencente a empresa do usuario
                equipamento_obj = Equipamento.objects.get(id_equip=int(id_equip), empresa=empresa_usuario)
                print(f'Equipamento encontrado {equipamento_obj}')
                equipamento_obj.delete()
                messages.success(requisicao, "Equipamento excluido com sucesso!")
            except Equipamento.DoesNotExist:
                messages.error(requisicao, "Equipamento não encontrado para esta empresa.")

            #Aqui Equipamento volta a ser um queryset (iteravel)
            equipamentos = Equipamento.objects.filter(empresa=empresa_usuario)
            return render(requisicao, template_name='website/home/equipamento/salvo.html', context={'equipamento': equipamentos})

        if status == 'consultar':
            print('entrou no consultar')

            if requisicao.user.is_superuser:
                equipamento = Equipamento.objects.all()
            else:
                equipamento = Equipamento.objects.filter(empresa=requisicao.user.profile.empresa)
            return render(requisicao, template_name='website/home/equipamento/salvo.html', context={'equipamento': equipamento})

# Tela de cadastro de Refeições
@login_required
def cria_refeicao(requisicao: HttpRequest):
    #print(f"este é o GET = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print('entrou no get refeicao')
        form = RefeicaoForm()
        return render(requisicao, template_name='website/home/refeicao/refeicao.html', context={'form': form})
    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        #print(f'este é o botao incluir {requisicao.form.get()}')
        form = RefeicaoForm(requisicao.POST)
        ref = requisicao.POST
        print(f'este e o ref = {ref}')
        for r in ref.values():
            status = r
        print(f'este é o status =  {status}')


        if status == 'incluir':
            print('entrou no incluir')
            if form.is_valid():
                print('entrou no form.is_valid')
                refeicao = form.save(commit=False)
                refeicao.empresa = requisicao.user.profile.empresa
                refeicao.save()
                refeicao = Refeicao.objects.filter(empresa=requisicao.user.profile.empresa)
                empresa = requisicao.user.profile.empresa
                context = {'refeicao': refeicao, 'empresa': empresa}
                return render(requisicao, template_name='website/home/refeicao/salvo.html',
                              context=context)


        if status == 'alterar':
            print('entrou no alterar')
            print(requisicao.POST)
            id_ref = requisicao.POST['id_ref']
            empresa_usuario = requisicao.user.profile.empresa
            try:
                #Buca o registro da refeicao pertencente a mesma empresa
                refeicao = Refeicao.objects.get(id_ref=id_ref, empresa=empresa_usuario)
            except Refeicao.DoesNotExist:
                messages.error(requisicao, "Refeicao não encontrada para esta empresa.")
                refeicao = Refeicao.objects.filter(empresa=empresa_usuario)
                return render(requisicao, template_name='website/home/refeicao/salvo.html',
                              context={'refeicao': refeicao})
            form = RefeicaoForm(requisicao.POST, instance=refeicao)

            if form.is_valid():
                form.save()
            return render(requisicao, template_name='website/home/refeicao/salvo.html', context={'refeicao': refeicao})

        if status == 'excluir':
            print('entrou no excluir ')
            print(f"este é a requisicao.POST = {requisicao.POST}")
            id_ref = requisicao.POST.get('id_ref')
            empresa_usuario = requisicao.user.profile.empresa

            if not id_ref:
                messages.error(requisicao, "ID da refeicao não fornecido.")
                refeicoes = Refeicao.objects.filter(empresa=empresa_usuario)
                return render(requisicao, template_name='website/home/refeicao/salvo.html', context={'refeicao': refeicoes})


            try:
                #Busca apenas a refeição pertencente a epresa do usuario
                refeicao_obj = Refeicao.objects.get(id_ref=int(id_ref), empresa=empresa_usuario)
                print(f'Refeição encontrada: {refeicao_obj}')
                refeicao_obj.delete()
                messages.success(requisicao, "Refeição excluida com sucesso!")
            except Refeicao.DoesNotExist:
                messages.error(requisicao, "Refeição não encontrada para esta empresa.")

            # Aqui refeição volta a ser um queryset (iteravel)
            refeicoes = Refeicao.objects.filter(empresa=empresa_usuario)
            return render(requisicao, template_name='website/home/refeicao/salvo.html', context={'refeicao': refeicoes})


        if status == 'consultar':
            print('entrou no consultar')
            #empresa_usuario = requisicao.user.profile.empresa

            if requisicao.user.is_superuser:
                refeicao = Refeicao.objects.all()
            else:
                refeicao = Refeicao.objects.filter(empresa=requisicao.user.profile.empresa)

            return render(requisicao, template_name='website/home/refeicao/salvo.html',
                          context={'refeicao': refeicao})


# Cadastro de Funcionarios
@login_required
def cria_funcionario(requisicao: HttpRequest):

    user = requisicao.user
    print(f'este é o usr: {user}')
    if user.is_superuser:
        empresa_usuario = None
    else:
        empresa_usuario = getattr(user.profile, 'empresa', None)
    print(f'este é o empresa_usuario: {empresa_usuario}')

    if requisicao.method == 'GET':
        print('entrou no get funcionarios')
        if user.is_superuser:
            form =FuncionarioForm()
            funcionarios = Funcionario.objects.all()
            grupos = Grupo_Refeicao.objects.all()
        else:
            form = FuncionarioForm(requisicao.POST)
            funcionarios = Funcionario.objects.filter(empresa=empresa_usuario)
            grupos = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)

        print(f'funcionarios: {funcionarios}')
        print(f'grupos:{grupos}')

        context = {
            'form': form,
            'funcionarios': funcionarios,
            'grupos_refeicao': grupos,
            'empresa': empresa_usuario,
        }

        return render(requisicao,
                      template_name='website/home/funcionario/funcionario.html',
                      context=context)

    elif requisicao.method == 'POST':
        print('entrou no post')
        if user.is_superuser:
            form = FuncionarioForm(requisicao.POST)
            funcionarios = Funcionario.objects.all()
            grupos= Grupo_Refeicao.objects.all()
        else:
            form = FuncionarioForm(requisicao.POST)
            funcionarios = Funcionario.objects.filter(empresa=empresa_usuario)
            grupos = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)


        print(f'funcionarios: {funcionarios}')
        print(f'grupos:{grupos}')

        # identifica qual botão foi pressionado
        if 'incluir' in requisicao.POST:
            status = 'incluir'
        elif 'alterar' in requisicao.POST:
            status = 'alterar'
        elif 'excluir' in requisicao.POST:
            status = 'excluir'
        elif 'consultar' in requisicao.POST:
            status = 'consultar'
        else:
            status = None

        print(f'ação selecionada = {status}')

        if status == 'incluir':
            print('entrou no incluir')
            form = FuncionarioForm(requisicao.POST)

            if form.is_valid():
                print('form valido criando o funcionario')
                funcionario = form.save(commit=False)

                # associa campos automaticos
                funcionario.empresa = empresa_usuario # FK da empresa logada
                funcionario.grup_ref_id = requisicao.POST.get('grupos_refeicao') # id do grupo de refeicao
                funcionario.save()
                print(f'funcionario criado: {funcionario}')
                context = {'funcionario': [funcionario]}
                return render(requisicao,
                              template_name='website/home/funcionario/salvo.html',
                              context=context
                )
            else:
                print('form invalido, erros')
                print(f'este é o erro: {form.errors}')

                # Precisa retornar alguma resposta, mesmo com erro
                context = {'form': form, 'erros':form.errors}
                return render(
                    requisicao,
                    template_name='website/home/funcionario/erro.html',
                    context=context
                )

        if status == 'alterar':
            print('entrou no alterar')
            try:
                matricula = requisicao.POST['matricula']
                print(f'este é a matricula: {matricula}')

                if not matricula:
                    print('Nenhuma matricula recebida no POST')
                    return render(
                        requisicao,
                        template_name='website/home/funcionario/erro.html',
                        context={'mensagem': 'Matricula do funcionario não informado.'}
                    )

                funcionario = Funcionario.objects.get(matricula=matricula, empresa=empresa_usuario)
                print(f'este é o funcionario: {funcionario}')
                funcionario = FuncionarioForm(requisicao.POST, instance=funcionario)
                funcionario.empresa = empresa_usuario  # FK da empresa logada
                funcionario.grup_ref_id = requisicao.POST.get('grupos_refeicao')  # id do grupo de refeicao
                funcionario.save()
                funcionario = Funcionario.objects.all()

                context = {
                    'funcionario': funcionario,
                }
                return render(requisicao,
                              template_name='website/home/funcionario/salvo.html',
                              context=context
                )
            except Funcionario.DoesNotExist:
                print(f'Funcionario "{matricula}" não encontrada para a empresa {empresa_usuario}. ')
                return render(
                    requisicao,
                    template_name='website/home/funcionario/erro.html',
                    context={'mensagem': f'Funcionario da matricula "{matricula}" não encontrado.'}
                )
            except Exception as e:
                print(f'Erro inesperado na tentativa de alterar o funcionario.{str(e)}')
                return render(
                    requisicao,
                    template_name='website/home/funcionario/erro.html',
                    context={'mensagem': f'Ocorreu um erro na tentativa de alterar o funiconario {str(e)}'}
                )

        if status == 'excluir':
            print('entrou no excluir ')
            try:
                matricula = requisicao.POST.get('matricula')

                if not matricula:
                    print('Nenhuma matricula foi recebida no POST.')
                    return render(
                        requisicao,
                        template_name='website/home/funcionario/erro.html',
                        context={'mensagem': 'Matricula do funcionario não informado.'}
                    )
                funcionario = Funcionario.objects.get(matricula=matricula, empresa=empresa_usuario)
                print(f'estes são os dados do funcionario: {funcionario}')

                #Deleta o Funcionario não precisa apagar o grupo vinculado na tabela de Grupos_refeicao
                funcionario.delete()
                funcionario = Funcionario.objects.filter(empresa=empresa_usuario)

                return render(
                    requisicao,
                    template_name='website/home/funcionario/salvo.html',
                    context={'funcionario': funcionario}
                )
            except Funcionario.DoesNotExist:
                print(f'Funcionario "{matricula}" não encontrado para a empresa {empresa_usuario}.')
                return render(
                    requisicao,
                    template_name='website/home/funcionario/erro.html',
                    context={'mensagem': f'Funcionario "{matricula}" não encontrado.'}
                )
            except Exception as e:
                print(f'Erro inesperado ao excluir o funcionario: {e}')
                return render(
                    requisicao,
                    template_name='website/home/funcionario/erro.html',
                    context={'mensagem': f'Ocorreu um erro ao excluir o funcionario {str(e)}'}
                )


        if status == 'consultar':
            print('entrou no consultar')
            user = requisicao.user
            if user.is_superuser:
                funcionario = Funcionario.objects.all()
            else:
                empresa_usuario = requisicao.user.profile.empresa
                funcionario = Funcionario.objects.filter(empresa=empresa_usuario)

            context = {
                'funcionario': funcionario,
                'empresa': empresa_usuario
            }
            return render(requisicao, template_name='website/home/funcionario/salvo.html',
                          context=context)


# cadastro de Visitante
@login_required
def cria_visitante(requisicao: HttpRequest):

    user = requisicao.user
    print(f'este é o user: {user}')
    if user.is_superuser:
        empresa_usuario = None
    else:
        empresa_usuario = getattr(user.profile, 'empresa', None)
    print(f'este é a empresa_usuario: {empresa_usuario}')

    if requisicao.method == 'GET':
        print('entrou no Get do visitantes')
        if user.is_superuser:
            form = VisitanteForm()
            visitante = Visitante.objects.all()
            completo = Funcionario.objects.all()
            grupo_refeicao = Grupo_Refeicao.objects.all()
            for f in completo.values():
                func = f['nome']
                print(f'nome do funcionario = {func}')
                func = func
                for g in grupo_refeicao.values():
                    id_grup_ref = g['id_grup_ref']
            print(f'codigo do grupo = {id_grup_ref}')
            grupo_ref = id_grup_ref

            context = {
                'form': form,
                'completo': completo,
                'grupo_refeicao': grupo_refeicao,
                'hoje': datetime.date.today().isoformat(),
                'func': func,
                'grupo_ref': grupo_ref
            }
            return render(requisicao, template_name='website/home/visitante/visitante.html', context=context)

        else:
            form = VisitanteForm(requisicao.POST)
            visitante = Visitante.objects.filter(empresa=empresa_usuario)
            completo = Funcionario.objects.filter(empresa=empresa_usuario)
            grupo_refeicao = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)
            print(f'visitante: {visitante}')
            print(f'completo: {completo}')
            print(f'grupo de refeicao: {grupo_refeicao}')
            '''
            for f in completo.values():
                func = f['nome']
                print(f'nome do funcionario = {func}')
                func = func
                for g in grupo_refeicao.values():
                    grup_ref = g['grup_ref']
            print(f'codigo do grupo = {grup_ref}')
            '''

            context = {
                'form': form,
                'completo': completo,
                'grupo_refeicao': grupo_refeicao,
                'hoje': datetime.date.today().isoformat(),

            }
            return render(
                requisicao,
                template_name='website/home/visitante/visitante.html',
                context=context
            )

    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        form = VisitanteForm(requisicao.POST)
        vis = requisicao.POST
        for v in vis.values():
            status = v
        print(f'este é o status = {status}')

        if status == 'incluir':
            print('entrou no incluir')
            matricula = requisicao.POST['matricula']
            nome = requisicao.POST['nome']
            documento = requisicao.POST['documento']
            credencial = requisicao.POST['credencial']
            data_inicio = requisicao.POST['data_inicio']
            hora_inicio = requisicao.POST['hora_inicio']
            data_fim = requisicao.POST['data_fim']
            hora_fim = requisicao.POST['hora_fim']
            func = requisicao.POST.get('func')
            grupo_ref = requisicao.POST.get('grup_ref')
            motivo = requisicao.POST.get('motivo')
            visita =  matricula, nome, documento, credencial, data_inicio, data_fim, hora_inicio, hora_fim,func, grupo_ref, motivo
            print(f'este é visita = {visita}')
            print("func recebido no POST:", requisicao.POST.get('func'))
            print("queryset disponível no form:", list(form.fields['func'].queryset.values_list('id', flat=True)))

            if form.is_valid():
                visitante = Visitante(**form.cleaned_data)
                print(f'este é o visitantes = {visitante}')
                visitante.save()
                visitante = Visitante.objects.all()
                context = {'visitante': visitante}
                return render(requisicao, template_name='website/home/visitante/salvo.html', context=context)
            else:
                print(form.errors)

        if status == 'alterar':
            print('entrou no alterar')
            matricula = requisicao.POST['matricula']
            nome = requisicao.POST['nome']
            documento = requisicao.POST['documento']
            credencial = requisicao.POST['credencial']
            data_inicio = '2024-05-31'
            hora_inicio = requisicao.POST['hora_inicio']
            data_fim = requisicao.POST['data_fim']
            hora_fim = requisicao.POST['hora_fim']
            func = requisicao.POST.get('func')
            grupo_ref = requisicao.POST.get('grup_ref')
            motivo = requisicao.POST.get('motivo')
            visita = matricula, nome, documento, credencial, data_inicio, data_fim, hora_inicio, hora_fim, func, grupo_ref, motivo
            print(f'este é visita = {visita}')
            matricula = requisicao.POST['matricula']
            visitante = Visitante.objects.get(matricula=matricula)
            visitante = VisitanteForm(requisicao.POST, instance=visitante)
            visitante.save()
            visitante = Visitante.objects.all()
            return render(requisicao, template_name='website/home/visitante/salvo.html', context={'visitante': visitante})

        if status == 'excluir':
            print('entrou no excluir')
            print(f'este é a requisicao.POST = {requisicao.POST}')
            matricula = requisicao.POST['matricula']
            matricula = int(matricula)
            print(f'este é o id = {matricula}')
            visitante = Visitante.objects.get(matricula=matricula)
            print(f'exemplo da apostila {visitante}')
            visitante.delete()
            visitante = Visitante.objects.all()
            return render(
                requisicao,
                template_name='website/home/visitante/salvo.html',
                context={'visitante': visitante}
            )


        if status == 'consultar':
            print('entrou no consultar')
            visitante = Visitante.objects.all()
            return render(requisicao, template_name='website/home/visitante/salvo.html', context={'visitante': visitante})

#Cadastro de Terceiro

@login_required
def cria_terceiro(requisicao: HttpRequest):
    if requisicao.method == 'GET':
        print('entrou no Get do terceiro')
        completo = Funcionario.objects.all()
        grupo_refeicao = Grupo_Refeicao.objects.all()
        for f in completo.values():
            func = f['nome']
        print(f'nome do funcionario = {func}')
        func = func
        for g in grupo_refeicao.values():
            id_grup_ref = g['id_grup_ref']
        print(f'codigo do grupo = {id_grup_ref}')
        grupo_ref = id_grup_ref

        form = TerceiroForm()
        context = {
            'form': form,
            'completo': completo,
            'grupo_refeicao': grupo_refeicao,
            'func': func,
            'grupo_ref': grupo_ref
        }
        return render(requisicao, template_name='website/home/terceiro/terceiro.html', context=context)
    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        form = TerceiroForm(requisicao.POST)
        ter = requisicao.POST
        for t in ter.values():
            status = t
        print(f'este é o status = {status}')

        if status == 'incluir':
            print('entrou no incluir')
            matricula = requisicao.POST['matricula']
            nome = requisicao.POST['nome']
            documento = requisicao.POST['documento']
            empresa = requisicao.POST['empresa']
            credencial = requisicao.POST['credencial']
            data_inicio = requisicao.POST['data_inicio']
            hora_inicio = requisicao.POST['hora_inicio']
            data_fim = requisicao.POST['data_fim']
            hora_fim = requisicao.POST['hora_fim']
            func = requisicao.POST.get('func')
            grupo_ref = requisicao.POST.get('grup_ref')
            terc =  matricula, nome, empresa, documento, credencial, data_inicio, data_fim, hora_inicio, hora_fim,func, grupo_ref
            print(f'este é terc = {terc}')
            print("func recebido no POST:", requisicao.POST.get('func'))
            print("queryset disponível no form:", list(form.fields['func'].queryset.values_list('id', flat=True)))

            if form.is_valid():
                terceiro = Terceiro(**form.cleaned_data)
                print(f'este é o terceiro = {terceiro}')
                terceiro.save()
                terceiro = Terceiro.objects.all()
                context = {'terceiro': terceiro}
                return render(requisicao, template_name='website/home/terceiro/salvo.html', context=context)
            else:
                print(form.errors)

        if status == 'alterar':
            print('entrou no alterar')
            matricula = requisicao.POST['matricula']
            nome = requisicao.POST['nome']
            empresa = requisicao.POST['empresa']
            documento = requisicao.POST['documento']
            credencial = requisicao.POST['credencial']
            data_inicio = '2024-05-31'
            hora_inicio = requisicao.POST['hora_inicio']
            data_fim = requisicao.POST['data_fim']
            hora_fim = requisicao.POST['hora_fim']
            func = requisicao.POST.get('func')
            grupo_ref = requisicao.POST.get('grup_ref')
            terc = matricula, nome, empresa, documento, credencial, data_inicio, data_fim, hora_inicio, hora_fim, func, grupo_ref
            print(f'este é terc = {terc}')
            matricula = requisicao.POST['matricula']
            terceiro = Terceiro.objects.get(matricula=matricula)
            terceiro = TerceiroForm(requisicao.POST, instance=terceiro)
            terceiro.save()
            terceiro = Terceiro.objects.all()
            return render(requisicao, template_name='website/home/terceiro/salvo.html', context={'terceiro': terceiro})

        if status == 'excluir':
            print('entrou no excluir')
            print(f'este é a requisicao.POST = {requisicao.POST}')
            matricula = requisicao.POST['matricula']
            matricula = int(matricula)
            print(f'este é o id = {matricula}')
            terceiro = Terceiro.objects.get(matricula=matricula)
            print(f'exemplo da apostila {terceiro}')
            terceiro.delete()
            terceiro = Terceiro.objects.all()
            return render(requisicao, template_name='website/home/terceiro/salvo.html', context={'terceiro': terceiro})

        if status == 'consultar':
            print('entrou no consultar')
            terceiro = Terceiro.objects.all()
            return render(requisicao, template_name='website/home/terceiro/salvo.html', context={'terceiro': terceiro})

# cadastro de Grupo de Refeicao
@login_required
def cria_grupo_refeicao(requisicao: HttpRequest):

    user = requisicao.user
    print(f'este é o user: {user}')
    if user.is_superuser:
        empresa_usuario = None
    else:
        empresa_usuario = getattr(user.profile, 'empresa', None)
    print(f'este é o empresa_usuario acabei de criar: {empresa_usuario}')

    print(f'esta é a empesa_usuario: {empresa_usuario}')
    if requisicao.method == 'GET':
        print('entrou no get grupo de refeição')
        if user.is_superuser:
            form = Grupo_RefeicaoForm()
            grupos = Grupo_Refeicao.objects.all()
            refeicoes = Refeicao.objects.all()
        else:
            form = Grupo_RefeicaoForm(requisicao.POST)
            grupos = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)
            refeicoes = Refeicao.objects.filter(empresa=empresa_usuario)

        context = {
            'form': form,
            'grupo_refeicao': grupos,
            'refeicoes': refeicoes,
            'empresa': empresa_usuario,
        }

        return render(requisicao,
                      template_name='website/home/grupo_refeicao/grupo_refeicao.html',
                      context=context
                      )

    elif requisicao.method == 'POST':
        print('entrou no post')
        if user.is_superuser:
            form = Grupo_RefeicaoForm()
            grupos = Grupo_Refeicao.objects.all()
            refeicoes = Refeicao.objects.all()
        else:
            form = Grupo_RefeicaoForm(requisicao.POST)
            grupos = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)
            refeicoes = Refeicao.objects.filter(empresa=empresa_usuario)

        #ifentifica qual botão foi pressionado

        if 'incluir' in requisicao.POST:
            status = 'incluir'
        elif 'alterar' in requisicao.POST:
            status = 'alterar'
        elif 'excluir' in requisicao.POST:
            status = 'excluir'
        elif 'consultar' in requisicao.POST:
            status = 'consultar'
        else:
            status = None

        print(f'ação selecionada = {status}')

        if status == 'incluir':
            nome = requisicao.POST.get('nome')
            list_refeicoes_ids = requisicao.POST.getlist("refeicoes")
            teste = requisicao.POST.getlist("refeicoes")
            print(f'nome do grupo {nome}')
            print(f'ids das refeicoes selecionadas: {list_refeicoes_ids}')
            print(f'este é o teste: {teste}')

            if form.is_valid():
                print('form valido criando o grupo de refeição...')
                grupo_refeicao = form.save(commit=False)
                grupo_refeicao.empresa = empresa_usuario
                grupo_refeicao.save()
                form.save_m2m()

                # salva as refeicoes selecionadas no ManyToMany (django ja cuida da tabela intermediaria)
                grupo_refeicao.refeicoes.set(Refeicao.objects.filter(id_ref__in=list_refeicoes_ids))

                #Associa as refeicoes selecionadas através da tabela intermediaria
                for refeicao in Refeicao.objects.filter(id_ref__in=list_refeicoes_ids):
                    Inter_grup_ref.objects.update_or_create(
                        grup_ref=grupo_refeicao,
                        ref=refeicao,
                        defaults={'empresa': empresa_usuario}
                    )

                    print(f'Refeicao {refeicao} associada ao grupo {grupo_refeicao}')
            else:
                print('form invalido, erros:')
                print(form.errors)

            #atualiza dados para exibir na tela
            grupos = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)
            refeicoes = Refeicao.objects.filter(empresa=empresa_usuario)

            context = {
                'grupo_refeicao': grupos,
                'refeicao': refeicoes,
                'empresa': empresa_usuario,
            }
            return render(
                requisicao,
                template_name='website/home/grupo_refeicao/salvocomp.html',
                context=context
            )

        if status == 'alterar':
            print('entrou no alterar')
            try:
                nome = requisicao.POST.get('nome')
                print(f'este é o nome: {nome}')

                if not nome:
                    print('Nenhum nome foi recebido no POST')
                    return render(
                        requisicao,
                        template_name='website/home/grupo_refeicao/erro.html',
                        context={'mensagem': 'Nome do grupo não informado.'}
                    )



                grupo = Grupo_Refeicao.objects.get(nome=nome, empresa=empresa_usuario)
                print(f'este é o grupo: {grupo}')

                grup_id = grupo.id_grup
                print(f'este é o grup_id: {grup_id}')



                list_refeicoes = (requisicao.POST.getlist('refeicoes'))
                print(f'este é o list_refeicoes = {list_refeicoes}')
                # alterar o grupo e os vinculos associados

                inter = Inter_grup_ref.objects.filter(grup_ref=grupo).delete()
                print(f'este é o inter = {inter}')

                # teste da empresa
                emp = empresa_usuario.id
                print(f'este é o codigo da empresa: {emp}')
                for i in list_refeicoes:
                    print(f'este é o id_grup_ref = {grupo.id_grup}')
                    print(f'este é o i = {i}')



                    inter = Inter_grup_ref(grup_ref=grupo, ref_id=i, empresa=Empresa.objects.get(id=emp))
                    print(f'este é o inter gravou no banco = {inter}')
                    inter.save()

                grupo_refeicao = Grupo_Refeicao.objects.get(id_grup=grup_id, empresa=Empresa.objects.get(id=emp)) # grup_ref_id=grup_id
                print(f'primeiro grupo_refeicao: {grupo_refeicao}')
                #grupo_refeicao = Grupo_RefeicaoForm(requisicao.POST, instance=grupo_refeicao)
                #print(f'segundo grupo_refeicao: {grupo_refeicao}')
                grupo_refeicao.save()
                grupo_refeicao = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)

                context = {
                    'grupo_refeicao': grupo_refeicao,

                }
                return render(
                    requisicao,
                    template_name='website/home/grupo_refeicao/salvocomp.html',
                    context=context
                )

            except Grupo_Refeicao.DoesNotExist:
                print(f'Grupo "{nome}" não encontrado para a empresa {empresa_usuario}.')
                return render(
                    requisicao,
                    template_name='website/home/grupo_refeicao/erro.html',
                    context={'mensagem': f'Grupo "{nome}" não encontrado.'}
                )

            except Exception as e:
                print(f'Erro inesperado ao excluir grupo: {e}')
                return render(
                    requisicao,
                    template_name='website/home/grupo_refeicao/erro.html',
                    context={'mensagem': f'Ocorreu um erro ao excluir o grupo {str(e)}'}
                )

        if status == 'excluir':
            print('entrou no excluir ')
            print(f"este é a requisicao.POST = {requisicao.POST.get('nome')}")
            try:
                nome = requisicao.POST.get('nome')
                print(f'este é o nome = {nome}')

                if not nome:
                    print('Nenhum nome foi recebido no POST.')
                    return render(
                        requisicao,
                        template_name='website/home/grupo_refeicao/erro.html',
                        context={'mensagem': 'Nome do grupo não informado.'}
                    )

                grupo = Grupo_Refeicao.objects.get(nome=nome, empresa=empresa_usuario)
                print(f'este é o grupo_refeicao: {grupo}')

                id_grup = grupo.id_grup
                print(f'exemplo da apostila: {id_grup}')

                #Deleta o grupo e os vinculos associados
                grupo.delete()
                Inter_grup_ref.objects.filter(grup_ref_id=id_grup).delete()

                grupo_refeicao = Grupo_Refeicao.objects.all()

                return render(
                   requisicao,
                   template_name='website/home/grupo_refeicao/salvocomp.html',
                   context={'grupo_refeicao': grupo_refeicao}
                )
            except Grupo_Refeicao.DoesNotExist:
                print(f'Grupo "{nome}" não encontrado para a empresa {empresa_usuario}.')
                return render(
                    requisicao,
                    template_name='website/home/grupo_refeicao/erro.html',
                    context={'mensagem': f'Grupo "{nome}" não encontrado.'}
                )
            except Exception as e:
                print(f'Erro inesperado ao excluir grupo: {e}')
                return render(
                    requisicao,
                    template_name='website/home/grupo_refeicao/erro.html',
                    context={'mensagem': f'Ocorreu um erro ao excluir o grupo {str(e)}'}
                )



        if status == 'consultar':
            print('entrou na consultar')
            user = requisicao.user
            if user.is_superuser:
                grupo_refeicao = Grupo_Refeicao.objects.all()

            else:
                print(f'este é a requisicao POST = {requisicao.POST}')
                empresa_usuario = requisicao.user.profile.empresa
                print(f'este é o empresa = {empresa_usuario}')
                grupo_refeicao = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)
                print(f'este é o grupo de refeicao = {grupo_refeicao}')

            context ={
               'grupo_refeicao': grupo_refeicao,
                'empresa': empresa_usuario,
            }
            return render(requisicao, template_name='website/home/grupo_refeicao/salvo.html',
                          context=context)


@login_required
def cria_busca(requisicao: HttpRequest):
    # print(f"este é o GET = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print('entrou no get busca')
        form = BuscaForm()
        return render(requisicao, template_name='website/home/busca/busca.html',
                      context={'form': form})

    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        # print(f'este é o botao incluir {requisicao.form.get()}')
        form = BuscaForm(requisicao.POST)
        print(form)


# Relatorios

# monitoramento
@login_required
def monitoramento(requisicao: HttpRequest):
    #print(f"este é o GET = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print('entrou no get monitoramento')
        form = EventoForm()
        import datetime
        data_atual = datetime.date.today()
        print(data_atual)
        evento = Evento.objects.filter(data=(data_atual))
        context = {
            'form': form,
            'evento': evento
        }
        return render(requisicao, template_name='website/home/relatorio/monitoramento/resultado.html', context=context)


# Relatorio de Refeições
@login_required
def relatorio_refeicoes(requisicao: HttpRequest):
    #print(f"este é o GET = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print('entrou no get relatorio de refeicoes')
        form = EventoForm()
        return render(requisicao, template_name='website/home/relatorio/refeicoes/refeicoes.html', context={'form': form})
    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        #print(f'este é o botao incluir {requisicao.form.get()}')
        form = EventoForm(requisicao.POST)
        req = requisicao.POST
        for r in req.values():
            status = r
        print(f'este é o status =  {status}')


        if status == 'consultar':
            print('entrou no consultar')
            print(f'este é o post {requisicao.POST}')
            data_inicial = requisicao.POST['data_inicio']
            print(f'data inicial {data_inicial}')
            data_final = requisicao.POST.get('data_final')
            print(f' data final {data_final}')
            id = Refeicao.objects.values_list('id_ref', flat=True)
            hora_i = Refeicao.objects.values_list('hora_inicio', flat=True)
            hora_f = Refeicao.objects.values_list('hora_fim', flat=True)
            print(f'dados de refeicao = {id, hora_i, hora_f}')
            tabela_total = Refeicao.objects.all()
            print(f'total = {tabela_total}')
            horas = []
            for tab in tabela_total:
                print('Este é o for do tab')
                id = tab.id_ref
                print(id)
                hi = tab.hora_inicio
                print(hi)
                hf = tab.hora_fim
                print(hf)
                horas += id, hi, hf
                tipo_ref = tab.nome
                valor = tab.valor
                print(f'estes são nomes e valores de refeicao = {tipo_ref}, {valor}')

            idr = horas[0]
            refrr = []
            refeicao_1 = Refeicao.objects.filter(id_ref=idr)
            for refr in refeicao_1:
                ref_nome_1 = refr.nome
                ref_valor_1 = str(refr.valor)
                refrr += ref_nome_1, ref_valor_1

            evento_cafe= Evento.objects.filter(data__range=(data_inicial, data_final)) \
                                    .filter(hora__range=(horas[1], horas[2])) \
                                    .order_by('data')

            idr = horas[3]
            refrr = []
            refeicao_3 = Refeicao.objects.filter(id_ref=idr)
            for refr in refeicao_3:
                ref_nome_3 = refr.nome
                ref_valor_3 = str(refr.valor)
                refrr += ref_nome_3, ref_valor_3

            evento_almoco = Evento.objects.filter(data__range=(data_inicial, data_final)) \
                                   .filter(hora__range=(horas[4], horas[5])) \
                                   .order_by('data')

            idr = horas[6]
            refrr = []
            refeicao_6 = Refeicao.objects.filter(id_ref=idr)
            for refr in refeicao_6:
                ref_nome_6 = refr.nome
                ref_valor_6 = str(refr.valor)
                refrr += ref_nome_6, ref_valor_6

            evento_cafe_tarde = Evento.objects.filter(data__range=(data_inicial, data_final)) \
                                  .filter(hora__range=(horas[7], horas[8])) \
                                  .order_by('data')

            idr = horas[9]
            refrr = []
            refeicao_9 = Refeicao.objects.filter(id_ref=idr)
            for refr in refeicao_9:
                ref_nome_9 = refr.nome
                ref_valor_9 = str(refr.valor)
                refrr += ref_nome_9, ref_valor_9

            evento_jantar = Evento.objects.filter(data__range=(data_inicial, data_final)) \
                                  .filter(hora__range=(horas[10], horas[11])) \
                                  .order_by('data')

            idr = horas[12]
            refrr = []
            refeicao_12 = Refeicao.objects.filter(id_ref=idr)
            for refr in refeicao_12:
                ref_nome_12 = refr.nome
                ref_valor_12 = str(refr.valor)
                refrr += ref_nome_12, ref_valor_12


            evento_ceia = Evento.objects.filter(data__range=(data_inicial, data_final)) \
                                  .filter(hora__range=(horas[13], horas[14])) \
                                  .order_by('data')


            context = {

                
                'evento_almoco': evento_almoco,
                'evento_cafe': evento_cafe,
                'evento_cafe_tarde': evento_cafe_tarde,
                'evento_jantar': evento_jantar,
                'evento_ceia': evento_ceia,
                'ref_nome_1': ref_nome_1,
                'ref_valor_1': ref_valor_1,
                'ref_nome_3': ref_nome_3,
                'ref_valor_3': ref_valor_3,
                'ref_nome_6': ref_nome_6,
                'ref_valor_6': ref_valor_6,
                'ref_nome_9': ref_nome_9,
                'ref_valor_9': ref_valor_9,
                'ref_nome_12': ref_nome_12,
                'ref_valor_12': ref_valor_12
            }
            return render(requisicao, template_name='website/home/relatorio/refeicoes/resultado.html',
                      context=context)

# Relatorio refeições totalizado por funcionario
@login_required
def tot_func(requisicao: HttpRequest):
    #print(f"este é o GET = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print('entrou no get relatorio de tot_func')
        form = EventoForm()
        query = requisicao.GET.get('func')
        print(f'nome = {query}')

        print(f'este é o func = {query}')
        if query:
            print('entrou no if da query')
            func = Funcionario.objects.filter(nome__istartswhith=query)
        else:
            print('entrou no else do get')
            func = Funcionario.objects.all()
        completo = Funcionario.objects.all()

        context = {
            'func': func,
            'form': form,
            'completo': completo
        }
        return render(requisicao, template_name='website/home/relatorio/tot_func/tot_func.html', context=context)
    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        func = requisicao.POST.get('func')
        print(f'este é o func {func}')
        form = EventoForm(requisicao.POST)
        req = requisicao.POST
        for r in req.values():
            status = r
        print(f'este é o status =  {status}')


        if status == 'consultar':
            print('entrou no consultar')
            print(f'este é o post consulta {requisicao.POST}')
            data_inicial = requisicao.POST['data_inicio']
            print(f'data inicial {data_inicial}')
            data_final = requisicao.POST.get('data_final')
            print(f' data final {data_final}')
            funcionario = requisicao.POST.get('func')
            print(f'funcionario = {funcionario}')
            tabela_total = Refeicao.objects.all()
            print(f'tabela total = {tabela_total}')
            refeicoes = Refeicao.objects.aggregate(Count('id_ref'))
            tot_ref = refeicoes["id_ref__count"]

            eventos = []
            horas = []
            tot = []
            total_eventos = []
            n = 0

            while n != tot_ref:

                for tab in tabela_total:
                    print('Este é o for do tab')
                    id = tab.id_ref
                    print(id)
                    hi = tab.hora_inicio
                    print(hi)
                    hf = tab.hora_fim
                    print(hf)
                    horas += id, hi, hf
                    tipo_ref = tab.nome
                    valor = tab.valor
                    print(f'estes são nomes e valores de refeicao = {tipo_ref}, {valor}')

                    # pega todas as refeicoes
                    idr = id
                    refrr = []
                    refeicao_12 = Refeicao.objects.filter(id_ref=idr)
                    for refr in refeicao_12:
                        ref_nome_12 = refr.nome
                        ref_valor_12 = str(refr.valor)
                        ref_hi = refr.hora_inicio
                        ref_hf = refr.hora_fim
                        refrr += ref_nome_12, ref_valor_12, ref_hi, ref_hf
                        print(f'este é o refrr = {refrr}')
                        print(f'este é o horario = {ref_hi} {ref_hf}')
                        evento = Evento.objects.filter(data__range=(data_inicial, data_final)) \
                            .filter(nome__startswith=funcionario) \
                            .filter(hora__range=(ref_hi, ref_hf))


                        eventos += evento
                        som_eventos = eventos, tipo_ref, valor
                        print(f'este é o evento {evento}')
                        total = len(evento)
                        print(f'total de eventos = {total}')
                        tot_t = total * float(ref_valor_12)


                        total_eventos.append((funcionario, ref_nome_12, f'{str(total)}', ref_valor_12, f'{tot_t:.2f}'))


                    n += 1

            #total geral


            eve_0 = total_eventos[0]
            eve_1 = total_eventos[1]
            eve_2 = total_eventos[2]
            eve_3 = total_eventos[3]
            eve_4 = total_eventos[4]

            total_geral = float(eve_0[4]) + float(eve_1[4]) + float(eve_2[4]) + float(eve_3[4]) + float(eve_4[4])
            tot_geral = (f'{total_geral:.2f}')
            context = {
                'funcionario': funcionario,
                'eve_0': eve_0,
                'eve_1': eve_1,
                'eve_2': eve_2,
                'eve_3': eve_3,
                'eve_4': eve_4,
                'tot_geral': tot_geral


                }
            return render(requisicao, template_name='website/home/relatorio/tot_func/resultado.html',
                              context=context)


        return render(requisicao, template_name='website/home/relatorio/tot_func/semdados.html')


# Relatorios Refeições Totalizadas
@login_required
def tot_refeicao(requisicao: HttpRequest):
    print(f"este é o GET = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print('entrou no get relatorio de tot_refeicoes')
        return render(requisicao, template_name='website/home/relatorio/tot_refeicao/tot_refeicao.html')
    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        form = EventoForm(requisicao.POST)
        print(f'este é o form = {form}')
        req = requisicao.POST
        for r in req.values():
            status = r
        print(f'este é o status =  {status}')

        if status == 'consultar':
            print('entrou no consultar')
            print(f'este é o post consulta {requisicao.POST}')
            data_inicial = requisicao.POST['data_inicio']
            print(f'data inicial {data_inicial}')
            data_final = requisicao.POST.get('data_final')
            print(f' data final {data_final}')
            tabela_total = Refeicao.objects.all()
            print(f'tabela total = {tabela_total}')
            refeicoes = Refeicao.objects.aggregate(Count('id_ref'))
            tot_ref = refeicoes["id_ref__count"]

            n = 0
            eventos = []
            horas = []
            total_eventos = []

            while n != tot_ref:

                for tab in tabela_total:
                    print('Este é o for do tab')
                    id = tab.id_ref
                    print(id)
                    hi = tab.hora_inicio
                    print(hi)
                    hf = tab.hora_fim
                    print(hf)
                    horas += id, hi, hf
                    tipo_ref = tab.nome
                    valor = tab.valor
                    print(f'estes são nomes e valores de refeicao = {tipo_ref}, {valor}')

                    # pega todas as refeicoes
                    idr = id
                    refrr = []
                    refeicao_12 = Refeicao.objects.filter(id_ref=idr)
                    for refr in refeicao_12:
                        ref_nome_12 = refr.nome
                        ref_valor_12 = str(refr.valor)
                        ref_hi = refr.hora_inicio
                        ref_hf = refr.hora_fim
                        refrr += ref_nome_12, ref_valor_12, ref_hi, ref_hf
                        print(f'este é o refrr = {refrr}')
                        print(f'este é o horario = {ref_hi} {ref_hf}')
                        evento = Evento.objects.filter(data__range=(data_inicial, data_final)) \
                            .filter(hora__range=(ref_hi, ref_hf))

                        eventos += evento
                        som_eventos = eventos, tipo_ref, valor
                        print(f'este é o evento {evento}')
                        total = len(evento)
                        print(f'total de eventos = {total}')
                        tot_t = total * float(ref_valor_12)

                        total_eventos.append((ref_nome_12, f'{str(total)}', ref_valor_12, f'{tot_t:.2f}'))

                    n += 1

            print(f'este é o total eventos {total_eventos}')
            eve_0 = total_eventos[0]
            eve_1 = total_eventos[1]
            eve_2 = total_eventos[2]
            eve_3 = total_eventos[3]
            eve_4 = total_eventos[4]

            total_geral = float(eve_0[3]) + float(eve_1[3]) + float(eve_2[3]) + float(eve_3[3]) + float(eve_4[3])
            tot_geral = (f'{total_geral:.2f}')

            context= {
                'eve_0': eve_0,
                'eve_1': eve_1,
                'eve_2': eve_2,
                'eve_3': eve_3,
                'eve_4': eve_4,
                'tot_geral': tot_geral

            }

            return render(requisicao, template_name='website/home/relatorio/tot_refeicao/resultado.html',
                          context=context)

# Sobre
@login_required
def sobre(requisicao: HttpRequest):
    print(f"este é o GET = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print(f'entrou no if do get')
        return render(requisicao, template_name='website/home/ajuda/sobre/sobre.html')

# Configurações


# Modelo de Refeições
@login_required
def modelo(requisicao: HttpRequest):
    print(f"este é o Get do Modelo = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print(f'entrou no if do get')
        parametro = Parametro.objects.all()

        print(f'este é o parametro do get = {parametro}')
        context = {
            'parametro': parametro
        }
        return render(requisicao, template_name='website/home/configuracoes/modelos/salvo.html', context=context)

    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        form = ParametroForm(requisicao.POST)



        print(form)
        req = requisicao.POST
        for r in req.values():
            status = r
        print(f'este é o status =  {status}')


        if status == 'incluir':
            print('entrou no incluir')
            print(f'este é o post incluir {requisicao.POST}')

            if form.is_valid():
                print(f'entrou no form.is_valid()')

                padrao_usu = form.cleaned_data.get('mod_padrao_usu', False)
                padrao_visi = form.cleaned_data.get('mod_padrao_visi', False)
                credito_usu = form.cleaned_data.get('mod_credito_usu', False)
                credito_visi = form.cleaned_data.get('mod_credito_usu', False)
                id_param = requisicao.POST['id_param']
                nome = requisicao.POST['nome']

                print(f'estes sao os campos acima = {id_param, nome, padrao_usu, padrao_visi, credito_usu, credito_visi}')



                parametro = Parametro(id_param, id_param, nome, padrao_usu, padrao_visi, credito_usu, credito_visi)
                parametro.save()
                parametro = Parametro.objects.all()

                print(f'este é o parametro = {parametro}')
                context = {
                    'parametro': parametro

                }

                return render(requisicao, template_name='website/home/configuracoes/modelos/salvo.html', context=context)

        if status == 'alterar':
            print('Entrou no Alterar')



            parametro = Parametro.objects.all()

            for p in parametro:
                id = p.id_param

            print(f'consegui separar o id = {id}')
            print(f'este é o parametro = {parametro}')

            context = {
                'parametro': parametro
            }

            return render(requisicao, template_name='website/home/configuracoes/modelos/salvo.html', context=context)


        if status == 'consultar':
            print('Entrou no Alterar')


            parametro = Parametro.objects.all()

            print(f'este é o parametro = {parametro}')

            context = {
                'parametro': parametro
            }

            return render(requisicao, template_name='website/home/configuracoes/modelos/salvo.html', context=context)

@login_required
def cria_usuario(requisicao: HttpRequest):
    if requisicao.method == 'GET':
        print(f'entrou no if do get usuario')

        return render(requisicao, template_name='website/home/configuracoes/logins/logins.html')
    # Verifique se a requisição é POST
    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        form = ParametroForm(requisicao.POST)
        req = requisicao.POST
        for r in req.values():
            status = r
        print(f'este é o status =  {status}')

        if status == 'incluir':
            username = requisicao.POST['username']
            password = requisicao.POST['password']
            email = requisicao.POST.get('email', '')

            # Crie o usuário
            user = User.objects.create_user(username=username, password=password, email=email)

            # Adicione informações adicionais
            user.first_name = requisicao.POST.get('first_name', '')
            user.last_name = requisicao.POST.get('last_name', '')
            user.save()

            logins = User.objects.all()

            context = {
                'logins': logins
            }

            return render(requisicao, template_name='website/home/configuracoes/logins/salvo.html', context=context)

        if status == 'alterar':
            print('entrou no alterar')
            username = requisicao.POST['username']
            nova_senha = requisicao.POST['password']
            user = User.objects.get(username=username)
            user.set_password(nova_senha)
            user.save()


            logins = User.objects.all()

            context = {
                'logins': logins
            }

            return render(requisicao, template_name='website/home/configuracoes/logins/alterado.html', context=context)

        if status == 'excluir':
            print('entrou no excluir')
            username = requisicao.POST['username']
            user = User.objects.get(username=username)
            user.delete()


            logins = User.objects.all()
            context = {
                'logins': logins
            }

            return render(requisicao, template_name='website/home/configuracoes/logins/excluido.html', context=context)

        if status == 'consultar':
            print('entrou no consultar')

            logins = User.objects.all()
            context = {
                'logins': logins
            }

            return render(requisicao, template_name='website/home/configuracoes/logins/salvo.html', context=context)

# Relatorio de Funcionarios
@login_required
def relat_funcionarios(requisicao: HttpRequest):
    if requisicao.method == "GET":
        print('entrou no Get de Relat Funcionario')
        form = FuncionarioForm
        func = Funcionario.objects.all()
        print(f'este é o func = {func}')

        context = {
            'form': form,
            'func': func
        }
        return render(requisicao, template_name='website/home/relatorio/funcionarios/funcionarios.html', context=context)

@login_required
def relat_visitantes(requisicao: HttpRequest):
    if requisicao.method == "GET":
        print('entrou no Get de Relat Funcionario')
        form = VisitanteForm
        visi = Visitante.objects.all()

        context = {
            'form': form,
            'visi': visi
        }
        return render(requisicao, template_name='website/home/relatorio/visitantes/visitantes.html', context=context)

#Relatorio de Terceiros
@login_required
def relat_terceiros(requisicao: HttpRequest):
    if requisicao.method == "GET":
        print('entrou no Get de Relat Funcionario')
        form = TerceiroForm
        terc = Terceiro.objects.all()

        context = {
            'form': form,
            'terc': terc
        }
        return render(requisicao, template_name='website/home/relatorio/terceiros/terceiros.html', context=context)

