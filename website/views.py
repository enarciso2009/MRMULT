from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.views import LoginView
# validação de usuarios
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth import logout
from django.shortcuts import redirect
import datetime
from datetime import date, time, datetime
from website.forms import UsuarioForm, TerceiroForm, EquipamentoForm, RefeicaoForm, FuncionarioForm, Grupo_RefeicaoForm, VisitanteForm, BuscaForm, EventoForm, ParametroForm
from website.models import Terceiro, Equipamento, Refeicao, Funcionario, Grupo_Refeicao, Inter_grup_ref, Visitante, Evento, Parametro, Empresa, Profile, Usuario
from website.decorators import grupo_required



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


def acesso_negado(requisicao):
    return render(requisicao,
                  template_name='website/acesso_negado.html')

status = ''

# Tela de Cadastro de Equipamentos
#@login_required
@grupo_required(['Administrador', 'Operador'])
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
@grupo_required(['Administrador', 'Operador'])
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
@grupo_required(['Administrador', 'Operador'])
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
@grupo_required(['Administrador', 'Operador'])
def cria_visitante(requisicao: HttpRequest):
    import datetime
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
            grupos = Grupo_Refeicao.objects.all()
        else:
            form = VisitanteForm(requisicao.POST)
            visitante = Visitante.objects.filter(empresa=empresa_usuario)
            completo = Funcionario.objects.filter(empresa=empresa_usuario)
            grupos = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)

        context = {
            'form': form,
            'visitante': visitante,
            'completo': completo,
            'grupos_refeicao': grupos,
            'hoje': datetime.date.today().isoformat(),
            'empresa': empresa_usuario,

        }
        return render(
            requisicao,
            template_name='website/home/visitante/visitante.html',
            context=context
        )



    elif requisicao.method == 'POST':
        print('entrou no post')
        if user.is_superuser:
            form = VisitanteForm(requisicao.POST)
            visitante = Visitante.objects.all()
            completo = Funcionario.objects.all()
            grupos = Grupo_Refeicao.objects.all()
        else:
            form = VisitanteForm(requisicao.POST)
            visitante = Visitante.objects.filter(empresa=empresa_usuario)
            completo = Funcionario.objects.filter(empresa=empresa_usuario)
            grupos = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)


        # identifica qual o botao foi pressionado

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

        print(f'este é o status = {status}')

        if status == 'incluir':
            print('entrou no incluir')
            form = VisitanteForm(requisicao.POST)
            if form.is_valid():
                print('form valido criando o visitante')
                visitante = form.save(commit=False)

                # Associa campos automaticos
                visitante.empresa = empresa_usuario # FK da empresa logada
                visitante.grup_ref_id = requisicao.POST.get('grupos_refeicao') # id do grupo de refeicao
                visitante.save()
                print(f'visitante criado: {visitante}')
                context = {'visitante': [visitante]}
                return render(
                    requisicao,
                    template_name='website/home/visitante/salvo.html',
                    context=context
                )
            else:
                print('form invalido, erros')
                print(f'este é o erro: {form.errors}')
                # precisa retornar alguma resposta, mesmo que seja erro
                context = {'form': form, 'erros': form.errors}
                return render(
                    requisicao,
                    template_name='website/home/visitante/erro.html',
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
                        template_name='website/home/visitante/erro.html',
                        context={'mensagem': 'Matricula do visitante não informado.'}
                    )
                visitante = Visitante.objects.get(matricula=matricula, empresa=empresa_usuario)
                print(f'este é o visitante: {visitante}')
                visitante = VisitanteForm(requisicao.POST, instance=visitante)
                visitante.empresa = empresa_usuario # FK da empresa logada
                visitante.grup_ref_id = requisicao.POST.get('grupos_refeicao') # id do grupo de refeicao
                visitante.save()
                if user.is_superuser:
                    visitante = Visitante.objects.all()
                else:
                    visitante = Visitante.objects.filter(empresa=empresa_usuario)

                context = {
                    'visitante': visitante,
                }

                return render(
                    requisicao,
                    template_name='website/home/visitante/salvo.html',
                    context=context
                )
            except Visitante.DoesNotExist:
                print(f'Visitante "{matricula}" não encontrada para a empresa {empresa_usuario}.')
                return render(
                    requisicao,
                    template_name='website/home/visitante/erro.html',
                    context={'mensagem': f'Visitante da matricula "{matricula}" não encontrado.'}
                )
            except Exception as e:
                print(f'Erro inesperado na tentativa de alterar o visitante: {str(e)}')
                return render(
                    requisicao,
                    template_name='website/home/visitante/erro.html',
                    context={'mensagem': f'Ocorreu um erro na tentativa de alterar o visitante {str(e)}'}
                )

        if status == 'excluir':
            print('entrou no excluir')
            try:
                matricula = requisicao.POST.get('matricula')
                if not matricula:
                    print('Nenhuma matricula foi recebida no POST.')
                    return render(
                        requisicao,
                        template_name='website/home/visitante/erro.html',
                        context={'mensagem': 'Matricula do funcionario não infomado.'}
                    )
                visitante = Visitante.objects.get(matricula=matricula, empresa=empresa_usuario)
                print(f'estes são os dados do visitante {visitante}')

                # Deleta o visitante não precisa apagar o grupo de refeicao vinculado na tabela de Grupo_refeicao
                visitante.delete()
                if user.is_superuser:
                    visitante = Visitante.objects.all()
                else:
                    visitante = Visitante.objects.filter(empresa=empresa_usuario)
                return render(
                    requisicao,
                    template_name='website/home/visitante/salvo.html',
                    context={'visitante': visitante}
                )
            except Visitante.DoesNotExist:
                print(f'Visitante "{matricula}" não encontrado para a empresa {empresa_usuario}.')
                return render(
                    requisicao,
                    template_name='website/home/visitante/erro.html',
                    context={'mensagem': f'Visitante "{matricula}" não encontrada.'}
                )
            except Exception as e:
                print(f'Erro inesperado ao excluir o visitante: {e}')
                return render(
                    requisicao,
                    template_name='website/home/visitante/erro.html',
                    context={'mensagem': f'Ocorreu um erro ao excluir o visitante {str(e)}'}
                )

        if status == 'consultar':
            print('entrou no consultar')
            user = requisicao.user
            if user.is_superuser:
                visitante = Visitante.objects.all()
            else:
                visitante = Visitante.objects.filter(empresa=empresa_usuario)

            context= {
                'visitante': visitante,
                'empresa': empresa_usuario,
            }
            return render(
                requisicao,
                template_name='website/home/visitante/salvo.html',
                context=context
            )

