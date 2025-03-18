from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views import View
from api.serializers import UsuarioSerializer, EnderecoSerializer, CartaoSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Criar requisições
from .models import Usuario, Endereco, CartaoCredito
from rest_framework import status


class UsuarioView(APIView):

    @swagger_auto_schema(
        operation_description="Cria um novo usuário.",
        request_body=UsuarioSerializer,
        responses={
            201: UsuarioSerializer,
            400: "Erro de validação: Email ou CPF já cadastrados."
        }
    )
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            cpf = serializer.validated_data.get('cpf')

            if Usuario.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Este email já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Usuario.objects.filter(cpf=cpf).exists():
                return Response(
                    {'error': 'Este CPF já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retorna um usuário específico pelo ID ou lista todos os usuários se nenhum ID for fornecido.",
        pk_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID do usuário",
                required=True
            )
        ],
        responses={
            200: UsuarioSerializer(many=True),
            404: "Usuário não encontrado."
        }
    )
    def get(self, request, pk=None):
        if pk:
            try:
                # Se na requisição é enviado um ID de usuário, programa verifica se existe na base de dados e caso exista, 
                # retorna os dados do usuário junto dos de cartão e endereço.
                usuario = Usuario.objects.prefetch_related('cartoes', 'enderecos').get(pk=pk)
                serializer = UsuarioSerializer(usuario)
                return Response(serializer.data)
            except Usuario.DoesNotExist:
                return Response(
                    {'error': 'Usuário não encontrado.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        usuarios = Usuario.objects.prefetch_related('cartoes', 'enderecos').all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Atualiza um usuário pelo ID (parcialmente).",
        request_body=UsuarioSerializer,
        responses={
            200: UsuarioSerializer,
            400: "Erro de validação: Email já cadastrado.",
            404: "Usuário não encontrado."
        }
    )
    def patch(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            if Usuario.objects.filter(email=email).exclude(pk=pk).exists():
                return Response(
                    {'error': 'Este email já foi cadastrado anteriormente.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Exclui um usuário pelo ID.",
        responses={
            204: "Usuário excluído com sucesso.",
            404: "Usuário não encontrado."
        }
    )
    def delete(self, request, pk):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EnderecoView(APIView):

    @swagger_auto_schema(
        request_body=EnderecoSerializer,
        responses={201: EnderecoSerializer, 400: "Erro de validação"},
        operation_description="Cria um novo endereço.",
    )
    def post(self, request):
        serializer = EnderecoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Obtém um endereço pelo ID ou lista todos os endereços.",
        pk_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="ID do endereço",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={200: EnderecoSerializer(many=True), 404: "Endereço não encontrado"},
    )
    def get(self, request, pk=None):
        if pk:
            try:
                endereco = Endereco.objects.get(pk=pk)
                serializer = EnderecoSerializer(endereco)
                return Response(serializer.data)
            except Endereco.DoesNotExist:
                return Response(
                    {"error": "Endereço não encontrado."}, status=status.HTTP_404_NOT_FOUND
                )

        enderecos = Endereco.objects.all()
        serializer = EnderecoSerializer(enderecos, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=EnderecoSerializer,
        responses={200: EnderecoSerializer, 400: "Erro de validação", 404: "Endereço não encontrado"},
        operation_description="Atualiza parcialmente um endereço pelo ID.",
    )
    def patch(self, request, pk):
        try:
            endereco = Endereco.objects.get(pk=pk)
        except Endereco.DoesNotExist:
            return Response(
                {"error": "Endereço não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = EnderecoSerializer(endereco, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={204: "Endereço deletado", 404: "Endereço não encontrado"},
        operation_description="Deleta um endereço pelo ID.",
    )
    def delete(self, request, pk):
        try:
            endereco = Endereco.objects.get(pk=pk)
        except Endereco.DoesNotExist:
            return Response(
                {"error": "Endereço não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        endereco.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


