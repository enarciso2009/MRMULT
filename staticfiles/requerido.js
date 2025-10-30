const = form = document.getElementById('meuFormulario');

form.addEventListener('submit', function(event) {
    // identifica qual botao foi clicado
    const botaoClicado = event.submitter;

    // se o botão for "consultar" não faz a validação obrigatoria
    if (botaoClicado && botaoClicado.id === "btnConsultar") {
        return; // deixa enviar o formulario normalmente
    }
    const campos = form.querySelectorAll('[required]');
    let tudoPreenchido = true;

    campos.forEach(campo => {
        if (!campo.value.trim()) {
            campo.setCustomValidity('Este campo é obrigatório!');
            campo.reportValidity();
            tudoPreenchido = false;
        }   else {
            campo.setCustomValidity('');
        }
    });

    if (!tudoPreenchido) {
        event.preventDefault();
    }
]);