#Cadastro de Terceiro

@grupo_required(['Administrador', 'Operador'])
def cria_terceiro(requisicao: HttpRequest):
    import datetime
    user = requisicao.user
    print(f'este é o user: {user}')
    if user.is_superuser:
        empresa_usuario = None
    else:
        empresa_usuario = getattr(user.profile, 'empresa', None)
    print(f'este é a empresa_usuario: {empresa_usuario}')

    if requisicao.method == 'GET':
        print('entrou no Get do terceiro')
        if user.is_superuser:
            form = TerceiroForm()
            terceiro = Terceiro.objects.all()
            completo = Funcionario.objects.all()
            grupos_refeicao = Grupo_Refeicao.objects.all()
        else:
            form = VisitanteForm(requisicao.POST)
            terceiro = Terceiro.objects.filter(empresa=empresa_usuario)
            completo = Funcionario.objects.filter(empresa=empresa_usuario)
            grupos_refeicao = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)

        context = {
            'form': form,
            'terceiro': terceiro,
            'completo': completo,
            'grupos_refeicao': grupos_refeicao,
            'hoje': datetime.date.today().isoformat(),
            'empresa': empresa_usuario,
        }
        return render(
            requisicao,
            template_name='website/home/terceiro/terceiro.html',
            context=context
        )

    elif requisicao.method == 'POST':
        print('entrou no post')
        if user.is_superuser:
            form = TerceiroForm(requisicao.POST)
            terceiro = Terceiro.objects.all()
            completo = Funcionario.objects.all()
            grupos_refeicao = Grupo_Refeicao.objects.all()
        else:
            form = TerceiroForm(requisicao.POST)
            terceiro = Terceiro.objects.filter(empresa=empresa_usuario)
            completo = Funcionario.objects.filter(empresa=empresa_usuario)
            grupos_refeicao = Grupo_Refeicao.objects.filter(empresa=empresa_usuario)

        # identifica qual o botao foi pressionado

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

        print(f'este é o status = {status}')

        if status == 'incluir':
            print('entrou no incluir')
            form = TerceiroForm(requisicao.POST)
            if form.is_valid():
                print('form valido criando o terceiro')
                terceiro = form.save(commit=False)

                # Associa campos automaticos

                terceiro.empresa = empresa_usuario # FK da empresa logada
                terceiro.grup_ref_id = requisicao.POST.get('grupos_refeicao') # id do grupo de refeicao
                terceiro.save()
                print(f'terceiro criado: {terceiro}')
                context = {'terceiro': [terceiro]}

                return render(
                    requisicao,
                    template_name='website/home/terceiro/salvo.html',
                    context=context
                )
            else:
                print("form invalido, errors")
                print(f'este é o erro {form.errors}')

                # Precisa retornar alguma resposta, mesmo que seja erro

                context= {'form': form, 'erros': form.errors}

                return render(
                    requisicao,
                    template_name='website/home/terceiro/erro.html',
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
                        template_name='website/home/terceiro/erro.html',
                        context={'mensagem': 'Matricula do terceiro não informado.'}
                    )
                terceiro = Terceiro.objects.get(matricula=matricula, empresa=empresa_usuario)
                terceiro = TerceiroForm(requisicao.POST, instance=terceiro)
                print(f'este é o terceiro: {terceiro}')
                terceiro.empresa = empresa_usuario #FK da empresa logada
                terceiro.grup_ref_id = requisicao.POST.get('grupos_refeicao') # id do grupo de refeicao
                terceiro.save()
                if user.is_superuser:
                    terceiro = Terceiro.objects.all()
                else:
                    terceiro = Terceiro.objects.filter(empresa=empresa_usuario)

                context = {
                    'terceiro': terceiro,
                }

                return render(
                    requisicao,
                    template_name='website/home/terceiro/salvo.html',
                    context=context
                )
            except Terceiro.DoesNotExist:
                print(f'Terceiro "{matricula}" não encontrado para a empresa {empresa_usuario}.')
                return render(
                    requisicao,
                    template_name='website/home/terceiro/erro.html',
                    context={'mensagem': f'Terceiro da matricula "{matricula}" não encontrado.'}
                )
            except Exception as e:
                print(f'Erro inesperado na tentativa de alterar o Terceiro: {str(e)}')
                return render(
                    requisicao,
                    template_name='website/home/terceiro/erro.html',
                    context={'mensagem': f'Ocorreu um erro na tentativa de alterar o terceiro {str(e)}'}
                )

        if status == 'excluir':
            print('entrou no excluir')
            try:
                matricula = requisicao.POST.get('matricula')
                if not matricula:
                    print('Nenhuma matricula foi recebida no POST')
                    return render(
                        requisicao,
                        template_name='website/home/terceiro/erro.html',
                        context={'mensagem': 'Matricula do terceiro não informado.'}
                    )
                terceiro = Terceiro.objects.get(matricula=matricula, empresa=empresa_usuario)
                print(f'estes são os dados do terceiro: {terceiro}')

                # Deleta o terceiro, não precisa apagar o grupo de refeicao vinculado na tabela de Grupo_refeicao
                terceiro.delete()
                if user.is_superuser:
                    terceiro = Terceiro.objects.all()
                else:
                    terceiro = Terceiro.objects.filter(empresa=empresa_usuario)
                return render(
                    requisicao,
                    template_name='website/home/terceiro/salvo.html',
                    context={'terceiro': terceiro}
                )
            except Terceiro.DoesNotExist:
                print(f'Terceiro "{matricula}" não encontrado para a empresa {empresa_usuario}.')
                return render(
                    requisicao,
                    template_name='website/home/terceiro/erro.html',
                    context={'mensagem': f'Terceiro {matricula} não encontrado.'}
                )
            except Exception as e:
                print(f'Erro inesperado ao excluir o terceiro: {e}')
                return render(
                    requisicao,
                    template_name='website/home/terceiro/erro.html',
                    context={'mensagem': f'Ocorreu um erro ao excluir o terceiro {str(e)}'}
                )

        if status == 'consultar':
            print('entrou no consultar')
            if user.is_superuser:
                terceiro = Terceiro.objects.all()
            else:
                terceiro = Terceiro.objects.filter(empresa=empresa_usuario)

            context = {
                'terceiro': terceiro,
                'empresa': empresa_usuario,
            }
            return render(
                requisicao,
                template_name='website/home/terceiro/salvo.html',
                context=context
            )

