import random
import razorpay
import hashlib
import hmac
import uuid
from typing import Type
from decimal import Decimal

from django.db.models import Q, Sum
from rest_framework.exceptions import PermissionDenied
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from rest_framework import permissions, status, viewsets, generics, filters
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.parsers import (FileUploadParser, FormParser,
                                    MultiPartParser)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from templated_email import send_templated_mail

from freelancing.custom_auth.models import (ApplicationUser, LoginOtp, CustomBlacklistedToken,
                                         CustomPermission, Wallet, MerchantProfile, Category,
                                        WalletHistory, RazorpayTransaction, MerchantDeal, 
                                        MerchantDealRequest, MerchantDealConfirmation, 
                                        MerchantNotification, MerchantPointsTransfer, DealPointUsage)
from freelancing.custom_auth.permissions import IsSelf
from freelancing.custom_auth.serializers import (BaseUserSerializer,
                                                ChangePasswordSerializer,
                                                PasswordValidationSerializer,
                                                UserAuthSerializer,
                                                UserPhotoSerializer,
                                                UserStatisticSerializerMixin,
                                                CustomPermissionSerializer, SendPasswordResetEmailSerializer,
                                                UserPasswordResetSerializer, MerchantProfileSerializer, WalletSerializer,
                                                CategorySerializer, WalletHistorySerializer, MerchantListingSerializer,
                                                RazorpayOrderSerializer, RazorpayPaymentVerificationSerializer,
                                                RazorpayTransactionSerializer, MerchantDealSerializer, 
                                                MerchantDealCreateSerializer, MerchantDealRequestSerializer, 
                                                MerchantDealConfirmationSerializer, MerchantNotificationSerializer,
                                                MerchantPointsTransferSerializer, DealPointUsageSerializer, DealStatsSerializer
                                            )
# from trade_time_accounting.notification.FCM_manager import unsubscribe_from_topic
from freelancing.registrations.serializers import CheckOtp
from freelancing.utils.permissions import  IsReadAction, IsSuperAdminUser
from freelancing.utils.serializers import add_serializer_mixin

from django.db.models import F, FloatField, ExpressionWrapper, Count
from django.db.models.functions import ACos, Cos, Radians, Sin
from drf_yasg.utils import swagger_auto_schema

from rest_framework_simplejwt.authentication import JWTAuthentication # type: ignore
User = get_user_model()


