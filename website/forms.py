import datetime
from doctest import REPORT_ONLY_FIRST_FAILURE

from django import forms
from website.models import Equipamento, Refeicao, Funcionario, Grupo_Refeicao, Visitante, Evento, Parametro, Terceiro, Inter_grup_ref


# Forms Funcionario
class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        '''
        fields = [
            'matricula', 'nome', 'admissao', 'departamento', 'centro_de_custo', 'cargo', 'documento', 'credencial', 'grup_ref', 'ativo', 'empresa'
        ]
        '''
        exclude = ['grup_ref', 'empresa'] # vamos preencher manualmente

 # Forms Visitante
class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = [
            'matricula', 'nome', 'documento', 'credencial', 'data_inicio', 'data_fim', 'hora_inicio', 'hora_fim', 'func', 'grup_ref', 'motivo', 'empresa'

        ]
# Forms Terceiros
class TerceiroForm(forms.ModelForm):
    class Meta:
        model = Terceiro
        fields = [
            'matricula', 'nome', 'empresa', 'documento', 'credencial', 'data_inicio', 'data_fim', 'hora_inicio', 'hora_fim', 'func', 'grup_ref', 'empresa'

        ]

# Forms Equipamento
class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = [
            'id_equip','nome', 'ip', 'mask', 'empresa'
        ]

class RefeicaoForm(forms.ModelForm):
    class Meta:
        model = Refeicao
        fields = [
            'id_ref', 'nome', 'valor', 'data_inicio', 'hora_inicio', 'data_fim', 'hora_fim', 'empresa'
        ]


class Grupo_RefeicaoForm(forms.ModelForm):
    class Meta:
        model = Grupo_Refeicao
        fields = [
            'id_grup', 'nome', 'empresa', 'refeicoes'
        ]


class BuscaForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            'matricula', 'nome', 'empresa'
        ]

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'id_evento', 'matricula', 'nome', 'data', 'hora', 'equip_id', 'equip_nome', 'empresa'
        ]


class ParametroForm(forms.ModelForm):
    class Meta:
        model = Parametro
        fields = [
            'id_param', 'nome', 'mod_padrao_usu', 'mod_credito_usu', 'mod_padrao_visi', 'mod_credito_visi', 'empresa'
        ]