# cadastro de Grupo de Refeicao
@grupo_required(['Administrador', 'Operador'])
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


@grupo_required(['Administrador', 'Operador'])
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
        import datetime
        user = requisicao.user

        print('entrou no get monitoramento')
        if user.is_superuser:
            form = EventoForm()
            data_atual = datetime.date.today()
            print(data_atual)
            evento = Evento.objects.filter(data=(data_atual))
        else:
            empresa_usuario = getattr(user.profile, 'empresa', None)
            form = EventoForm()
            data_atual = datetime.date.today()
            evento = Evento.objects.filter(data=(data_atual), empresa=empresa_usuario)
        context = {
            'form': form,
            'evento': evento
        }
        return render(requisicao, template_name='website/home/relatorio/monitoramento/resultado.html', context=context)


#extrair horario
def extract_time(value):
    """
    Normaliza diferentes formatos de hora para um datetime.time ou retorno None.
    Aceita:
    - datetime.time -> retorna como está
    - datetime.datetime -> retorna .time()
    - str (ex: '08:00', '08:00:00') -> parseia
    - list/tuple/set -> pega o primeiro elemento e tenta novamente
    - None -> retorna None
    """
    if value is None:
        return None

    # já é time
    if isinstance(value, time):
        return value

    #datetime -> pega time()
    if isinstance(value, datetime):
        return value.time()

    # string: tenta parsear
    if isinstance(value, str):
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue
    # se não conseguiu parsear, retorna None
    return None

    # Coleções -> pega o primeiro elemento
    if isinstance(value, (list,tuple, set)):
        try:
            first = next(iter(value))
            return extract_time(first)
        except StopIteration:
            return None

    # Caso desconhecido
    return None


