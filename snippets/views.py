from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import SnippetForm
from . import models
from .tasks import sendEmailInSnippetCreation

class SnippetAdd(LoginRequiredMixin, View):
    """
    Vista para manejar la creación de snippets, disponible solo para usuarios autenticados.

    Atributos:
        login_url (str): URL a la cual redirigir si el usuario no está autenticado.

    Métodos:
        get(request):
            Renderiza la página para agregar un snippet con un formulario vacío.

        post(request):
            Procesa el formulario enviado para agregar un snippet. Si es válido,
            guarda el snippet y lo asocia con el usuario actual.
    """

    login_url = "login"

    def get(self, request):
        """
        Maneja la solicitud GET para mostrar el formulario de creación de snippets.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.

        Returns:
            HttpResponse: Página HTML con el formulario de creación de snippets.
        """
        return render(
            request, 
            "snippets/snippet_add.html", 
            {'form': SnippetForm, 'action': 'Agregar'},
        )

    def post(self, request):
        """
        Maneja la solicitud POST para procesar el formulario de creación de snippets.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP con los datos del formulario.

        Returns:
            HttpResponse: Redirige a la página principal si el formulario es válido.
                          De lo contrario, vuelve a cargar el formulario.
        """
        form = SnippetForm(request.POST)

        if form.is_valid():
            new_snippet = form.save(commit=False)
            new_snippet.user = request.user
            new_snippet.save()
            return redirect('index')

        return render(
            request, 
            "snippets/snippet_add.html", 
            {'form': SnippetForm, 'action': 'Agregar'},
        )

class SnippetEdit(LoginRequiredMixin, View):
    """
    Vista para manejar la edición de snippets, permitiendo la edición solo al propietario del snippet.

    Atributos:
        login_url (str): URL a la cual redirigir si el usuario no está autenticado.

    Métodos:
        get(request, *args, **kwargs):
            Renderiza la página de edición con el formulario cargado con los datos del snippet.

        post(request, *args, **kwargs):
            Procesa el formulario enviado para actualizar un snippet. Si es válido,
            guarda los cambios en el snippet.
    """

    login_url = "login"

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar el formulario de edición de snippets.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales, usados para obtener el ID del snippet.

        Returns:
            HttpResponse: Página HTML con el formulario de edición de snippets.
        """
        snippet_id = self.kwargs.get("id")
        snippet = get_object_or_404(models.Snippet, id=snippet_id)
        form = SnippetForm(instance=snippet)
        return render(
            request, 
            "snippets/snippet_add.html", 
            {"form": form, "action": "Editar"},
        )
    
    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud POST para procesar el formulario de edición de snippets.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP con los datos del formulario.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales, usados para obtener el ID del snippet.

        Returns:
            HttpResponse: Redirige a la página principal si el formulario es válido.
                          De lo contrario, vuelve a cargar el formulario.
        """
        snippet_id = self.kwargs.get("id")
        snippet = get_object_or_404(models.Snippet, id=snippet_id)

        form = SnippetForm(request.POST, instance=snippet)

        if form.is_valid():
            form.save()
            return redirect("index")

        return render(
            request, 
            "snippets/snippet_add.html", 
            {"form": form, "action": "Editar"}, 
        )

class SnippetDelete(LoginRequiredMixin, View):
    """
    Vista para manejar la eliminación de snippets, permitiendo la eliminación solo al propietario del snippet.

    Atributos:
        login_url (str): URL a la cual redirigir si el usuario no está autenticado.

    Métodos:
        get(request, *args, **kwargs):
            Renderiza la página de confirmación de eliminación de snippets.

        post(request, *args, **kwargs):
            Procesa la solicitud de eliminación de un snippet. Solo el propietario puede eliminar el snippet.
    """

    login_url = "login"

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar la página de confirmación de eliminación de snippets.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales, usados para obtener el ID del snippet.

        Returns:
            HttpResponse: Página HTML de confirmación de eliminación.
        """
        return render(
            request, 
            "snippets/snippet_add.html", 
            {"action": "Eliminar"},
        )

    def post(self, request, *args, **kwargs):
        """
        Maneja la solicitud POST para eliminar un snippet específico.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales, usados para obtener el ID del snippet.

        Returns:
            HttpResponseRedirect: Redirige a la página principal si el snippet es eliminado exitosamente
                                  o si el usuario no tiene permisos.
        """
        snippet_id = self.kwargs.get("id")
        snippet = get_object_or_404(models.Snippet, id=snippet_id)

        if snippet.user == request.user:
            snippet.delete()
            return redirect("index")

        return redirect("index")

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class SnippetDetails(View):
    """
    Vista para mostrar los detalles de un snippet específico.

    Métodos:
        get(request, *args, **kwargs):
            Obtiene un snippet por su ID y renderiza su contenido con resaltado de sintaxis.
    """

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar los detalles de un snippet, incluyendo el código con resaltado de sintaxis.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales, usados para obtener el ID del snippet.

        Returns:
            HttpResponse: Página HTML con los detalles del snippet y su código resaltado.
        """
        snippet_id = self.kwargs["id"]
        snippet = models.Snippet.objects.get(id=snippet_id)

        lenguaje = str(snippet.language)

        try:
            lexer = get_lexer_by_name(lenguaje)
        except:
            lexer = get_lexer_by_name("text")

        formatter = HtmlFormatter(style='monokai')
        codigo = highlight(snippet.snippet, lexer, formatter)

        return render(
            request, 
            "snippets/snippet.html", 
            {"snippet": snippet, "code": codigo},
        )

