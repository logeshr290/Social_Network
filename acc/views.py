import logging
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.core.paginator import Paginator

from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import FriendRequest
from .forms import UserSignupForm, UserLoginForm
from .serializers import UserSerializer

User = get_user_model()

def home(request):
    return render(request, 'home.html')

class UserSignupView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        form = UserSignupForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('home'))
        return render(request, 'signup.html', {'form': form})

class UserLoginView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('list-friends'))
        return render(request, 'login.html', {'form': form})

class UserSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

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
        ).order_by('username')
        if search_query:
            potential_friends = potential_friends.filter(
                Q(username__icontains=search_query) | Q(email__icontains=search_query)
            )

        paginator = Paginator(potential_friends, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        pending_requests = FriendRequest.objects.filter(receiver=user, status='pending')
        sent_requests = FriendRequest.objects.filter(sender=user, status='pending')

        context = {
            'friends': friends,
            'page_obj': page_obj,
            'pending_requests': pending_requests,
            'sent_requests': sent_requests,
            'search_query': search_query,
        }
        return render(request, 'list_friends.html', context)

    def update_potential_friends(self, user):
        potential_friends = User.objects.exclude(
            Q(id=user.id) | Q(sent_requests__receiver=user, sent_requests__status='accepted') |
            Q(received_requests__sender=user, received_requests__status='accepted')
        )
        return potential_friends

def logout_view(request):
    logout(request)
    return redirect(reverse('home'))

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender_id = request.data.get('sender_id')

        if not sender_id:
            return Response({"error": "Sender ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            friend_request = FriendRequest.objects.get(sender_id=sender_id, receiver=request.user, status='pending')
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request does not exist."}, status=status.HTTP_404_NOT_FOUND)
        friend_request.status = 'accepted'
        friend_request.save()
        return Response({"message": "Friend request accepted."}, status=status.HTTP_200_OK)

class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender_id = request.data.get('sender_id')

        if not sender_id:
            return Response({"error": "Sender ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            friend_request = FriendRequest.objects.get(sender_id=sender_id, receiver=request.user, status='pending')
        except FriendRequest.DoesNotExist:
            return Response({"error": "Friend request does not exist."}, status=status.HTTP_404_NOT_FOUND)
        friend_request.delete()
        return Response({"message": "Friend request rejected."}, status=status.HTTP_200_OK)