@grupo_required(['Administrador', 'Operador', 'Consulta'])
def relatorio_refeicoes(requisicao: HttpRequest):
    user = requisicao.user
    if user.is_superuser:
        empresa_usuario =None
    else:
        empresa_usuario = getattr(user.profile, 'empresa', None)
        print(f'Usuario logado: {user} Empresa: {empresa_usuario}')

    if requisicao.method == "GET":
        print('entrou no GET relatorio de refeicoes')
        form = EventoForm()
        context = {
            'form': form,
        }
        return render(
            requisicao,
            template_name='website/home/relatorio/refeicoes/refeicoes.html',
            context=context
        )
    elif requisicao.method == 'POST':
        print('entrou no POST relatorio de refeicoes')
        form = EventoForm(requisicao.POST)
        acao = requisicao.POST.get('consultar') or ''
        print(f'Ação identificada: {acao}')

        if acao == 'consultar':
           try:
                data_inicial = requisicao.POST.get('data_inicio')
                data_final = requisicao.POST.get('data_final')

                print(f'esta é a empresa do usuario: {empresa_usuario}')
                if not data_inicial or not data_final:
                    return render(
                        requisicao,
                        template_name='website/home/relatorio/refeicoes/erro.html',
                        context={'mensagem': 'Por favor, selecione o intervalo de datas'}
                    )
                print(f'Data inicial: {data_inicial} e Data final: {data_final}')

                #Busca todas as refeicoes da empresa
                if user.is_superuser:
                    refeicoes = Refeicao.objects.all().order_by('hora_inicio')
                else:
                    refeicoes = Refeicao.objects.filter(empresa=empresa_usuario).order_by('hora_inicio')
                if not refeicoes.exists():
                    return render(
                        requisicao,
                        template_name='website/home/relatorio/refeicoes/erro.html',
                        context={'mensagem': 'Nenhuma refeição configurada para esta empresa'}
                    )

                print(f'refeicoes encontradas: {refeicoes.count()}')
                # Busca o tipo de pessoa
                tipos_pessoa = requisicao.POST.getlist('tipo_pessoa')

                # Busca os eventos no intervalo de datas e da empresa
                if user.is_superuser:
                    eventos_qs = Evento.objects.filter(
                        data__range=[data_inicial, data_final]
                    ).order_by('data', 'hora')
                else:
                    eventos_qs = Evento.objects.filter(
                        empresa=empresa_usuario,
                        data__range=[data_inicial, data_final]
                    ).order_by('data', 'hora')

                if tipos_pessoa:
                    eventos_qs = eventos_qs.filter(tipo_pessoa__in=tipos_pessoa)
                if not eventos_qs.exists():
                    return render(
                        requisicao,
                        template_name='website/home/relatorio/refeicoes/erro.html',
                        context={'mensagem': 'Nenhum evento encontrado para o periodo selecionado.'}
                    )
                print(f'eventos_qs: {eventos_qs}')
                print(f'Total de eventos encontrados: {eventos_qs.count()}')

                # Para evitar multiplos hits no DB ao acessar .hora muitas vezes
                print('Para evitar multiplos hits no DB ao acessar .hora muitas vezes')
                # Materializamos a lista (pequeno custo de memoria, melhora comparações customizadas)
                print('Materializamos a lista (pequeno custo de memoria, melhora comparações customizadas)')
                eventos = list(eventos_qs)
                print('----------------testes -------------')
                eve = Evento.objects.filter(empresa=empresa_usuario)
                ref = Refeicao.objects.filter(empresa=empresa_usuario)
                eve_enc = []

                for r in ref:
                    for e in eventos:
                        print(f'comparando {r.hora_inicio} - {e.hora} - {r.hora_fim}')
                        if r.hora_inicio <= e.hora <= r.hora_fim:
                            print(f'querendo fazer as comparações: {r.hora_inicio} - {e.hora} - {r.hora_fim}')
                            eve_enc.append(e)
                print(f'este é o eve_enc: {eve_enc}')

                print(f'eventos: {eventos}')
                eventos_por_refeicao = []
                refeicoes_info ={}

                print('-------------looping -------------')

                #Percorre todas as refeicoes configuradas
                print('Percorre todas as refeicoes configuradas')

                for refeicao in refeicoes:
                   for e in eventos:
                       print(f'comparando {refeicao.hora_inicio} - {e.hora} - {refeicao.hora_fim}')
                       if refeicao.hora_inicio <= e.hora <= refeicao.hora_fim:
                           eventos_por_refeicao.append(e)
                print(f'este é o eventos encontrados: {eventos_por_refeicao}')
                eventos_por_refeicao = list({eventos.id: eventos for eventos in eventos_por_refeicao}.values())

                print('---RESULTADOS---')
                print(f'Refeicoes info: {refeicoes_info}')
                print(f'eventos encontrados: {eventos_por_refeicao}')
                print(f'Total eventos por refeicao: {len(eventos_por_refeicao)}')

                data_inicial_fmt = datetime.strptime(data_inicial, "%Y-%m-%d").date()
                data_final_fmt = datetime.strptime(data_final, "%Y-%m-%d").date()

                context = {

                    'refeicoes_info': refeicoes_info,
                    'eventos_por_refeicao': eventos_por_refeicao,
                    'data_inicial': data_inicial_fmt,
                    'data_final': data_final_fmt,
                    'ref_nome': refeicao.nome,
                    'ref_valor': refeicao.valor,

                }

                return render(
                    requisicao,
                    template_name='website/home/relatorio/refeicoes/resultado.html',
                    context=context
                )
           except Exception as e:
               print(f'Erro ao gerar relatorio: {e}')
               return render(
                   requisicao,
                   template_name='website/home/relatorio/refeicoes/erro.html',
                   context={'mensagem': f'Ocorreu um erro: {str(e)}'}
               )
        else:
            print('Ação diferente de "consultar"')
            return render(
                requisicao,
                template_name='website/home/relatorio/refeicoes/refeicoes.html',
                context={'mensagem': 'Ação diferente de consultar'}
            )


