from django.urls import path
from .views import browse
from .views import about
from .views import manage
from .views import login
from .views import theme
from .views import user
from .views import linker
from .views import download
from .views import update
from .views import delete
from .views import docs
from .views import resource
from .views import audio
from .views import logout

urlpatterns = [
    path('', browse),
    path('about', about),
    path('docs', docs),
    path('manage', manage),
    path('login', login),
    path('u/<str:user>', user),
    path('l/<str:user>/<str:linker>', linker),
    path('g/<str:user>/<str:linker>', download),
    path('r/<str:user>/<str:linker>/<str:type>/<str:file>', resource),
    path('d/<str:linker>', delete),
    path('p/<str:linker>', update),
    path('theme.css', theme),
    path('audio.js', audio),
    path('logout', logout),
]
