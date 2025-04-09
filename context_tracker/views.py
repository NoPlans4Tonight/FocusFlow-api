from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import status
from .models import ContextEntry, User
from django.utils.timezone import now
from django.contrib.auth import authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken
import json
from datetime import datetime
import logging
from .services.context_service import context_service

class LogContextView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        activity = request.data.get('activity')
        note = request.data.get('note', '')
        response = context_service.log_context(request.user.id, activity, note)
        return Response(response)

    def get(self, request):
        entries = context_service.get_user_contexts(request.user.id)
        return Response(entries)

    def delete(self, request, log_id):
        response = context_service.delete_context(request.user.id, log_id)
        status_code = status.HTTP_200_OK if 'message' in response else status.HTTP_404_NOT_FOUND
        return Response(response, status=status_code)

    def put(self, request, log_id):
        response = context_service.update_context(request.user.id, log_id, request.data)
        status_code = status.HTTP_200_OK if 'message' in response else status.HTTP_404_NOT_FOUND
        return Response(response, status=status_code)

@csrf_exempt
@api_view(['POST'])
def api_login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'message': 'Login successful',
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

@csrf_exempt
@api_view(['POST'])
def user_logout(request):
    logout(request)
    return Response({'message': 'Logout successful'})

@csrf_exempt
@api_view(['POST'])
def user_register(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')

    if not all([username, password, email]):
        return JsonResponse({'error': 'All fields are required'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
    return JsonResponse({'message': 'User registered successfully', 'user_id': user.id})