# Relatorio refeições totalizado por funcionario
@grupo_required(['Administrador', 'Operador', 'Consultar'])
def tot_func(requisicao: HttpRequest):
    user = requisicao.user
    if user.is_superuser:
        empresa_usuario = None
    else:
        empresa_usuario = getattr(user.profile, 'empresa', None)

    if requisicao.method == 'GET':
        print('entrou no get relatorio de tot_func')
        form = EventoForm()
        query = requisicao.GET.get('func')
        print(f'Nome pesquisado = {query}')

        if user.is_superuser:
            completo = Funcionario.objects.all()
        else:

            completo = Funcionario.objects.filter(empresa=empresa_usuario)

        if query:
            print('entrou no if da query')
            func = Funcionario.objects.filter(
                nome__istartswith=query,
                empresa=empresa_usuario
            )
        else:
            print('entrou no else do get')
            func = Funcionario.objects.filter(empresa=empresa_usuario)


        context = {
            'func': func,
            'form': form,
            'completo': completo,
        }
        return render(requisicao,
                      template_name='website/home/relatorio/tot_func/tot_func.html',
                      context=context
        )

    elif requisicao.method == 'POST':
        print('entrou no post')
        form = EventoForm(requisicao.POST)
        acao = requisicao.POST.get('acao') or requisicao.POST.get('status') or 'consultar'
        print(f'Ação: {acao}')

        if acao == 'consultar':
            print('entrou no consultar')
            data_inicial = requisicao.POST['data_inicio']
            data_final = requisicao.POST.get('data_final')
            funcionario_nome = requisicao.POST.get('func')

            print(f'periodo: {data_inicial} a {data_final}')
            print(f'Funcionario selecionado: {funcionario_nome}')

            # Se escolher "Todos", traz todos os funcionarios da empresa
            if funcionario_nome == "Todos":
                if user.is_superuser:
                    funcionarios = Funcionario.objects.all()
                else:
                    funcionarios = Funcionario.objects.filter(empresa=empresa_usuario)
            else:
                if user.is_superuser:
                    funcionarios = Funcionario.objects.filter(nome__startswith=funcionario_nome)
                else:
                    funcionarios = Funcionario.objects.filter(
                    nome__startswith=funcionario_nome,
                    empresa=empresa_usuario
                )
            if not funcionarios.exists():
                print('Nenhum funcionario encontrado.')
                return render(
                    requisicao,
                    template_name='website/home/relatorio/tot_func/semdados.html'
                )

            # Superuser vê tudo, usuario comum só da empresa dele
            if user.is_superuser:
                eventos_base = Evento.objects.all()
                refeicoes = Refeicao.objects.all()
            else:
                eventos_base = Evento.objects.filter(empresa=empresa_usuario)
                refeicoes = Refeicao.objects.filter(empresa=empresa_usuario)

            # Dicionario de totais
            totais_funcionarios = defaultdict(list)
            total_geral = 0.0

            #total_eventos = defaultdict(lambda: {"total": 0, "valor": 0.0})

            for func in funcionarios:
                subtotal_func = 0.0
                # Pega só as refeicoes da empresa do funcionario
                if user.is_superuser:
                    refeicoes_func = Refeicao.objects.filter(empresa=func.empresa)
                else:
                    refeicoes_func = refeicoes # já filtradas no codigo mais acima

                for ref in refeicoes_func:
                    eventos_filtrados = eventos_base.filter(
                        data__range=(data_inicial, data_final),
                        nome__startswith=func.nome,
                        hora__range=(ref.hora_inicio, ref.hora_fim),
                        empresa=func.empresa
                    ).distinct()

                    total = eventos_filtrados.count()
                    #total_valor = total * float(ref.valor)

                    #chave = (func.nome, ref.nome)
                    #total_eventos[chave]["total"] += total
                    #total_eventos[chave]["valor"] += total_valor
                    if total == 0:
                        continue # pula refeicao sem registros
                    valor_unit = float(ref.valor)
                    total_valor = total * valor_unit
                    subtotal_func += total_valor



                    totais_funcionarios[func.nome].append({
                        'refeicao': ref.nome,
                        'quantidade': total,
                        'valor_unit': f"{valor_unit:.2f}",
                        'valor_total': f"{total_valor:.2f}",


                    })

                    print(f'estas são as validações {func.nome} - {ref.nome}: {total} eventos X {ref.valor} = {total_valor}')


                if subtotal_func > 0:
                    totais_funcionarios[func.nome].append({
                        'subtotal': f"{subtotal_func:.2f}"
                    })
                    total_geral += subtotal_func

            print(f"Total geral = {total_geral:.2f}")

            context = {
                'funcionario': funcionario_nome,
                'totais_funcionarios': dict(totais_funcionarios),
                'tot_geral': f"{total_geral:.2f}",
                'data_inicial': data_inicial,
                'data_final': data_final,
            }
            return render(
                requisicao,
                template_name='website/home/relatorio/tot_func/resultado.html',
                context=context
            )

    return render(
        requisicao,
        template_name='website/home/relatorio/tot_func/semdados.html'
    )

