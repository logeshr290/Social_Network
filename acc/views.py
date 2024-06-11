from django.http import HttpResponse
import logging
from rest_framework.exceptions import NotFound
from django.template.response import TemplateResponse
from django.contrib.auth import logout
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate, login
from .models import FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.authtoken.models import Token
from datetime import timedelta
from .serializers import UserSignupSerializer, UserLoginSerializer

User = get_user_model()

def home(request):
    return render(request, 'home.html')

class UserSignupView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSignupSerializer

    def get(self, request, *args, **kwargs):
        return Response({
            "message": "Provide email, username, and password to sign up.",
            "fields": ["email", "username", "password"]
        })

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect(reverse('home'))
            return Response({"message": "Signup successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def get(self, request, *args, **kwargs):
        return Response({
            "message": "Provide email and password to log in.",
            "fields": ["email", "password"]
        })

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return redirect(reverse('list-friends'))

class UserSearchView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            logging.info("Empty query parameter")
            return User.objects.none()

        logging.info(f"Query parameter: {query}")
        return User.objects.filter(
            Q(email__iexact=query) |
            Q(username__icontains=query) |
            Q(first_name__icontains=query)
        )


class ListFriendsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        friends = User.objects.filter(
            Q(sent_requests__receiver=user, sent_requests__status='accepted') |
            Q(received_requests__sender=user, received_requests__status='accepted')
        ).distinct()

        search_query = request.GET.get('search', '')
        potential_friends = User.objects.exclude(
            Q(id=user.id) | Q(sent_requests__receiver=user, sent_requests__status='accepted') |
            Q(received_requests__sender=user, received_requests__status='accepted')
        )
        if search_query:
            potential_friends = potential_friends.filter(
                Q(username__icontains=search_query) | Q(email__icontains=search_query)
            )

        pending_requests = FriendRequest.objects.filter(receiver=user, status='pending')
        context = {
            'friends': friends,
            'potential_friends': potential_friends,
            'pending_requests': pending_requests,
            'search_query': search_query,
        }
        return TemplateResponse(request, 'list_friends.html', context)



def logout_view(request):
    logout(request)
    return redirect(reverse('home'))

class SendFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sender = request.user
        receiver_email = request.data.get('receiver_email')
        try:
            receiver = User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if sender.sent_requests.filter(created_at__gte=timezone.now() - timedelta(minutes=1)).count() >= 3:
            return Response({"error": "You cannot send more than 3 friend requests within a minute."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            return Response({"error": "Friend request already sent."}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest(sender=sender, receiver=receiver)
        friend_request.save()
        return Response({"message": "Friend request sent."}, status=status.HTTP_201_CREATED)

class AcceptFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        sender_id = request.data.get('sender_id')

        if not sender_id:
            return Response({"error": "Sender ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        logging.info(f"Received sender_id: {sender_id}, Current user: {request.user}")

        try:
            friend_request = FriendRequest.objects.get(sender_id=sender_id, receiver=request.user, status='pending')
        except FriendRequest.DoesNotExist as e:
            logging.error(f"Friend request does not exist: {e}")
            return Response({"error": "Friend request does not exist."}, status=status.HTTP_404_NOT_FOUND)
        friend_request.status = 'accepted'
        friend_request.save()
        return Response({"message": "Friend request accepted."}, status=status.HTTP_200_OK)

class RejectFriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
