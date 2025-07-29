from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from freelancing.utils.permissions import IsAPIKEYAuthenticated
from django.db import transaction
import json
import requests
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from freelancing.voucher.models import Voucher, WhatsAppContact, Advertisement
from freelancing.voucher.serializers import VoucherCreateSerializer, WhatsAppContactSerializer, GiftCardShareSerializer, AdvertisementSerializer
from rest_framework.filters import SearchFilter

class VoucherViewSet(viewsets.ModelViewSet):
    queryset = Voucher.objects.all()
    serializer_class = VoucherCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAPIKEYAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ["title", "message", "merchant__business_name"]
    ordering = ["-create_time"]
    filterset_fields = ["voucher_type", "is_gift_card"]
    def get_queryset(self):
        # Only show merchant's own vouchers
        return Voucher.objects.filter(merchant__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="redeem", permission_classes=[permissions.AllowAny,
                                                                IsAPIKEYAuthenticated])
    def redeem_voucher(self, request, pk=None):
        """Redeem a voucher - increases redemption count"""
        try:
            voucher = self.get_object()
           
            with transaction.atomic():
                # Check if voucher has a limit and if it's been reached
                if voucher.count and voucher.redemption_count >= voucher.count:
                    return Response(
                        {"error": "Voucher redemption limit reached"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
               
                # Increment redemption count
                voucher.redemption_count += 1
                voucher.save(update_fields=['redemption_count'])
               
                return Response({
                    "message": "Voucher redeemed successfully",
                    "redemption_count": voucher.redemption_count,
                    "remaining": voucher.count - voucher.redemption_count if voucher.count else None
                })
               
        except Voucher.DoesNotExist:
            return Response(
                {"error": "Voucher not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Failed to redeem voucher"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="share-gift-card", permission_classes=[permissions.AllowAny,
                                                                IsAPIKEYAuthenticated])
    def share_gift_card(self, request, pk=None):
        """Share gift card via WhatsApp"""
        try:
            voucher = self.get_object()
           
            # Check if it's a gift card
            if not voucher.is_gift_card:
                return Response(
                    {"error": "Only gift cards can be shared"},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            serializer = GiftCardShareSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
           
            phone_numbers = serializer.validated_data.get('phone_numbers', [])
           
            # Get user's WhatsApp contacts
            user_contacts = WhatsAppContact.objects.filter(
                user=request.user,
                phone_number__in=phone_numbers,
                is_on_whatsapp=True
            )
           
            if not user_contacts.exists():
                return Response(
                    {"error": "No valid WhatsApp contacts found"},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            # Send gift card via WhatsApp API
            success_count = 0
            failed_numbers = []
           
            for contact in user_contacts:
                try:
                    # WhatsApp API call (you'll need to implement this based on your WhatsApp provider)
                    success = self.send_whatsapp_gift_card(contact.phone_number, voucher)
                    if success:
                        success_count += 1
                    else:
                        failed_numbers.append(contact.phone_number)
                except Exception as e:
                    failed_numbers.append(contact.phone_number)
           
            return Response({
                "message": f"Gift card shared to {success_count} contacts",
                "success_count": success_count,
                "failed_numbers": failed_numbers
            })
           
        except Voucher.DoesNotExist:
            return Response(
                {"error": "Gift card not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Failed to share gift card"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_whatsapp_gift_card(self, phone_number, voucher):
        """Send gift card via WhatsApp API"""
        # This is a placeholder - implement based on your WhatsApp provider
        # Example: Twilio, MessageBird, etc.
        
        message = f"""
                🎁 *Gift Card from {voucher.merchant.business_name}*

                *{voucher.title}*

                {voucher.message}

                💰 *Value*: {self.get_voucher_value(voucher)}
                📅 *Valid Until*: Unlimited
                🎯 *Terms*: {voucher.terms_conditions[:100]}...

                Use this gift card at {voucher.merchant.business_name}!
        """
       
        # Implement your WhatsApp API call here
        # Example with a generic API:
        try:
            # api_url = "https://your-whatsapp-api.com/send"
            # payload = {
            #     "phone": phone_number,
            #     "message": message,
            #     "type": "text"
            # }
            # response = requests.post(api_url, json=payload)
            # return response.status_code == 200
           
            # For now, return True as placeholder
            return True
        except Exception:
            return False

    def get_voucher_value(self, voucher):
        """Get voucher value based on type"""
        if voucher.voucher_type.name == 'percentage':
            return f"{voucher.percentage_value}% off"
        elif voucher.voucher_type.name == 'flat':
            return f"₹{voucher.flat_amount} off"
        elif voucher.voucher_type.name == 'product':
            return f"Free {voucher.product_name}"
        return "Special offer"

    @action(detail=False, methods=["get"], url_path="popular", permission_classes=[permissions.AllowAny,
                                                                IsAPIKEYAuthenticated])
    def popular_vouchers(self, request):
        try:
            # Fixed: Use redemption_count instead of count for filtering
            top_vouchers = Voucher.objects.filter(
                redemption_count__gt=0,
                is_gift_card=False  # Exclude gift cards from public listing
            ).order_by("-redemption_count")[:10]
           
            data = [{
                "id": v.id,
                "title": v.title,
                "merchant": v.merchant.business_name,
                "redemption_count": v.redemption_count,
                "voucher_type": v.voucher_type.name
            } for v in top_vouchers]
           
            return Response(data)
        except Exception as e:
            return Response(
                {"error": "Failed to fetch popular vouchers"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # @action(detail=False, methods=["get"], url_path="gift-cards",permission_classes=[permissions.AllowAny,
    #                                                             IsAPIKEYAuthenticated])
    # def gift_cards(self, request):
    #     """Get user's gift cards"""
    #     try:
    #         gift_cards = Voucher.objects.filter(
    #             merchant__user=request.user,
    #             is_gift_card=True
    #         ).order_by('-create_time')
           
    #         data = [{
    #             "id": v.id,
    #             "title": v.title,
    #             "message": v.message,
    #             "value": self.get_voucher_value(v),
    #             "created_at": v.create_time
    #         } for v in gift_cards]
           
    #         return Response(data)
    #     except Exception as e:
    #         return Response(
    #             {"error": "Failed to fetch gift cards"},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )


class WhatsAppContactViewSet(viewsets.ModelViewSet):
    """Manage WhatsApp contacts for gift card sharing"""
    queryset = WhatsAppContact.objects.all()
    serializer_class = WhatsAppContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WhatsAppContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="sync-contacts")
    def sync_contacts(self, request):
        """Sync user's phone contacts and check WhatsApp status"""
        try:
            contacts_data = request.data.get('contacts', [])
           
            if not contacts_data:
                return Response(
                    {"error": "No contacts provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            # Clear existing contacts for this user
            WhatsAppContact.objects.filter(user=request.user).delete()
           
            # Create new contacts
            created_contacts = []
            for contact in contacts_data:
                name = contact.get('name', '')
                phone_number = contact.get('phone_number', '')
               
                if phone_number:
                    # Check if contact is on WhatsApp (implement your WhatsApp API check here)
                    is_on_whatsapp = self.check_whatsapp_status(phone_number)
                   
                    contact_obj = WhatsAppContact.objects.create(
                        user=request.user,
                        name=name,
                        phone_number=phone_number,
                        is_on_whatsapp=is_on_whatsapp
                    )
                    created_contacts.append(contact_obj)
           
            # Return only WhatsApp contacts
            whatsapp_contacts = WhatsAppContact.objects.filter(
                user=request.user,
                is_on_whatsapp=True
            )
           
            serializer = self.get_serializer(whatsapp_contacts, many=True)
           
            return Response({
                "message": f"Synced {len(created_contacts)} contacts, {len(whatsapp_contacts)} on WhatsApp",
                "whatsapp_contacts": serializer.data
            })
           
        except Exception as e:
            return Response(
                {"error": "Failed to sync contacts"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def check_whatsapp_status(self, phone_number):
        """Check if a phone number is registered on WhatsApp"""
        # This is a placeholder - implement based on your WhatsApp provider
        # Example: Use WhatsApp Business API to check number status
       
        try:
            # api_url = "https://your-whatsapp-api.com/check"
            # payload = {"phone": phone_number}
            # response = requests.post(api_url, json=payload)
            # return response.json().get('is_whatsapp', False)
           
            # For now, return True as placeholder (you should implement actual check)
            return True
        except Exception:
            return False

    @action(detail=False, methods=["get"], url_path="whatsapp-contacts")
    def whatsapp_contacts(self, request):
        """Get only WhatsApp contacts"""
        try:
            whatsapp_contacts = WhatsAppContact.objects.filter(
                user=request.user,
                is_on_whatsapp=True
            ).order_by('name')
           
            serializer = self.get_serializer(whatsapp_contacts, many=True)
            return Response(serializer.data)
           
        except Exception as e:
            return Response(
                {"error": "Failed to fetch WhatsApp contacts"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdvertisementViewSet(viewsets.ModelViewSet):
    """Manage voucher advertisements"""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show advertisements for user's vouchers
        return Advertisement.objects.filter(voucher__merchant__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the voucher belongs to the current user
        voucher = serializer.validated_data.get('voucher')
        if voucher.merchant.user != self.request.user:
            raise ValidationError("You can only create advertisements for your own vouchers")
        serializer.save()

    @action(detail=False, methods=["get"], url_path="active")
    def active_advertisements(self, request):
        """Get active advertisements"""
        try:
            current_date = timezone.now().date()
            active_ads = Advertisement.objects.filter(
                start_date__lte=current_date,
                end_date__gte=current_date,
                is_active=True
            ).order_by('-create_time')
           
            serializer = self.get_serializer(active_ads, many=True)
            return Response(serializer.data)
           
        except Exception as e:
            return Response(
                {"error": "Failed to fetch active advertisements"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="by-location")
    def advertisements_by_location(self, request):
        """Get advertisements by city and state"""
        try:
            city = request.query_params.get('city')
            state = request.query_params.get('state')
           
            if not city or not state:
                return Response(
                    {"error": "City and state parameters are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            current_date = timezone.now().date()
            location_ads = Advertisement.objects.filter(
                city__iexact=city,
                state__iexact=state,
                start_date__lte=current_date,
                end_date__gte=current_date,
                is_active=True
            ).order_by('-create_time')
           
            serializer = self.get_serializer(location_ads, many=True)
            return Response(serializer.data)
           
        except Exception as e:
            return Response(
                {"error": "Failed to fetch advertisements by location"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