# Relatorios Refeições Totalizadas
@grupo_required(['Administrador', 'Operador', 'Consultar'])
def tot_refeicao(requisicao: HttpRequest):
    user = requisicao.user
    empresa_usuario = getattr(user.profile, 'empresa', None) if not user.is_superuser else None


    if requisicao.method == 'GET':
        print('entrou no get relatorio de tot_refeicoes')
        return render(requisicao, template_name='website/home/relatorio/tot_refeicao/tot_refeicao.html')
    elif requisicao.method == 'POST':
        print('entrou no post')
        print(f'este é o post = {requisicao.method == "POST"}')
        form = EventoForm(requisicao.POST)
        acao = requisicao.POST.get('acao') or requisicao.POST.get('status') or 'consultar'

        if acao == 'consultar':
            data_inicial = requisicao.POST.get('data_inicio')
            data_final = requisicao.POST.get('data_final')
            print(f'Periodo sleecionado: {data_inicial} à {data_final}')

            #Define o conjunto de refeições e eventos de acordo com o tipo de usuario
            if user.is_superuser:
                refeicoes = Refeicao.objects.all()
                eventos_base = Evento.objects.all()
            else:
                refeicoes = Refeicao.objects.filter(empresa=empresa_usuario)
                eventos_base = Evento.objects.filter(empresa=empresa_usuario)

            total_eventos = []
            total_geral = 0.0

            for ref in refeicoes:
                print(f'Processando refeicao: {ref.nome} ({ref.hora_inicio} - {ref.hora_fim}')
                eventos_filtrados = eventos_base.filter(
                    data__range = (data_inicial, data_final),
                    hora__range = (ref.hora_inicio, ref.hora_fim),
                    empresa = ref.empresa # Garante que só conte eventos da mesma empresa
                ).distinct()

                total = eventos_filtrados.count()
                valor_unit = float(ref.valor)
                valor_total_num = total * valor_unit # valor numerico
                total_geral += valor_total_num
                empresa_nome = ref.empresa.nome if ref.empresa else "Sem Empresa"
                total_eventos.append((
                    ref.nome,
                    str(total),
                    f"{valor_unit:.2f}",
                    f"{valor_total_num:.2f}",
                    empresa_nome
                ))

                print(f'{ref.nome}: {total} eventos X {valor_unit} = {valor_total_num}')
            # Contexto para o template
            context = {
                'total_eventos': total_eventos,
                'tot_geral': f"{total_geral:.2f}",
                'data_inicial': data_inicial,
                'data_final': data_final
            }
            return render(
                requisicao,
                template_name='website/home/relatorio/tot_refeicao/resultado.html',
                context=context
            )
    return render(
        requisicao,
        template_name='website/home/relatorio/tot_refeicao/semdados.html',
    )

