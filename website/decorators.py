from django.shortcuts import redirect

def grupo_required(grupos_permitidos):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                #Usuario não autenticado vai para login
                return redirect('website:login')

                # superuser sempre pode acessar tudo
                if request.user.is_superuser:
                    return view_func(request, *args, **kwargs)

                # Verifica se o usuario esta em algum grupo permitido
                if request.user.groups.filter(name__in=grupos_permitidos).exists():
                    return view_func(request, *args, **kwargs)
                # Se não autorizado, redireciona para pagina de acesso negado
            return redirect('website:acesso_negado')
        return wrapped_view
    return decorator
