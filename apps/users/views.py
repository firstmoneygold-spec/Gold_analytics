from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import CustomUser
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer


# ==============================================================================
# Web UI Views (Template Rendered)
# ==============================================================================

def register_view(request):
    """Render registration form and handle account creation."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to TrendMaster AI, {user.full_name or user.email}! Your free tier account is ready.")
            return redirect('dashboard:home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """Render login form and authenticate user."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    # Ensure demo accounts exist on fresh cloud deployments
    try:
        if not CustomUser.objects.filter(email='trader@trendmaster.ai').exists():
            from django.core.management import call_command
            call_command('create_demo_trader')
    except Exception:
        pass

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, "Welcome back to TrendMaster AI.")
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid credentials or disabled account.")
    else:
        form = UserLoginForm()

    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    """Log out authenticated user and redirect to login."""
    logout(request)
    messages.info(request, "You have been signed out successfully.")
    return redirect('users:login')


@login_required
def profile_view(request):
    """View and update user profile, market preferences, and SaaS tier info."""
    user = request.user
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile and market preferences were updated successfully.")
            return redirect('users:profile')
    else:
        form = UserProfileUpdateForm(instance=user)

    token, _ = Token.objects.get_or_create(user=user)
    can_predict, quota_msg = user.can_make_prediction()

    context = {
        'form': form,
        'user': user,
        'api_token': token.key,
        'can_predict': can_predict,
        'quota_msg': quota_msg,
    }
    return render(request, 'auth/profile.html', context)


@login_required
@require_POST
def switch_market_preference(request):
    """Quick AJAX toggle to switch between US ($) and India (₹) market view."""
    market = request.POST.get('market', '').upper()
    if market in [CustomUser.MarketPreference.INDIA, CustomUser.MarketPreference.USA, CustomUser.MarketPreference.GLOBAL]:
        request.user.preferred_market = market
        if market == CustomUser.MarketPreference.INDIA:
            request.user.preferred_currency = CustomUser.CurrencyPreference.INR
            request.user.preferred_gold_unit = CustomUser.GoldUnitPreference.TEN_GRAMS
        elif market == CustomUser.MarketPreference.USA:
            request.user.preferred_currency = CustomUser.CurrencyPreference.USD
            request.user.preferred_gold_unit = CustomUser.GoldUnitPreference.TROY_OUNCE
        request.user.save()
        return JsonResponse({'status': 'success', 'market': market, 'currency': request.user.preferred_currency})
    return JsonResponse({'status': 'error', 'message': 'Invalid market selection'}, status=400)


# ==============================================================================
# REST API Endpoints (DRF + Tokens)
# ==============================================================================

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'status': 'success',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'status': 'success',
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