# Sobre
@grupo_required(['Administrador', 'Operador', 'Consultar'])
def sobre(requisicao: HttpRequest):
    print(f"este é o GET = {requisicao.method == 'GET'}")
    if requisicao.method == 'GET':
        print(f'entrou no if do get')
        return render(requisicao, template_name='website/home/ajuda/sobre/sobre.html')

# Configurações


# Modelo de Refeições
@grupo_required(['Administrador'])
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

@grupo_required(['Administrador'])
def cria_usuario(requisicao: HttpRequest):
    user = requisicao.user
    empresa_usuario = user.profile.empresa if hasattr(user, 'profile') else None

    if requisicao.method == 'GET':
        print(f'entrou no if do get usuario')
        grupo = Group.objects.all()
        print(f'Grupo selecionado: {grupo}')
        context = {'grupo': grupo}
        return render(requisicao,
                      template_name='website/home/configuracoes/logins/logins.html',
                      context=context
        )

    elif requisicao.method == 'POST':
        print('entrou no post')
        form = UsuarioForm(requisicao.POST)
        acao = requisicao.POST.get('acao') or requisicao.POST.get('status') or 'incluir'
        print(f'esta é a ação: {acao}')

        if acao == 'incluir':
            print('Entrou no incluir')
            username = requisicao.POST['username']
            password = requisicao.POST['password']
            email = requisicao.POST.get('email', '')
            first_name = requisicao.POST.get('first_name', '')
            last_name = requisicao.POST.get('last_name', '')

            # Captura o grupo escolhido no select

            grupo_id = requisicao.POST.get('grupo')
            print(f'Grupo selecionado: {grupo_id}')


            # Cria o usuário
            novo_usuario = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_superuser=False
            )
            print(f'este é o novo usuario: {novo_usuario}')

            # Associa o grupo escolhido
            if grupo_id:
                try:
                    grupo = Group.objects.get(id=grupo_id)
                    novo_usuario.groups.add(grupo)
                    print(f'Grupo {grupo.name} associado ao usuario {novo_usuario.username}')
                except Group.DoesNotExist:
                    print(f'Erro: grupo com o id {grupo_id} não existe')

            # Atualiza o profile ou cria caso Não exista
            try:
                profile = Profile.objects.get(user=novo_usuario)
                # Atualiza o campo empresa (ou outros campos que queira copiar)
                profile.empresa = empresa_usuario
                profile.save()
                print(f'Profile do novo usuario atualizado: empresa: {profile.empresa}')
            except Profile.DoesNotExist:
                # Se por algum motivo o profile não existir, cria com default
                profile = Profile.objects.create(user=novo_usuario, empresa=empresa_usuario)
                print('Profile não existia - Criado Agora.')

            # Recupera listagem ou redireciona conforme teu fluxo
            logins = User.objects.all()
            context= {'logins': logins}
            print(f'Usuario {novo_usuario.username} criado com sucesso. Empresa atribuida: {empresa_usuario}. Grupo: {getattr(grupo, "name", None)}')

            return render(
                requisicao,
                template_name='website/home/configuracoes/logins/salvo.html',
                context=context
            )

        elif status == 'alterar':
            print('entrou no alterar')
            username = requisicao.POST['username']
            nova_senha = requisicao.POST['password']
            email = requisicao.POST.get('email', '')
            first_name = requisicao.POST.get('last_name', '')
            last_name = requisicao.POST.get('last_name', '')
            grupo_id = requisicao.POST.get('grupo')

            user = User.objects.get(username=username)

            # Atualiza dados basicos
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            if nova_senha:
                user.set_password(nova_senha)

            user.save()

            # Atualiza grupo (se enviado no form)
            if grupo_id:
                grupo = Group.objects.get(id=grupo_id)
                user.groups.clear()
                user.groups.add(grupo)

            # Garante que o profile continue na mesma empresa
            profile = Profile.objects.filter(user=user).first()
            if not profile:
                profile = Profile.objects.filter(user=user, empresa=requisicao.user.profile.empresa)
            else:
                profile.empresa = requisicao.user.profile.empresa
                profile.save()

            context = {
                'logins': User.objects.all()
            }
            return render(requisicao,
                          template_name='website/home/configuracoes/logins/alterado.html',
                          context=context
            )


        elif status == 'excluir':
            print('entrou no excluir')
            username = requisicao.POST['username']
            user = User.objects.get(username=username)

            if user == requisicao.user:
                messages.error(requisicao, 'Você não pode excluir seu próprio usuario.')
            else:
                Profile.objects.filter(user=user).delete()
                user.delete()
                messages.success(requisicao, f"Usuario {username} excluido com sucesso.")

            logins = User.objects.all()
            context = {
                'logins': logins
            }

            return render(requisicao,
                          template_name='website/home/configuracoes/logins/excluido.html',
                          context=context
            )

        elif status == 'consultar':
            print('entrou no consultar')

            # pega a empresa do usuario logado
            user = requisicao.user

            if user.is_superuser:
                logins = User.objects.all()
            else:
                empresa_usuario = getattr(user.profile, 'empresa', None)
                if empresa_usuario:
                    # filtra usuarios da mesma empresa
                    logins = User.objects.filter(profile__empresa=empresa_usuario)
                else:
                    logins = User.objects.none() #usuario sem empresa não vê ninguém
            context = {
                'logins': logins
            }

            return render(requisicao,
                          template_name='website/home/configuracoes/logins/salvo.html',
                          context=context
            )

