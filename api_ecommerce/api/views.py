from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from models import Usuario, Endereco
from django.views import View

# Criar requisições