class UserAuthViewSet(viewsets.ViewSet):
    NEW_TOKEN_HEADER = "X-Token"
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    
    @classmethod
    def get_success_headers(cls, user):
        """
            Generate token for authentication
            :param user:
            :return:
        """
        return {cls.NEW_TOKEN_HEADER: user.tokens.create().key}
        # return {cls.NEW_TOKEN_HEADER: user.user_auth_tokens.create().key}

    def _auth(self, request, *args, **kwargs):
        """
            Represent authentication with email and password, with mobile and otp, with google sign in
            :param request:
            :param args:
            :param kwargs:
            :return:
        """
        auth_serializer = UserAuthSerializer(data=request.data, context={"request": request, "view": self})
        auth_serializer.is_valid(raise_exception=True)

        if 'phone' in auth_serializer.validated_data:
            # Check if user exists, if not, create
            user_mobile = auth_serializer.validated_data['phone']
            user = User.objects.filter(phone=user_mobile).first()
            if not user:
                user = User.objects.create(phone=user_mobile)
            # Send SMS code
            # otp = random.randint(1000, 9999)
            # LoginOtp.objects.update_or_create(user_mobile=user_mobile, defaults={'otp': otp})

            user_details = BaseUserSerializer(
                instance=user, context={"request": request, "view": self}
            ).data

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user_details['access_token'] = access_token
            user_details['refresh_token'] = refresh_token

            # logout previous login
            # token = Token.objects.filter(user_id=user.id)
            # if token.exists() and token.count() > 1:
            #     user.user_auth_tokens.first().delete()

            return Response({'message': 'Login Successful', 'data': user_details, 'success': 'true'},
                            status=status.HTTP_200_OK)
        
        else:
            user = authenticate(request, **auth_serializer.data)
            if not user:
                raise ValidationError("Invalid credentials")

            user_details = BaseUserSerializer(
                instance=user, context={"request": request, "view": self}
            ).data
            # user_details.update(self.get_success_headers(user))
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user_details['access_token'] = access_token
            user_details['refresh_token'] = refresh_token

            # logout previous login
            # token = Token.objects.filter(user_id=user.id)
            # if token.exists() and token.count() > 1:
            #     user.user_auth_tokens.first().delete()

            return Response({'message': 'Login Successful', 'data': user_details, 'success': 'true'},
                            status=status.HTTP_200_OK)
    @swagger_auto_schema(
        method="post",
        request_body=UserAuthSerializer,  # 👈 force swagger to show body schema
        responses={200: "Success"},
        operation_description="Authenticate user using email/password or phone/otp and return JWT tokens.",
    )
    @action(methods=["post"], detail=False, permission_classes=[permissions.AllowAny],
            url_name="classic", url_path="classic")
    def classic_auth(self, request, *args, **kwargs):
        return self._auth(request, *args, for_agent=False, **kwargs)

    # @action(methods=["post"], detail=False)
    # def logout(self, request, *args, **kwargs):

    #     if 'refresh' not in request.data:
    #         raise ValidationError(_('refresh field is required.'))

    #     if request.user.user_type == "student":
    #         unsubscribe_from_topic(
    #             topic="admin_channel", registration_token=request.user.device_token
    #         )
    #         user = request.user
    #         user.device_token = None
    #         user.save()
    #     # self.request.auth.delete()

    #     try:
    #         refresh_token = request.data.get("refresh")
    #         token = RefreshToken(refresh_token)
    #         token.blacklist()

    #         # Extract and blacklist the access token from the Authorization header
    #         auth_header = request.headers.get('Authorization')
    #         if not auth_header:
    #             raise ValidationError("Authorization header is required")
    #         access_token = auth_header.split()[1]
    #         CustomBlacklistedToken.objects.create(token=access_token)

    #         return Response({"data": "Logout Successful! Thank you for using our services. "
    #                                  "Have a great day!", "success": "true"}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         raise ValidationError(_(str(e)))

    #     # if you want delete multiple token
    #     # if request.user.tokens.count() > 1:
    #     #     self.request.auth.delete()
    #     # else:
    #     #     request.user.tokens.all().delete()

    #     # unsubscribe_from_topic(topic="admin_channel", registration_token=request.user.device_token)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [
        permissions.IsAuthenticated
        # IsReadAction | IsSelf,
    ]
    authentication_classes = [JWTAuthentication]
    # lookup_field = "uuid"
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ["fullname"]
    ordering = ["fullname"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Account deleted successfully."}, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action in ["create", "metadata"]:
            return [AllowAny()]

        return super().get_permissions()

    def _get_base_serializer_class(self):
        if self.action == "list":
            return BaseUserSerializer

        if self.action == "set_photo":
            return UserPhotoSerializer

        if self.action == "reset_change_password":
            return PasswordValidationSerializer

        if self.action == "change_password":
            return ChangePasswordSerializer

        return BaseUserSerializer

    @property
    def ordering_fields(self):
        ordering_fields = []
        if "with_statistics" in self.request.query_params or self.action != "list":
            ordering_fields += ["filters_amount"]
        return ordering_fields

    def get_serializer_class(self) -> Type[BaseSerializer]:
        serializer_class = self._get_base_serializer_class()
        # if "with_statistics" in self.request.query_params or self.action != "list":
        #     serializer_class = add_serializer_mixin(
        #         serializer_class, UserStatisticSerializerMixin
        #     )

        return serializer_class

    # def get_queryset(self):
    #     user = self.request.user
    #     return self.queryset.filter(id=user.id)
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_superuser:
    #         return User.objects.all()
    #     return User.objects.filter(user=user)
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    @action(
        detail=False,
        methods=["get", "put", "patch"],
        url_path="me",
        permission_classes=[permissions.IsAuthenticated, IsSelf]
        )
    def me(self, request):
        if request.method in ["PUT", "PATCH"]:
            serializer = self.get_serializer(request.user, data=request.data, partial=(request.method == "PATCH"))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=[permissions.AllowAny, IsSelf],
        url_path="photos/update_or_create",
        url_name="set_photo",
    )
    def set_photo(self, request, *args, **kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        serializer = self.get_serializer(request.user, data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["delete"],
        detail=True,
        permission_classes=[permissions.AllowAny, IsSelf],
        url_path="photos/(?P<id>[0-9]+)",
        url_name="delete_photo",
    )
    def delete_photo(self, request, *args, **kwargs):
        user = self.get_object()
        self.check_object_permissions(request, user)
        user.photo.delete()
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # @action(
    #     methods=["post"],
    #     detail=False,
    #     permission_classes=[permissions.AllowAny, IsAPIKEYAuthenticated],
    #     url_path="reset-password-email",
    #     url_name="reset_password_email",
    # )
    # def reset_password_email(self, request, *args, **kwargs):
    #     """
    #     :param request:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     user_email = request.data.get("email")
    #     user_type = request.data.get("user_type")
    #     if not user_email:
    #         raise ValidationError(_("Email field is required."))
    #     if not user_type:
    #         raise ValidationError(_("User type field is required."))

    #     user_model = User
    #     user = user_model.objects.filter(email__iexact=user_email, is_active=True, is_delete=False).first()

    #     if not user:
    #         raise NotFound(_("User doesn't exists."))

    #     if user.user_type != user_type:
    #         if user.user_type == "sub_admin" and user_type == "admin":
    #             pass  # Allow sub_admin to access admin resources
    #         else:
    #             if user_type == "student":
    #                 raise ValidationError(_("Please enter valid email id"))
    #             raise PermissionDenied("You do not have permission to access this resource.")

    #     if user.user_type == "student" and user.login_type != "S":
    #         raise ValidationError(_("Please enter valid email id"))

    #     otp = random.randint(1111, 9999)

    #     LoginOtp.objects.create(user=user, otp=otp)
    #     # forget_password_otp(user, otp)
    #     site = get_current_site(request)

    #     send_templated_mail(
    #         template_name="user_password_reset",
    #         from_email=settings.DEFAULT_FROM_EMAIL,
    #         recipient_list=[user.email],
    #         context={
    #             'domain': site.domain,
    #             'user': user,
    #             'protocol': 'http',
    #             'otp': otp,
    #         }
    #     )

    #     # return Response(_("Email has been sent."))
    #     return Response({"message": "OTP sent successfully."})

    # @action(
    #     methods=["post"],
    #     permission_classes=[permissions.AllowAny, IsAPIKEYAuthenticated],
    #     url_name="check_otp",
    #     url_path="check-otp",
    #     detail=False,
    # )
    # def check_otp(self, *args, **kwargs):
    #     serializer = CheckOtp(data=self.request.data)
    #     serializer.is_valid(raise_exception=True)

    #     user_model = User
    #     user = user_model.objects.filter(
    #         email=serializer.validated_data.get("email")
    #     ).first()
    #     if not user:
    #         raise NotFound(_("User doesn't exists."))
    #     otp = serializer.data["otp"]
    #     # get_otp = Otp.objects.filter(user=user, expiration_time__gte=timezone.now()).last()
    #     get_otp = (
    #         LoginOtp.objects.filter(user=user, expiration_time__gte=timezone.now()).first()
    #         if int(otp) == 1234
    #         else LoginOtp.objects.filter(
    #             user=user, otp=otp, expiration_time__gt=timezone.now()
    #         ).first()
    #     )
    #     if not get_otp:
    #         raise ValidationError(_("Otp doesn't match"))

    #     # if int(get_otp.otp) == int(serializer.data['otp']):
    #     #     return Response(_("Otp verified!!"), status=HTTP_200_OK)
    #     return Response(_("Otp verified!!"), status=HTTP_200_OK)

    # @action(
    #     methods=["post"],
    #     permission_classes=[permissions.AllowAny, IsAPIKEYAuthenticated],
    #     url_name="reset_change_password",
    #     url_path="reset_change_password",
    #     detail=False,
    # )
    # def reset_change_password(self, request, *args, **kwargs):
    #     email = request.data.get("email")

    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     password_reset_obj = get_object_or_404(
    #         ApplicationUser, email=email, is_delete=False
    #     )

    #     user = ApplicationUser.objects.get(pk=password_reset_obj.id)
    #     user.set_password(serializer.data["password"])
    #     user.save()

    #     # send mail
    #     site = get_current_site(request)

    #     send_templated_mail(
    #         template_name="user_password_reset",
    #         from_email=settings.DEFAULT_FROM_EMAIL,
    #         recipient_list=[user.email],
    #         context={
    #             'domain': site.domain,
    #             'user': user,
    #             'protocol': 'http',
    #             'password': serializer.data["password"],
    #         }
    #     )
    #     # if user.user_type == "student":
    #     #     sing_up_successful(user, serializer.data["password"])

    #     return Response(_("Password reset successfully!"))

    # @action(
    #     methods=["post"],
    #     detail=False,
    #     url_path="change_password",
    #     url_name="change_password",
    # )
    # def change_password(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)

    #     serializer.is_valid(raise_exception=True)

    #     user = request.user
    #     user.set_password(serializer.data["new_password"])
    #     user.save()

    #     return Response(_("Password update successfully!"))



class CustomPermissionViewSet(viewsets.ModelViewSet):
    queryset = CustomPermission.objects.all()
    serializer_class = CustomPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]



class SendPasswordResetEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {
                    "status": "201 Ok",
                    "msg": "Password Reset link send. Pleas check Your Email",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Password Reset Succesfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# MerchantProfileViewSet

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, SearchFilter)
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = None
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "results": serializer.data
        })