class UserSnippets(View):
    """
    Vista para mostrar los snippets de un usuario específico, aplicando lógica de acceso público y privado.

    Métodos:
        get(request, *args, **kwargs):
            Obtiene los snippets del usuario especificado según su visibilidad (público/privado).
    """

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar los snippets de un usuario.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales, usados para obtener el nombre de usuario.

        Returns:
            HttpResponse: Página HTML con los snippets del usuario especificado.
                          Solo los snippets públicos serán visibles para otros usuarios;
                          si el usuario actual es el propietario, verá todos sus snippets.
        """
        username = self.kwargs["username"]
        usuario = get_object_or_404(models.User, username=username)

        if request.user.is_anonymous:
            snippets = usuario.snippet_set.filter(public=True)
        elif request.user == usuario:
            snippets = usuario.snippet_set.all()
        else:
            snippets = usuario.snippet_set.filter(public=True)

        return render(
            request,
            "snippets/user_snippets.html",
            {"snippetUsername": username, "snippets": snippets},
        )

class SnippetsByLanguage(View):
    """
    Vista para mostrar snippets según el lenguaje de programación especificado.

    Métodos:
        get(request, *args, **kwargs):
            Obtiene los snippets filtrados por el lenguaje especificado y visibilidad pública/privada.
    """

    def get(self, request, *args, **kwargs):
        """
        Manejo de solicitud GET para mostrar los snippets de un lenguaje específico.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales, usados para obtener el slug del lenguaje.

        Returns:
            HttpResponse: Página HTML con los snippets filtrados por el lenguaje.
                          Solo se muestran los snippets públicos para usuarios anónimos,
                          mientras que los usuarios autenticados pueden ver también sus propios snippets privados.
        """
        language = self.kwargs["language"]
        language_table = get_object_or_404(models.Language, slug=language)

        if request.user.is_anonymous:
            snippets = language_table.snippet_set.filter(public=True)
        else:
            snippets = language_table.snippet_set.filter(public=True) | language_table.snippet_set.filter(user=request.user)

        return render(
            request, 
            "index.html", 
            {"snippets": snippets},
        )

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

class Login(View):
    """
    Vista para manejar el inicio de sesión de los usuarios.

    Métodos:
        get(request):
            Renderiza la página de inicio de sesión con un formulario de autenticación.

        post(request):
            Procesa el formulario de inicio de sesión y autentica al usuario.
    """

    def get(self, request):
        """
        Maneja la solicitud GET para mostrar la página de inicio de sesión.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.

        Returns:
            HttpResponse: Página HTML con el formulario de inicio de sesión.
        """
        return render(
            request,
            "login.html",
            {'form': AuthenticationForm},
        )

    def post(self, request):
        """
        Maneja la solicitud POST para procesar el inicio de sesión.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP que contiene los datos del formulario.

        Returns:
            HttpResponse: Redirige a la página principal si la autenticación es exitosa,
                          de lo contrario, vuelve a mostrar la página de inicio de sesión.
        """
        usuario = request.POST.get('username')
        contra = request.POST.get('password')

        user = authenticate(request, username=usuario, password=contra)

        if user is None:
            return render(
                request, 
                "login.html", 
                {'form': AuthenticationForm},
            )
        else:
            login(request, user)
            return redirect('index')

class Logout(View):
    """
    Vista para manejar el cierre de sesión de los usuarios.

    Métodos:
        get(request):
            Cierra la sesión del usuario y redirige a la página principal.
    """

    def get(self, request):
        """
        Maneja la solicitud GET para cerrar la sesión del usuario.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.

        Returns:
            HttpResponseRedirect: Redirige a la página principal después de cerrar la sesión.
        """
        logout(request)
        return redirect("index")

class Index(View):
    """
    Vista para mostrar la página principal con todos los snippets públicos
    y los snippets del usuario autenticado.

    Métodos:
        get(request, *args, **kwargs):
            Obtiene y muestra todos los snippets públicos, así como los del usuario autenticado.
    """

    def get(self, request, *args, **kwargs):
        """
        Maneja la solicitud GET para mostrar la página principal.

        Args:
            request (HttpRequest): Objeto de solicitud HTTP.
            *args: Argumentos adicionales.
            **kwargs: Argumentos clave adicionales.

        Returns:
            HttpResponse: Página HTML que muestra todos los snippets públicos
                          y los snippets del usuario autenticado.
        """
        
        snippets_user = []
        snippets_publics = models.Snippet.objects.filter(public=True)
        
        snippet_ids = set()

        if not request.user.is_anonymous:
            try:
                snippets_user = request.user.snippet_set.all()
            except Exception as e:
                snippets_user = []

            for snippet in snippets_user:
                snippet_ids.add(snippet.id)

        snippets = list(snippets_user)
        for snippet in snippets_publics:
            if snippet.id not in snippet_ids:
                snippets.append(snippet)

        return render(
            request, 
            "index.html", 
            {"snippets": snippets},
        )