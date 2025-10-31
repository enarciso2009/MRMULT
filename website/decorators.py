from django.shortcuts import redirect

def grupo_required(grupos_permitidos):
    def decorator(view_func):
        print(f'view_func: {view_func}')
        print('entrou no decorator')
        def wrapped_view(request, *args, **kwargs):
            print(f'este é o request {request, *args,}')
            print('entrou no whapped_view')
            # Verifica se o usuario esta em algum grupo permitido
            if request.user.groups.filter(name__in=grupos_permitidos).exists():
                usuario = request.user.groups.filter(name__in=grupos_permitidos).exists()
                print(f'usuario com algum grupo de acesso {usuario}')
                return view_func(request, *args, **kwargs)

            if not request.user.is_authenticated:
                print('entrou no nao autenticado')
                #Usuario não autenticado vai para login
                return redirect('website:login')

                # superuser sempre pode acessar tudo
            if request.user.is_superuser:
                print('usuario superuser')
                return view_func(request, *args, **kwargs)


            # Se não autorizado, redireciona para pagina de acesso negado
            return redirect('website:acesso_negado')
        return wrapped_view
    return decorator