# Relatorio de Funcionarios
@grupo_required(['Administrador', 'Operador', 'Consultar'])
def relat_funcionarios(requisicao: HttpRequest):
    user = requisicao.user
    empresa_usuario = getattr(user.profile, 'empresa', None) if not user.is_superuser else None
    if requisicao.method == "GET":
        print('entrou no Get de Relat Funcionario')
        if user.is_superuser:
            form = FuncionarioForm
            func = Funcionario.objects.all()
        else:
            form = FuncionarioForm
            func = Funcionario.objects.filter(empresa=empresa_usuario)

        print(f'este é o func = {func}')

        context = {
            'form': form,
            'func': func
        }
        return render(requisicao, template_name='website/home/relatorio/funcionarios/funcionarios.html', context=context)

@grupo_required(['Administrador', 'Operador', 'Consultar'])
def relat_visitantes(requisicao: HttpRequest):
    user = requisicao.user
    empresa_usuario = getattr(user.profile, 'empresa', None) if not user.is_superuser else None
    if requisicao.method == "GET":
        print('entrou no Get de Relat Visitante')
        form = VisitanteForm
        if user.is_superuser:
            visi = Visitante.objects.all()
        else:
            visi = Visitante.objects.filter(empresa=empresa_usuario)


        context = {
            'form': form,
            'visi': visi
        }
        return render(requisicao, template_name='website/home/relatorio/visitantes/visitantes.html', context=context)

#Relatorio de Terceiros
@grupo_required(['Administrador', 'Operador', 'Consultar'])
def relat_terceiros(requisicao: HttpRequest):
    user = requisicao.user
    empresa_usuario = getattr(user.profile, 'empresa', None) if not user.is_superuser else None
    if requisicao.method == "GET":
        print('entrou no Get de Relat Funcionario')
        form = TerceiroForm
        if user.is_superuser:
            terc = Terceiro.objects.all()
        else:
            terc = Terceiro.objects.filter(empresa=empresa_usuario)

        context = {
            'form': form,
            'terc': terc
        }
        return render(requisicao, template_name='website/home/relatorio/terceiros/terceiros.html', context=context)