# Create your views here.
class MerchantProfileViewSet(viewsets.ModelViewSet):
    queryset = MerchantProfile.objects.all()
    serializer_class = MerchantProfileSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    http_method_names = ['get', 'post']
    # search_fields = ["user__phone"]
    # ordering = [""]

    def perform_create(self, serializer):
        try:
            # Handle case where request.user might not be available (e.g., during Swagger inspection)
            if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
                serializer.save(user=self.request.user)
            else:
                raise ValidationError("User authentication required")
        except IntegrityError:
            raise ValidationError({
                "detail": "A MerchantProfile already exists for this user."
            })
    @action(detail=False, methods=["get", "put", "patch"], url_path="me")
    def me(self, request):
        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
        except MerchantProfile.DoesNotExist:
            return Response(
                {"success": False, "errors": "Merchant profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {"success": False, "errors": "Unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if request.method in ["PUT", "PATCH"]:
            try:
                serializer = self.get_serializer(
                    merchant_profile,
                    data=request.data,
                    partial=(request.method == "PATCH")
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
            except ValidationError as ve:
                return Response(
                    {"success": False, "errors": ve.message_dict},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception:
                return Response(
                    {"success": False, "errors": "Failed to update profile."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        serializer = self.get_serializer(merchant_profile)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    http_method_names = ['get']
    authentication_classes = [JWTAuthentication]
    filter_backends = (DjangoFilterBackend, SearchFilter)

    def get_queryset(self):
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user = self.request.user
            return Wallet.objects.filter(user=user)
        # Return empty queryset for unauthenticated requests or during inspection
        return Wallet.objects.none()

    def perform_create(self, serializer):
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user = self.request.user
            serializer.save(user=user)
        else:
            raise ValidationError("User authentication required")

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Wallet cannot be deleted manually."}, status=status.HTTP_403_FORBIDDEN)

class WalletHistoryListView(generics.ListAPIView):
    serializer_class = WalletHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["transaction_type", "reference_note", "reference_id"]
    ordering_fields = ["create_time", "amount"]
    ordering = ["-create_time"]

    def get_queryset(self):
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user = self.request.user
            wallet = Wallet.objects.filter(user=user).first()

            if not wallet:
                return WalletHistory.objects.none()

            return wallet.histories.all()
        # Return empty queryset for unauthenticated requests or during inspection
        return WalletHistory.objects.none()

class WalletSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Use user's wallet (common wallet for both user and merchant)
        user = request.user
        wallet = Wallet.objects.filter(user=user).first()

        if not wallet:
            return Response({"balance": 0.0, "recent_transactions": []})

        serializer = WalletHistorySerializer(wallet.histories.order_by("-create_time")[:5], many=True)
        return Response({
            "balance": wallet.balance,
            "recent_transactions": serializer.data
        })


class MerchantListAPIView(ListAPIView):
    serializer_class = MerchantListingSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = MerchantProfile.objects.filter(user__is_active=True)

        # Annotate with available vouchers count
        queryset = queryset.annotate(
            available_vouchers_count=Count(
                'vouchers',
                filter=Q(
                    vouchers__is_active=True,
                    vouchers__is_gift_card=False
                ) & (
                    Q(vouchers__count__isnull=True) |  # No limit
                    Q(vouchers__redemption_count__lt=F('vouchers__count'))  # Still has available redemptions
                )
            )
        )

        # Category Filter
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # City Filter
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)

        # State Filter
        state = self.request.query_params.get('state')
        if state:
            queryset = queryset.filter(state__icontains=state)

        # Filter by voucher availability
        has_vouchers = self.request.query_params.get('has_vouchers')
        if has_vouchers:
            if has_vouchers.lower() == 'true':
                queryset = queryset.filter(available_vouchers_count__gt=0)
            elif has_vouchers.lower() == 'false':
                queryset = queryset.filter(available_vouchers_count=0)

        # Order by voucher count if requested
        order_by = self.request.query_params.get('order_by')
        if order_by == 'vouchers_desc':
            queryset = queryset.order_by('-available_vouchers_count')
        elif order_by == 'vouchers_asc':
            queryset = queryset.order_by('available_vouchers_count')

        # Latitude/Longitude (Optional)
        user_lat = self.request.query_params.get('latitude')
        user_lng = self.request.query_params.get('longitude')

        if user_lat and user_lng:
            try:
                user_lat = float(user_lat)
                user_lng = float(user_lng)

                # Ignore merchants without valid lat/lng
                queryset = queryset.filter(latitude__isnull=False, longitude__isnull=False)

                # Haversine Formula
                distance_expr = 6371 * ACos(
                    Cos(Radians(user_lat)) *
                    Cos(Radians(F('latitude'))) *
                    Cos(Radians(F('longitude')) - Radians(user_lng)) +
                    Sin(Radians(user_lat)) *
                    Sin(Radians(F('latitude')))
                )

                queryset = queryset.annotate(
                    distance=ExpressionWrapper(distance_expr, output_field=FloatField())
                ).order_by('distance')

            except (ValueError, TypeError):
                # If conversion fails, just skip distance logic
                pass

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class RazorpayWalletAPIView(APIView):
    """API for Razorpay wallet operations"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize Razorpay client
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def post(self, request):
        """Create Razorpay order for adding points to wallet"""
        serializer = RazorpayOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        amount = serializer.validated_data['amount']
        
        # Get or create wallet for user
        wallet, created = Wallet.objects.get_or_create(user=user)
        
        # Create Razorpay order
        order_data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': serializer.validated_data.get('currency', 'INR'),
            'receipt': f'wallet_recharge_{user.id}_{int(timezone.now().timestamp())}',
            'notes': {
                'user_id': str(user.id),
                'wallet_id': str(wallet.id),
                'type': 'wallet_recharge'
            }
        }
        
        if serializer.validated_data.get('description'):
            order_data['notes']['description'] = serializer.validated_data['description']
        
        try:
            razorpay_order = self.client.order.create(data=order_data)
            
            # Create transaction record
            transaction = RazorpayTransaction.objects.create(
                user=user,
                wallet=wallet,
                razorpay_order_id=razorpay_order['id'],
                amount=amount,
                points_to_add=amount * 10,  # 1 rupee = 10 points
                currency=order_data['currency'],
                description=serializer.validated_data.get('description', ''),
                receipt=order_data['receipt'],
                notes=order_data['notes']
            )
            
            # Prepare auto_fill data with only mobile, name, and email
            auto_fill_data = {
                'mobile': str(user.phone) if user.phone else None,
                'name': user.fullname or f"{user.first_name} {user.last_name}".strip() or None,
                'email': user.email
            }
            
            return Response({
                'success': True,
                'data': {
                    'order_id': razorpay_order['id'],
                    'amount': amount,
                    'currency': order_data['currency'],
                    'receipt': order_data['receipt'],
                    'transaction_id': transaction.id,
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'auto_fill': auto_fill_data
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RazorpayPaymentVerificationAPIView(APIView):
    """API for verifying Razorpay payment and adding points to wallet"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize Razorpay client
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    def post(self, request):
        """Verify Razorpay payment and add points to wallet"""
        serializer = RazorpayPaymentVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        order_id = serializer.validated_data['razorpay_order_id']
        payment_id = serializer.validated_data['razorpay_payment_id']
        signature = serializer.validated_data.get('razorpay_signature', '')
        
        try:
            # Get transaction record
            transaction = RazorpayTransaction.objects.get(
                razorpay_order_id=order_id,
                user=user,
                status='pending'
            )
            
            # Verify signature only if provided
            if signature:
                expected_signature = hmac.new(
                    settings.RAZORPAY_KEY_SECRET.encode(),
                    f"{order_id}|{payment_id}".encode(),
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(expected_signature, signature):
                    transaction.mark_failed('INVALID_SIGNATURE', 'Payment signature verification failed')
                    return Response({
                        'success': False,
                        'error': 'Invalid payment signature'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify payment with Razorpay
            payment = self.client.payment.fetch(payment_id)
            
            if payment['status'] != 'captured':
                transaction.mark_failed('PAYMENT_NOT_CAPTURED', f"Payment status: {payment['status']}")
                return Response({
                    'success': False,
                    'error': f"Payment not captured. Status: {payment['status']}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark transaction as successful and add points
            transaction.mark_successful(payment_id, signature or '')
            
            return Response({
                    'success': True,
                    'data': {
                        'transaction_id': transaction.id,
                        'amount': transaction.amount,
                        'points_added': transaction.points_to_add,  # Show actual points added (10x)
                        'wallet_balance': transaction.wallet.balance,
                        'payment_id': payment_id
                    }
                }, status=status.HTTP_200_OK)
            
        except RazorpayTransaction.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Transaction not found or already processed'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RazorpayTransactionListView(generics.ListAPIView):
    """API for listing user's Razorpay transactions"""
    serializer_class = RazorpayTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'currency']
    ordering_fields = ['create_time', 'amount']
    ordering = ['-create_time']

    def get_queryset(self):
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user = self.request.user
            return RazorpayTransaction.objects.filter(user=user)
        # Return empty queryset for unauthenticated requests or during inspection
        return RazorpayTransaction.objects.none()

# Merchant Deal System APIs
class MerchantDealViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing merchant deals
    """
    serializer_class = MerchantDealSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ['title', 'description']
    filterset_fields = ['status', 'category', 'points_offered']
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'merchant_profile'):
            return MerchantDeal.objects.filter(merchant=user.merchant_profile)
        return MerchantDeal.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MerchantDealCreateSerializer
        return MerchantDealSerializer
    
    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user.merchant_profile)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a deal"""
        deal = self.get_object()
        deal.status = 'active'
        deal.save()
        return Response({'message': 'Deal activated successfully'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a deal"""
        deal = self.get_object()
        deal.status = 'inactive'
        deal.save()
        return Response({'message': 'Deal deactivated successfully'})
    
    @action(detail=True, methods=['get'])
    def usage_history(self, request, pk=None):
        """Get deal point usage history"""
        deal = self.get_object()
        usages = DealPointUsage.objects.filter(deal=deal)
        serializer = DealPointUsageSerializer(usages, many=True, context={'request': request})
        return Response(serializer.data)


class DealDiscoveryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for discovering deals with point-based filtering
    """
    serializer_class = MerchantDealSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ['title', 'description', 'merchant__business_name']
    filterset_fields = ['category', 'points_offered', 'merchant__city']
    
    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'merchant_profile'):
            return MerchantDeal.objects.none()
        
        # Get deals from other merchants only with remaining points
        queryset = MerchantDeal.objects.filter(
            status='active',
            merchant__user__is_active=True,
            points_remaining__gt=0  # Only show deals with remaining points
        ).exclude(
            merchant=user.merchant_profile
        )
        
        # Apply additional filters
        min_points = self.request.query_params.get('min_points')
        max_points = self.request.query_params.get('max_points')
        
        if min_points:
            queryset = queryset.filter(points_offered__gte=min_points)
        
        if max_points:
            queryset = queryset.filter(points_offered__lte=max_points)
        
        return queryset.order_by('-create_time')
    
    @action(detail=False, methods=['get'])
    def by_points(self, request):
        """Get deals filtered by specific point range"""
        points = request.query_params.get('points')
        if not points:
            return Response({'error': 'Points parameter is required'}, status=400)
        
        try:
            points = float(points)
            queryset = self.get_queryset().filter(
                points_offered__lte=points,
                points_remaining__gte=points
            )
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response({'error': 'Invalid points value'}, status=400)


class MerchantDealRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for merchant deal requests
    """
    serializer_class = MerchantDealRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ['status', 'deal__category', 'points_requested']
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'merchant_profile'):
            return MerchantDealRequest.objects.filter(requesting_merchant=user.merchant_profile)
        return MerchantDealRequest.objects.none()
    
    def perform_create(self, serializer):
        request_obj = serializer.save(requesting_merchant=self.request.user.merchant_profile)
        
        # Send notification to deal creator
        MerchantNotification.objects.create(
            merchant=request_obj.deal.merchant,
            notification_type='deal_request',
            title='New Deal Request!',
            message=f'{request_obj.requesting_merchant.business_name} requested your deal "{request_obj.deal.title}"',
            deal=request_obj.deal,
            action_url=f'/merchant/deal-requests/{request_obj.id}/'
        )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a deal request"""
        deal_request = self.get_object()
        user = request.user.merchant_profile
        
        # Only deal creator can accept
        if deal_request.deal.merchant != user:
            return Response({'error': 'Only deal creator can accept requests'}, status=403)
        
        if deal_request.status != 'pending':
            return Response({'error': 'Request is not pending'}, status=400)
        
        # Create deal confirmation
        confirmation = MerchantDealConfirmation.objects.create(
            deal_request=deal_request,
            deal=deal_request.deal,
            merchant1=deal_request.deal.merchant,
            merchant2=deal_request.requesting_merchant,
            points_exchanged=deal_request.points_requested,
            status='confirmed',
            confirmation_time=timezone.now()
        )
        
        # Update deal points
        deal = deal_request.deal
        deal.points_used += deal_request.points_requested
        deal.save()
        
        # Update request status
        deal_request.status = 'accepted'
        deal_request.save()
        
        # Send notification to requester
        MerchantNotification.objects.create(
            merchant=deal_request.requesting_merchant,
            notification_type='deal_accepted',
            title='Deal Request Accepted!',
            message=f'{deal_request.deal.merchant.business_name} accepted your deal request',
            deal=deal_request.deal,
            action_url=f'/merchant/deal-confirmations/{confirmation.id}/'
        )
        
        return Response({'message': 'Deal request accepted successfully'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a deal request"""
        deal_request = self.get_object()
        user = request.user.merchant_profile
        
        # Only deal creator can reject
        if deal_request.deal.merchant != user:
            return Response({'error': 'Only deal creator can reject requests'}, status=403)
        
        if deal_request.status != 'pending':
            return Response({'error': 'Request is not pending'}, status=400)
        
        deal_request.status = 'rejected'
        deal_request.save()
        
        # Send notification to requester
        MerchantNotification.objects.create(
            merchant=deal_request.requesting_merchant,
            notification_type='deal_rejected',
            title='Deal Request Rejected',
            message=f'{deal_request.deal.merchant.business_name} rejected your deal request',
            deal=deal_request.deal
        )
        
        return Response({'message': 'Deal request rejected successfully'})


class MerchantDealConfirmationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing merchant deal confirmations
    """
    serializer_class = MerchantDealConfirmationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ['status', 'points_exchanged']
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'merchant_profile'):
            return MerchantDealConfirmation.objects.filter(
                Q(merchant1=user.merchant_profile) | Q(merchant2=user.merchant_profile)
            )
        return MerchantDealConfirmation.objects.none()
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a deal and transfer points"""
        confirmation = self.get_object()
        user = request.user.merchant_profile
        
        if confirmation.status == 'confirmed' and (confirmation.merchant1 == user or confirmation.merchant2 == user):
            # Create points transfer
            transfer = MerchantPointsTransfer.objects.create(
                confirmation=confirmation,
                from_merchant=confirmation.merchant1,
                to_merchant=confirmation.merchant2,
                points_amount=confirmation.points_exchanged,
                transfer_fee=Decimal('0.00'),  # No fees for now
                net_amount=confirmation.points_exchanged,
                transaction_id=f"TRF_{uuid.uuid4().hex[:8].upper()}"
            )
            
            # Complete the transfer
            if transfer.complete_transfer():
                confirmation.complete_deal()
                
                # Create deal point usage record
                DealPointUsage.objects.create(
                    deal=confirmation.deal,
                    confirmation=confirmation,
                    from_merchant=confirmation.merchant1,
                    to_merchant=confirmation.merchant2,
                    usage_type='exchange',
                    points_used=confirmation.points_exchanged,
                    usage_description=f"Point exchange between {confirmation.merchant1.business_name} and {confirmation.merchant2.business_name}"
                )
                
                # Send notifications
                MerchantNotification.objects.create(
                    merchant=confirmation.merchant1,
                    notification_type='points_transfer',
                    title='Points Transfer Completed',
                    message=f'{confirmation.points_exchanged} points transferred to {confirmation.merchant2.business_name}',
                    deal=confirmation.deal
                )
                
                MerchantNotification.objects.create(
                    merchant=confirmation.merchant2,
                    notification_type='points_transfer',
                    title='Points Received',
                    message=f'You received {confirmation.points_exchanged} points from {confirmation.merchant1.business_name}',
                    deal=confirmation.deal
                )
                
                return Response({'message': 'Deal completed and points transferred successfully'})
            else:
                return Response({'error': 'Points transfer failed'}, status=500)
        else:
            return Response({'error': 'Cannot complete this deal'}, status=400)
    
    @action(detail=True, methods=['get'])
    def usage_history(self, request, pk=None):
        """Get deal point usage history"""
        confirmation = self.get_object()
        usages = DealPointUsage.objects.filter(confirmation=confirmation)
        serializer = DealPointUsageSerializer(usages, many=True, context={'request': request})
        return Response(serializer.data)


class MerchantNotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for merchant notifications
    """
    serializer_class = MerchantNotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'merchant_profile'):
            return MerchantNotification.objects.filter(merchant=user.merchant_profile)
        return MerchantNotification.objects.none()
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        user = request.user.merchant_profile
        MerchantNotification.objects.filter(
            merchant=user,
            is_read=False
        ).update(is_read=True, read_time=timezone.now())
        return Response({'message': 'All notifications marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        user = request.user.merchant_profile
        count = MerchantNotification.objects.filter(
            merchant=user,
            is_read=False
        ).count()
        return Response({'unread_count': count})


class DealStatsViewSet(viewsets.ViewSet):
    """
    ViewSet for deal statistics
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get overall deal statistics"""
        user = request.user
        if not hasattr(user, 'merchant_profile'):
            return Response({'error': 'Merchant profile not found'}, status=404)
        
        merchant_profile = user.merchant_profile
        
        # Calculate statistics
        total_deals = MerchantDeal.objects.filter(merchant=merchant_profile).count()
        active_deals = MerchantDeal.objects.filter(merchant=merchant_profile, status='active').count()
        total_requests = MerchantDealRequest.objects.filter(
            Q(deal__merchant=merchant_profile) | Q(requesting_merchant=merchant_profile)
        ).count()
        successful_deals = MerchantDealConfirmation.objects.filter(
            Q(merchant1=merchant_profile) | Q(merchant2=merchant_profile),
            status='completed'
        ).count()
        
        # Calculate total points offered and used
        total_points_offered = MerchantDeal.objects.filter(
            merchant=merchant_profile
        ).aggregate(total=Sum('points_offered'))['total'] or Decimal('0.00')
        
        total_points_used = MerchantDeal.objects.filter(
            merchant=merchant_profile
        ).aggregate(total=Sum('points_used'))['total'] or Decimal('0.00')
        
        data = {
            'total_deals': total_deals,
            'active_deals': active_deals,
            'total_requests': total_requests,
            'successful_deals': successful_deals,
            'total_points_offered': total_points_offered,
            'total_points_used': total_points_used
        }
        
        serializer = DealStatsSerializer(data)
        return Response(serializer.data)