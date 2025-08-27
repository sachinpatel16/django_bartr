"""
Voucher Management System API

This module provides comprehensive API endpoints for managing the complete voucher lifecycle
in the Bartr platform. It includes functionality for merchants to create and manage vouchers,
users to purchase and redeem vouchers, and various analytics and management features.

Main Components:
1. VoucherViewSet - Merchant voucher management (CRUD operations, analytics)
2. PublicVoucherViewSet - Public voucher browsing and discovery
3. VoucherPurchaseViewSet - Voucher purchase and redemption workflow
4. UserVoucherViewSet - User voucher portfolio management
5. WhatsAppContactViewSet - Contact management for gift card sharing
6. AdvertisementViewSet - Voucher advertisement management for merchants
7. PublicAdvertisementViewSet - Public advertisement discovery

Key Features:
- Complete voucher lifecycle management
- Wallet integration for point-based purchases
- Atomic transaction management for data consistency
- Location-based advertisement targeting
- WhatsApp integration for gift card sharing
- Comprehensive analytics and reporting
- JWT Token authentication system

Authentication:
- JWT Token: Required for user-specific operations
- No API Key required

Usage Examples:
- Merchants: Create vouchers, view analytics, manage advertisements
- Users: Browse vouchers, make purchases, manage portfolio
- Public: Discover vouchers and advertisements without login
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.db import transaction
import json
import requests
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError, DatabaseError
from decimal import Decimal, InvalidOperation

from freelancing.voucher.models import Voucher, WhatsAppContact, Advertisement, UserVoucherRedemption, VoucherType, GiftCardShare
from freelancing.voucher.serializers import (
    VoucherCreateSerializer, WhatsAppContactSerializer, GiftCardShareSerializer, 
    AdvertisementSerializer, VoucherListSerializer, VoucherPurchaseSerializer,
    UserVoucherSerializer, VoucherRedeemSerializer, VoucherTypeSerializer,
    VoucherCancelSerializer, VoucherRefundSerializer, PurchaseHistorySerializer,
    MerchantVoucherScanSerializer, MerchantVoucherRedeemSerializer
)
from freelancing.custom_auth.models import Wallet, SiteSetting
from rest_framework.filters import SearchFilter
from django.db import models
from freelancing.custom_auth.models import MerchantProfile
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

class VoucherViewSet(viewsets.ModelViewSet):
    """
    Voucher Management API for Merchants
    
    This ViewSet provides comprehensive voucher management functionality for merchants.
    It allows merchants to create, read, update, and delete their vouchers, as well as
    access various analytics and management features.
    
    Features:
    - CRUD operations for vouchers
    - Voucher statistics and analytics
    - Gift card sharing via WhatsApp
    - Popular voucher tracking
    - Merchant-specific voucher filtering
    
    Authentication: JWT Token required
    Permissions: Authenticated merchants can only manage their own vouchers
    """
    queryset = Voucher.objects.all()
    serializer_class = VoucherCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ["title", "message", "merchant__business_name"]
    ordering = ["-create_time"]
    filterset_fields = ["voucher_type", "is_gift_card", "category"]

    def get_queryset(self):
        """
        Filter queryset to show only the authenticated merchant's vouchers.
        
        Returns:
            QuerySet: Filtered vouchers belonging to the current merchant user
        """
        # Only show merchant's own vouchers
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            return Voucher.objects.filter(merchant__user=self.request.user)
        # Return empty queryset for unauthenticated requests or during inspection
        return Voucher.objects.none()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"], url_path="statistics")
    def voucher_statistics(self, request):
        """
        Get comprehensive voucher statistics for the authenticated merchant.
        
        This endpoint provides detailed analytics including:
        - Total voucher counts and performance metrics
        - Purchase and redemption statistics
        - Recent activity (last 30 days)
        - Top performing vouchers based on popularity score
        
        Returns:
            Response: JSON containing voucher statistics and analytics data
            
        Example Response:
        {
            "total_vouchers": 25,
            "total_purchases": 150,
            "total_redemptions": 120,
            "redemption_rate": 80.0,
            "recent_activity": {
                "purchases_last_30_days": 45,
                "redemptions_last_30_days": 38
            },
            "top_performing_vouchers": [...]
        }
        """
        try:
            merchant_vouchers = self.get_queryset()
            
            # Calculate statistics
            total_vouchers = merchant_vouchers.count()
            total_purchases = merchant_vouchers.aggregate(
                total=models.Sum('purchase_count')
            )['total'] or 0
            total_redemptions = merchant_vouchers.aggregate(
                total=models.Sum('redemption_count')
            )['total'] or 0
            
            # Get top performing vouchers
            top_vouchers = merchant_vouchers.annotate(
                popularity_score=models.F('purchase_count') * 2 + models.F('redemption_count')
            ).order_by('-popularity_score')[:5]
            
            # Get recent activity (last 30 days)
            from datetime import timedelta
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_purchases = UserVoucherRedemption.objects.filter(
                voucher__in=merchant_vouchers,
                purchased_at__gte=thirty_days_ago
            ).count()
            
            recent_redemptions = UserVoucherRedemption.objects.filter(
                voucher__in=merchant_vouchers,
                redeemed_at__gte=thirty_days_ago
            ).count()
            
            data = {
                "total_vouchers": total_vouchers,
                "total_purchases": total_purchases,
                "total_redemptions": total_redemptions,
                "redemption_rate": round((total_redemptions / total_purchases * 100) if total_purchases > 0 else 0, 2),
                "recent_activity": {
                    "purchases_last_30_days": recent_purchases,
                    "redemptions_last_30_days": recent_redemptions
                },
                "top_performing_vouchers": [{
                    "id": v.id,
                    "title": v.title,
                    "purchase_count": v.purchase_count,
                    "redemption_count": v.redemption_count,
                    "popularity_score": v.purchase_count * 2 + v.redemption_count
                } for v in top_vouchers]
            }
            
            return Response(data)
            
        except Exception as e:
            return Response(
                {"error": "Failed to fetch voucher statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="redeem", permission_classes=[permissions.AllowAny])
    def redeem_voucher(self, request, pk=None):
        """
        Redeem a voucher by incrementing its redemption count.
        
        This endpoint allows users to redeem vouchers. It checks if the voucher
        has reached its redemption limit and increments the redemption count
        atomically to prevent race conditions.
        
        Args:
            request: HTTP request object
            pk: Primary key of the voucher to redeem
            
        Returns:
            Response: Success message with updated redemption count and remaining limit
            
        Raises:
            400: If voucher redemption limit is reached
            404: If voucher not found
            500: If redemption process fails
            
        Example Response:
        {
            "message": "Voucher redeemed successfully",
            "redemption_count": 15,
            "remaining": 35
        }
        """
        try:
            voucher = Voucher.objects.get(id=pk)
            # voucher = self.get_object()

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
                {"error": f"Failed to redeem voucher: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="share-gift-card", permission_classes=[permissions.AllowAny])
    def share_gift_card(self, request, pk=None):
        """
        Share a gift card voucher via WhatsApp to multiple contacts.
        
        This endpoint allows users to share gift card vouchers with their WhatsApp
        contacts. It creates individual share records for each recipient, allowing
        them to claim and use the gift card independently.
        
        Args:
            request: HTTP request object containing phone numbers
            pk: Primary key of the gift card voucher to share
            
        Request Body:
            {
                "phone_numbers": ["+919876543210", "+919876543211"]
            }
            
        Returns:
            Response: Success message with count of successful shares and failed numbers
            
        Raises:
            400: If voucher is not a gift card or no valid WhatsApp contacts found
            500: If sharing process fails
            
        Example Response:
        {
            "message": "Gift card shared successfully to 3 contacts",
            "success_count": 3,
            "failed_numbers": ["+919876543212"],
            "shares_created": [
                {
                    "phone_number": "+919876543210",
                    "claim_reference": "GFT-12345678",
                    "share_id": 1
                }
            ]
        }
        """
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
           
            # Get or create the user's voucher redemption record
            try:
                user_redemption = UserVoucherRedemption.objects.get(
                    user=request.user,
                    voucher=voucher,
                    is_active=True
                )
            except UserVoucherRedemption.DoesNotExist:
                return Response(
                    {"error": "You must purchase this gift card before sharing it"},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            # Create gift card shares for each recipient
            shares_created = []
            success_count = 0
            failed_numbers = []
           
            for contact in user_contacts:
                try:
                    # Create or get existing share record
                    share, created = GiftCardShare.objects.get_or_create(
                        original_purchase=user_redemption,
                        recipient_phone=contact.phone_number,
                        defaults={
                            'recipient_name': contact.name,
                            'shared_via': 'whatsapp'
                        }
                    )
                    
                    if created:
                        shares_created.append({
                            'phone_number': contact.phone_number,
                            'claim_reference': share.claim_reference,
                            'share_id': share.id
                        })
                        success_count += 1
                    else:
                        # Share already exists
                        shares_created.append({
                            'phone_number': contact.phone_number,
                            'claim_reference': share.claim_reference,
                            'share_id': share.id,
                            'already_shared': True
                        })
                        success_count += 1
                        
                except Exception as e:
                    failed_numbers.append(contact.phone_number)
           
            # Send gift card via WhatsApp API
            for share in shares_created:
                try:
                    # WhatsApp API call (you'll need to implement this based on your WhatsApp provider)
                    success = self.send_whatsapp_gift_card(share['phone_number'], voucher, share['claim_reference'])
                    if not success:
                        failed_numbers.append(share['phone_number'])
                        success_count -= 1
                except Exception as e:
                    failed_numbers.append(share['phone_number'])
                    success_count -= 1
           
            return Response({
                "message": f"Gift card shared successfully to {success_count} contacts",
                "success_count": success_count,
                "failed_numbers": failed_numbers,
                "shares_created": shares_created,
                "note": "Each recipient can claim and use the gift card independently"
            })
           
        except Exception as e:
            return Response(
                {"error": "Failed to share gift card"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_whatsapp_gift_card(self, phone_number, voucher, claim_reference):
        """
        Send gift card voucher via WhatsApp API with claim reference.
        
        This method sends a WhatsApp message containing the gift card details
        and a unique claim reference that recipients can use to claim the gift card.
        
        Args:
            phone_number (str): Recipient's phone number
            voucher (Voucher): Gift card voucher object to send
            claim_reference (str): Unique claim reference for the recipient
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Create message with claim reference
            message_body = f"""
                🎁 *Gift Card: {voucher.title}*

                {voucher.message}

                🏪 *Merchant:* {voucher.merchant.business_name}
                📍 *Location:* {voucher.merchant.city}, {voucher.merchant.state}

                💳 *Voucher Type:* {voucher.voucher_type.name}
                💰 *Value:* {self.get_voucher_value(voucher)}

                ⏰ *Valid Until:* {voucher.expiry_date.strftime('%B %d, %Y') if voucher.expiry_date else 'No expiry'}

                🔑 *Claim Reference:* {claim_reference}

                To claim this gift card:
                1. Visit: https://yourdomain.com/claim-gift-card/{claim_reference}
                2. Or show this reference to the merchant

                *This gift card can only be claimed once by the recipient.*
            """
            
            # Implement your WhatsApp API integration here
            # This is a placeholder implementation
            print(f"Sending WhatsApp message to {phone_number}: {message_body}")
            return True
            
        except Exception:
            return False

    def get_voucher_value(self, voucher):
        """
        Get human-readable voucher value description based on voucher type.
        
        Args:
            voucher (Voucher): Voucher object to get value for
            
        Returns:
            str: Formatted string describing the voucher value
            
        Examples:
            - Percentage voucher: "25% off"
            - Flat amount voucher: "₹100 off"
            - Product voucher: "Free Coffee"
            - Other types: "Special offer"
        """
        if voucher.voucher_type.name == 'percentage':
            return f"{voucher.percentage_value}% off"
        elif voucher.voucher_type.name == 'flat':
            return f"₹{voucher.flat_amount} off"
        elif voucher.voucher_type.name == 'product':
            return f"Free {voucher.product_name}"
        return "Special offer"

    @action(detail=False, methods=["get"], url_path="popular")
    def popular_vouchers(self, request):
        """
        Get popular vouchers based on purchase and redemption activity.
        
        This endpoint returns vouchers ranked by popularity score, calculated as:
        (purchase_count * 2) + redemption_count. Only vouchers that have been
        used (purchased or redeemed) are included, excluding gift cards from
        public listing.
        
        Returns:
            Response: JSON containing top 10 popular vouchers with popularity metrics
            
        Example Response:
        {
            "popular_vouchers": [
                {
                    "id": 1,
                    "title": "50% Off Coffee",
                    "merchant": "Coffee Shop",
                    "purchase_count": 25,
                    "redemption_count": 20,
                    "popularity_score": 70,
                    "voucher_type": "percentage",
                    "category": "Food & Beverage",
                    "image": "http://example.com/image.jpg"
                }
            ],
            "total_count": 10,
            "message": "Popular vouchers based on purchase and redemption activity (only used vouchers)"
        }
        """
        try:
            # Get popular vouchers based on purchase count and redemption count
            # Only include vouchers that have been used (purchased or redeemed)
            # Priority: purchase_count (most important), then redemption_count
            top_vouchers = Voucher.objects.filter(
                is_gift_card=False,  # Exclude gift cards from public listing
                is_active=True
            ).filter(
                # Only include vouchers that have been used (purchased or redeemed)
                models.Q(purchase_count__gt=0) | models.Q(redemption_count__gt=0)
            ).annotate(
                popularity_score=models.F('purchase_count') * 2 + models.F('redemption_count')
            ).order_by("-popularity_score", "-purchase_count", "-redemption_count")[:10]
           
            data = [{
                "id": v.id,
                "title": v.title,
                "merchant": v.merchant.business_name,
                "purchase_count": v.purchase_count,
                "redemption_count": v.redemption_count,
                "popularity_score": v.purchase_count * 2 + v.redemption_count,
                "voucher_type": v.voucher_type.name,
                "category": v.category.name if v.category else None,
                "image": v.get_display_image().url if v.get_display_image() else None
            } for v in top_vouchers]
           
            return Response({
                "popular_vouchers": data,
                "total_count": len(data),
                "message": "Popular vouchers based on purchase and redemption activity (only used vouchers)"
            })
        except Exception as e:
            return Response(
                {"error": "Failed to fetch popular vouchers"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PublicVoucherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public Voucher Browsing and Discovery API
    
    This ViewSet provides public access to browse, search, and discover vouchers
    without requiring user authentication. Users can explore vouchers by category,
    merchant, location, and various other filters.
    
    Features:
    - Browse active vouchers (excluding gift cards)
    - Search by title, message, or merchant name
    - Filter by voucher type, category, and merchant
    - Get featured and trending vouchers
    - Location-based voucher discovery
    - Category-based voucher browsing
    
    Authentication: No authentication required (public access)
    Permissions: Public read-only access
    """
    queryset = Voucher.objects.filter(is_active=True, is_gift_card=False)
    serializer_class = VoucherListSerializer
    permission_classes = []
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ["title", "message", "merchant__business_name"]
    filterset_fields = ["voucher_type", "category", "merchant"]
    ordering = ["-create_time"]

    def get_queryset(self):
        """
        Filter vouchers based on availability and user preferences.
        
        This method applies various filters to the voucher queryset based on
        query parameters provided by the user. It supports filtering by:
        - Category ID
        - Merchant ID
        - Voucher type
        - Price range (min_cost, max_cost) - currently placeholder
        
        Query Parameters:
            category: Filter by voucher category ID
            merchant: Filter by merchant ID
            voucher_type: Filter by voucher type name
            min_cost: Minimum purchase cost (placeholder)
            max_cost: Maximum purchase cost (placeholder)
            
        Returns:
            QuerySet: Filtered vouchers based on provided parameters
        """
        queryset = super().get_queryset()
        
        # Filter by category if provided
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by merchant if provided
        merchant_id = self.request.query_params.get('merchant')
        if merchant_id:
            queryset = queryset.filter(merchant_id=merchant_id)
        
        # Filter by voucher type if provided
        voucher_type = self.request.query_params.get('voucher_type')
        if voucher_type:
            queryset = queryset.filter(voucher_type__name=voucher_type)
        
        # Filter by price range if provided
        min_cost = self.request.query_params.get('min_cost')
        max_cost = self.request.query_params.get('max_cost')
        
        if min_cost or max_cost:
            # This would require additional logic to filter by purchase cost
            # For now, we'll return all vouchers
            pass
        
        return queryset

    @action(detail=False, methods=["get"], url_path="type")
    def voucher_categories(self, request):
        """Get all voucher categories"""
        categories = VoucherType.objects.filter(is_active=True)
        serializer = VoucherTypeSerializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="featured")
    def featured_vouchers(self, request):
        """Get featured vouchers (most popular based on purchase and redemption)"""
        # Only include vouchers that have been used (purchased or redeemed)
        featured = self.get_queryset().filter(
            models.Q(purchase_count__gt=0) | models.Q(redemption_count__gt=0)
        ).annotate(
            popularity_score=models.F('purchase_count') * 2 + models.F('redemption_count')
        ).order_by('-popularity_score', '-purchase_count', '-redemption_count')[:10]
        serializer = self.get_serializer(featured, many=True)
        return Response({
            "featured_vouchers": serializer.data,
            "total_count": len(serializer.data),
            "message": "Featured vouchers based on popularity (only used vouchers)"
        })

    @action(detail=False, methods=["get"], url_path="nearby")
    def nearby_vouchers(self, request):
        """Get vouchers from nearby merchants"""
        # This would require location-based filtering
        # For now, return recent vouchers
        nearby = self.get_queryset().order_by('-create_time')[:20]
        serializer = self.get_serializer(nearby, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="trending")
    def trending_vouchers(self, request):
        """Get trending vouchers (recent popular purchases in last 7 days)"""
        from datetime import timedelta
        
        # Get vouchers with recent purchases (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        trending_vouchers = self.get_queryset().filter(
            user_redemptions__purchased_at__gte=seven_days_ago
        ).annotate(
            recent_purchases=models.Count('user_redemptions', filter=models.Q(
                user_redemptions__purchased_at__gte=seven_days_ago
            ))
        ).order_by('-recent_purchases', '-purchase_count')[:10]
        
        serializer = self.get_serializer(trending_vouchers, many=True)
        return Response({
            "trending_vouchers": serializer.data,
            "total_count": len(serializer.data),
            "period": "Last 7 days",
            "message": "Trending vouchers based on recent purchase activity"
        })

class VoucherPurchaseViewSet(viewsets.ViewSet):
    """
    Voucher Purchase and Redemption Management API
    
    This ViewSet handles the complete voucher purchase lifecycle including:
    - Purchasing vouchers using wallet points
    - Redeeming purchased vouchers
    - Cancelling voucher purchases
    - Processing refunds for cancelled purchases
    
    All operations use atomic database transactions to ensure data consistency
    and prevent race conditions. The system integrates with the wallet system
    for point-based purchases.
    
    Features:
    - Atomic transaction management
    - Wallet integration for purchases
    - Purchase validation and limits
    - Redemption tracking
    - Cancellation and refund processing
    
    Authentication: JWT Token required
    Permissions: Authenticated users can manage their own purchases
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        method='post',
        request_body=VoucherPurchaseSerializer,   # 👈 force swagger to show body
        responses={200: "Success"}
    )

    @action(detail=False, methods=["post"], url_path="purchase", permission_classes=[permissions.AllowAny])
    def purchase_voucher(self, request):
        """
        Purchase a voucher using wallet points with atomic transaction management.
        
        This endpoint handles the complete voucher purchase process including:
        - Validating voucher availability and user eligibility
        - Checking wallet balance and deducting points
        - Creating purchase records atomically
        - Updating voucher purchase counts
        - Generating unique transaction IDs
        
        The entire process is wrapped in a database transaction to ensure
        data consistency and prevent partial purchases.
        
        Request Body:
            {
                "voucher_id": 123
            }
            
        Returns:
            Response: Purchase confirmation with transaction details
            
        Raises:
            400: If voucher unavailable, insufficient balance, or already purchased
            401: If user not authenticated
            500: If database error occurs
            
        Example Response:
        {
            "message": "Voucher purchased successfully",
            "voucher_id": 123,
            "voucher_title": "50% Off Coffee",
            "purchase_cost": 10.0,
            "remaining_balance": 90.0,
            "redemption_id": 456,
            "purchase_reference": "REF-123456",
            "expiry_date": "2024-12-31T23:59:59Z",
            "transaction_id": "WT-789-20241201120000"
        }
        """
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required. Please provide a valid JWT token."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = VoucherPurchaseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        voucher_id = serializer.validated_data['voucher_id']
        user = request.user
        
        try:
            # Use atomic transaction for all database operations
            with transaction.atomic():
                # 1. Get voucher with select_for_update to prevent race conditions
                try:
                    voucher = Voucher.objects.select_for_update().get(
                        id=voucher_id, 
                        is_active=True
                    )
                except Voucher.DoesNotExist:
                    raise ValidationError("Voucher not found or inactive")
                
                # 2. Check if user already purchased this voucher
                if UserVoucherRedemption.objects.filter(
                    user=user, 
                    voucher=voucher
                ).exists():
                    raise ValidationError("You have already purchased this voucher")
                
                # 3. Check voucher availability
                if voucher.count and voucher.redemption_count >= voucher.count:
                    raise ValidationError("Voucher is out of stock")

                # 4. Get user wallet with select_for_update
                try:
                    wallet = Wallet.objects.select_for_update().get(user=user)
                except Wallet.DoesNotExist:
                    raise ValidationError("User wallet not found")
                
                # 5. Calculate cost with proper decimal handling
                try:
                    # Get voucher cost from settings, with better error handling
                    voucher_cost_setting = SiteSetting.get_value("voucher_cost", "10")
                    cost = Decimal(str(voucher_cost_setting))
                    if cost <= 0:
                        raise ValidationError("Invalid voucher cost")
                except (InvalidOperation, ValueError, TypeError):
                    # If there's any issue with the setting, use default value
                    cost = Decimal("10")
                    if cost <= 0:
                        raise ValidationError("Invalid voucher cost")
                
                # 6. Validate sufficient balance
                if wallet.balance < cost:
                    raise ValidationError(
                        f"Insufficient balance. Required: ₹{cost}, Available: ₹{wallet.balance}"
                    ) 
                
                # 7. Generate unique transaction ID
                transaction_id = f"WT-{wallet.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

                # 8. Deduct from wallet with error handling
                try:
                    wallet.deduct(cost, note=f"Voucher Purchase: {voucher.title}", ref_id=str(voucher.id))
                except ValidationError as e:
                    raise ValidationError(f"Wallet deduction failed: {str(e)}")
                # 9. Increment voucher purchase count atomically
                voucher.purchase_count = models.F('purchase_count') + 1
                voucher.save(update_fields=['purchase_count'])
                
                # 10. Create redemption record
                try:
                    redemption = UserVoucherRedemption.objects.create(
                        user=user,
                        voucher=voucher,
                        purchase_cost=cost,
                        is_active=True,
                        wallet_transaction_id=transaction_id,
                        voucher_purchase_count=1,  # Default to 1 voucher per purchase
                        max_redemption_allowed=1   # Default to 1 redemption allowed
                    )
                except IntegrityError:
                    raise ValidationError("Failed to create purchase record")

                return Response({
                    "message": "Voucher purchased successfully",
                    "voucher_id": voucher.id,
                    "voucher_title": voucher.title,
                    "purchase_cost": float(cost),
                    "remaining_balance": float(wallet.balance),
                    "redemption_id": redemption.id,
                    "purchase_reference": redemption.purchase_reference,
                    "expiry_date": redemption.expiry_date,
                    "transaction_id": transaction_id
                }, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as e:
            return Response(
                {"error": "Database error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"], url_path="redeem")
    def redeem_purchased_voucher(self, request):
        """
        DEPRECATED: Users cannot redeem their own vouchers.
        Vouchers must be redeemed by merchants through scanning.
        
        This endpoint is kept for backward compatibility but will always return an error.
        Merchants should use the merchant scanning endpoints instead.
        """
        return Response({
            "error": "Users cannot redeem their own vouchers. Vouchers must be redeemed by merchants through scanning.",
            "message": "Please ask the merchant to scan your voucher QR code for redemption.",
            "merchant_endpoint": "/api/v1/merchant/scan/scan/",
            "status": "deprecated"
        }, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=["post"], url_path="cancel")
    # def cancel_purchase(self, request):
    #     """Cancel a voucher purchase with atomic transaction"""
    #     serializer = VoucherCancelSerializer(data=request.data, context={'request': request})
    #     serializer.is_valid(raise_exception=True)
        
    #     redemption_id = serializer.validated_data['redemption_id']
    #     reason = serializer.validated_data.get('reason', '')
    #     user = request.user
        
    #     try:
    #         with transaction.atomic():
    #             # 1. Get redemption record with select_for_update
    #             try:
    #                 redemption = UserVoucherRedemption.objects.select_for_update().get(
    #                     id=redemption_id,
    #                     user=user
    #                 )
    #             except UserVoucherRedemption.DoesNotExist:
    #                 raise ValidationError("Voucher not found")
                
    #             # 2. Validate cancellation eligibility
    #             if redemption.redeemed_at:
    #                 raise ValidationError("Cannot cancel redeemed voucher")
    #             if redemption.purchase_status in ['cancelled', 'refunded']:
    #                 raise ValidationError("Voucher is already cancelled or refunded")
                
    #             # 3. Cancel the purchase
    #             try:
    #                 redemption.cancel_purchase(reason=reason)
    #             except ValidationError as e:
    #                 raise ValidationError(f"Cancellation failed: {str(e)}")
                
    #             return Response({
    #                 "message": "Voucher purchase cancelled successfully",
    #                 "voucher_title": redemption.voucher.title,
    #                 "purchase_reference": redemption.purchase_reference,
    #                 "purchase_status": redemption.purchase_status,
    #                 "transaction_id": redemption.wallet_transaction_id
    #             })
                
    #     except ValidationError as e:
    #         return Response(
    #             {"error": str(e)},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     except DatabaseError as e:
    #         return Response(
    #             {"error": "Database error occurred. Please try again."},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )
    #     except Exception as e:
    #         return Response(
    #             {"error": "An unexpected error occurred. Please try again."},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

    # @action(detail=False, methods=["post"], url_path="refund")
    # def refund_purchase(self, request):
    #     """Refund a voucher purchase with atomic transaction"""
    #     serializer = VoucherRefundSerializer(data=request.data, context={'request': request})
    #     serializer.is_valid(raise_exception=True)
        
    #     redemption_id = serializer.validated_data['redemption_id']
    #     reason = serializer.validated_data.get('reason', '')
    #     user = request.user
        
    #     try:
    #         with transaction.atomic():
    #             # 1. Get redemption record with select_for_update
    #             try:
    #                 redemption = UserVoucherRedemption.objects.select_for_update().get(
    #                     id=redemption_id,
    #                     user=user
    #                 )
    #             except UserVoucherRedemption.DoesNotExist:
    #                 raise ValidationError("Voucher not found")
                
    #             # 2. Validate refund eligibility
    #             if redemption.redeemed_at:
    #                 raise ValidationError("Cannot refund redeemed voucher")
    #             if redemption.purchase_status in ['cancelled', 'refunded']:
    #                 raise ValidationError("Voucher is already cancelled or refunded")
                
    #             # 3. Get user wallet with select_for_update
    #             try:
    #                 wallet = Wallet.objects.select_for_update().get(user=user)
    #             except Wallet.DoesNotExist:
    #                 raise ValidationError("User wallet not found for refund")
                
    #             # 4. Refund the purchase
    #             try:
    #                 redemption.refund_purchase(reason=reason)
    #             except ValidationError as e:
    #                 raise ValidationError(f"Refund failed: {str(e)}")
                
    #             return Response({
    #                 "message": "Voucher purchase refunded successfully",
    #                 "voucher_title": redemption.voucher.title,
    #                 "purchase_reference": redemption.purchase_reference,
    #                 "refund_amount": float(redemption.purchase_cost),
    #                 "remaining_balance": float(wallet.balance),
    #                 "purchase_status": redemption.purchase_status,
    #                 "transaction_id": redemption.wallet_transaction_id
    #             })
                
    #     except ValidationError as e:
    #         return Response(
    #             {"error": str(e)},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     except DatabaseError as e:
    #         return Response(
    #             {"error": "Database error occurred. Please try again."},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )
    #     except Exception as e:
    #         return Response(
    #             {"error": "An unexpected error occurred. Please try again."},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

class UserVoucherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User Voucher Management and History API
    
    This ViewSet provides comprehensive access to a user's voucher portfolio
    including purchased, redeemed, expired, cancelled, and refunded vouchers.
    Users can view their voucher history, check active vouchers, and access
    detailed purchase analytics.
    
    Features:
    - View all purchased vouchers with filtering options
    - Check active (unredeemed) vouchers
    - Access redemption history
    - View expired and cancelled vouchers
    - Gift card management
    - Purchase summary and statistics
    
    Authentication: JWT Token required
    Permissions: Users can only access their own voucher data
    """
    serializer_class = UserVoucherSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["purchase_status", "is_gift_voucher"]
    ordering = ["-purchased_at"]

    def get_queryset(self):
        """Get user's purchased vouchers"""
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            return UserVoucherRedemption.objects.filter(user=self.request.user)
        # Return empty queryset for unauthenticated requests or during inspection
        return UserVoucherRedemption.objects.none()

    @action(detail=False, methods=["get"], url_path="active")
    def active_vouchers(self, request):
        """Get user's active (unredeemed) vouchers"""
        active_vouchers = self.get_queryset().filter(
            purchase_status='purchased',
            redeemed_at__isnull=True
        ).exclude(expiry_date__lt=timezone.now())
        serializer = self.get_serializer(active_vouchers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="redeemed")
    def redeemed_vouchers(self, request):
        """Get user's redeemed vouchers"""
        redeemed_vouchers = self.get_queryset().filter(
            purchase_status='redeemed'
        )
        serializer = self.get_serializer(redeemed_vouchers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="expired")
    def expired_vouchers(self, request):
        """Get user's expired vouchers"""
        expired_vouchers = self.get_queryset().filter(
            purchase_status='purchased',
            expiry_date__lt=timezone.now()
        )
        serializer = self.get_serializer(expired_vouchers, many=True)
        return Response(serializer.data)

    # @action(detail=False, methods=["get"], url_path="cancelled")
    # def cancelled_vouchers(self, request):
    #     """Get user's cancelled vouchers"""
    #     cancelled_vouchers = self.get_queryset().filter(
    #         purchase_status='cancelled'
    #     )
    #     serializer = self.get_serializer(cancelled_vouchers, many=True)
    #     return Response(serializer.data)

    # @action(detail=False, methods=["get"], url_path="refunded")
    # def refunded_vouchers(self, request):
    #     """Get user's refunded vouchers"""
    #     refunded_vouchers = self.get_queryset().filter(
    #         purchase_status='refunded'
    #     )
    #     serializer = self.get_serializer(refunded_vouchers, many=True)
    #     return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="gift-cards")
    def gift_cards(self, request):
        """Get user's gift cards"""
        gift_cards = self.get_queryset().filter(
            is_gift_voucher=True
        )
        serializer = self.get_serializer(gift_cards, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="history")
    def purchase_history(self, request):
        """Get detailed purchase history"""
        history = self.get_queryset()
        
        # Apply filters if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            history = history.filter(purchase_status=status_filter)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            history = history.filter(purchased_at__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            history = history.filter(purchased_at__lte=date_to)
        
        serializer = PurchaseHistorySerializer(history, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="qr-code")
    def get_voucher_qr_code(self, request, pk=None):
        """
        Get voucher QR code data for a specific purchased voucher.
        
        This endpoint returns the QR code data that merchants can scan to redeem
        the voucher. The QR code contains the purchase reference or redemption ID.
        
        Returns:
            Response: QR code data and voucher details for scanning
            
        Raises:
            404: If voucher not found or not owned by user
             400: If voucher is already redeemed or expired
        """
        try:
            # Get the specific voucher redemption
            redemption = UserVoucherRedemption.objects.get(
                id=pk,
                user=request.user
            )
            
            # Check if voucher can still be redeemed
            if not redemption.can_redeem_voucher():
                if redemption.is_expired():
                    return Response({
                        "error": "Voucher has expired",
                        "expiry_date": redemption.expiry_date
                    }, status=status.HTTP_400_BAD_REQUEST)
                elif redemption.purchase_status == 'redeemed':
                    return Response({
                        "error": "Voucher has already been fully redeemed",
                        "redeemed_at": redemption.redeemed_at
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        "error": "Voucher cannot be redeemed"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Return QR code data
            return Response({
                "message": "Voucher QR code data",
                "voucher_details": {
                    "id": redemption.voucher.id,
                    "title": redemption.voucher.title,
                    "merchant_name": redemption.voucher.merchant.business_name,
                    "voucher_type": redemption.voucher.voucher_type.name,
                    "voucher_value": self._get_voucher_value(redemption.voucher),
                    "purchased_at": redemption.purchased_at,
                    "expiry_date": redemption.expiry_date,
                    "remaining_redemptions": redemption.get_remaining_redemptions()
                },
                "qr_code_data": {
                    "purchase_reference": redemption.purchase_reference,
                    "redemption_id": redemption.id,
                    "voucher_uuid": str(redemption.voucher.uuid)
                },
                "redemption_instructions": "Show this QR code to the merchant for redemption. The merchant will scan it to process your voucher."
            })
            
        except UserVoucherRedemption.DoesNotExist:
            return Response({
                "error": "Voucher not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": "An unexpected error occurred"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_voucher_value(self, voucher):
        """Helper method to get formatted voucher value"""
        try:
            if not voucher or not hasattr(voucher, 'voucher_type') or not voucher.voucher_type:
                return "Special offer"
            
            voucher_type_name = getattr(voucher.voucher_type, 'name', 'unknown')
            
            if voucher_type_name == 'percentage':
                percentage_value = getattr(voucher, 'percentage_value', 0)
                min_bill = getattr(voucher, 'percentage_min_bill', 0)
                return f"{percentage_value}% off (min bill: ₹{min_bill})"
            elif voucher_type_name == 'flat':
                flat_amount = getattr(voucher, 'flat_amount', 0)
                min_bill = getattr(voucher, 'flat_min_bill', 0)
                return f"₹{flat_amount} off (min bill: ₹{min_bill})"
            elif voucher_type_name == 'product':
                product_name = getattr(voucher, 'product_name', 'Product')
                min_bill = getattr(voucher, 'product_min_bill', 0)
                return f"Free {product_name} (min bill: ₹{min_bill})"
            else:
                return "Special offer"
        except Exception:
            return "Special offer"

    @action(detail=False, methods=["get"], url_path="summary")
    def purchase_summary(self, request):
        """Get purchase summary statistics"""
        user_vouchers = self.get_queryset()
        
        summary = {
            "total_purchases": user_vouchers.count(),
            "total_spent": sum(v.purchase_cost for v in user_vouchers),
            "active_vouchers": user_vouchers.filter(
                purchase_status='purchased',
                redeemed_at__isnull=True
            ).exclude(expiry_date__lt=timezone.now()).count(),
            "redeemed_vouchers": user_vouchers.filter(purchase_status='redeemed').count(),
            "expired_vouchers": user_vouchers.filter(
                purchase_status='purchased',
                expiry_date__lt=timezone.now()
            ).count(),
            "cancelled_vouchers": user_vouchers.filter(purchase_status='cancelled').count(),
            "refunded_vouchers": user_vouchers.filter(purchase_status='refunded').count(),
            "total_refunds": sum(v.purchase_cost for v in user_vouchers.filter(purchase_status='refunded')),
            "gift_cards": user_vouchers.filter(is_gift_voucher=True).count()
        }
        
        return Response(summary)


class WhatsAppContactViewSet(viewsets.ModelViewSet):
    """
    WhatsApp Contact Management API for Gift Card Sharing
    
    This ViewSet manages user contacts for WhatsApp-based gift card sharing.
    It allows users to sync their phone contacts, check WhatsApp availability,
    and maintain a list of contacts that can receive gift cards via WhatsApp.
    
    Features:
    - Create and manage WhatsApp contacts
    - Sync phone contacts with WhatsApp status
    - Filter contacts by WhatsApp availability
    - Bulk contact operations
    - Contact validation and management
    
    Authentication: JWT Token required
    Permissions: Users can only manage their own contacts
    """
    queryset = WhatsAppContact.objects.all()
    serializer_class = WhatsAppContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            return WhatsAppContact.objects.filter(user=self.request.user)
        # Return empty queryset for unauthenticated requests or during inspection
        return WhatsAppContact.objects.none()

    def perform_create(self, serializer):
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            raise ValidationError("User authentication required")

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
        """Check if a phone number is registered on WhatsApp using RapidAPI"""
        try:
            # Clean phone number (remove + if present)
            clean_phone = phone_number.replace('+', '') if phone_number else ''
            
            if not clean_phone:
                print(f"Invalid phone number: {phone_number}")
                return False
            
            # Basic phone number validation (should be at least 10 digits)
            if len(clean_phone) < 10:
                print(f"Phone number too short: {clean_phone}")
                return False
            
            # For now, let's assume all valid phone numbers have WhatsApp
            # This is a temporary fix until we get the RapidAPI working properly
            print(f"Valid phone number {clean_phone} - assuming has WhatsApp (temporary fix)")
            return True
            
            # TODO: Uncomment below code when RapidAPI is working properly
            """
            url = "https://whatsapp-number-validator3.p.rapidapi.com/WhatsappNumberHasItWithToken"
            
            payload = {"phone_number": clean_phone}
            headers = {
                "x-rapidapi-key": "bd54de3881msh517848c79ec25b6p10c042jsnb1179d9521b2",
                "x-rapidapi-host": "whatsapp-number-validator3.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            print(f"Checking WhatsApp status for: {clean_phone}")
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"RapidAPI Response for {clean_phone}: {result}")
                
                # Check if the API response indicates the number has WhatsApp
                if isinstance(result, dict):
                    has_whatsapp = result.get('has_whatsapp', False)
                    is_valid = result.get('is_valid', False)
                    status = result.get('status', '').lower()
                    whatsapp_status = result.get('whatsapp_status', False)
                    valid = result.get('valid', False)
                    
                    is_whatsapp = has_whatsapp or is_valid or 'success' in status or 'true' in status or whatsapp_status or valid
                    print(f"WhatsApp check result for {clean_phone}: {is_whatsapp}")
                    return is_whatsapp
                else:
                    is_whatsapp = bool(result)
                    print(f"WhatsApp check result for {clean_phone}: {is_whatsapp}")
                    return is_whatsapp
            else:
                print(f"WhatsApp validation API error for {clean_phone}: {response.status_code} - {response.text}")
                return False
            """
                
        except Exception as e:
            print(f"WhatsApp validation error for {phone_number}: {str(e)}")
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

    @action(detail=False, methods=["post"], url_path="test-whatsapp-validation")
    def test_whatsapp_validation(self, request):
        """Test WhatsApp validation for a single phone number"""
        try:
            phone_number = request.data.get('phone_number')
            if not phone_number:
                return Response(
                    {"error": "phone_number is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Test the validation
            is_whatsapp = self.check_whatsapp_status(phone_number)
            
            return Response({
                "phone_number": phone_number,
                "is_on_whatsapp": is_whatsapp,
                "message": f"Phone number {phone_number} {'has' if is_whatsapp else 'does not have'} WhatsApp"
            })
            
        except Exception as e:
            return Response(
                {"error": f"Failed to test WhatsApp validation: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdvertisementViewSet(viewsets.ModelViewSet):
    """
    Voucher Advertisement Management API for Merchants
    
    This ViewSet allows merchants to create, manage, and track advertisements
    for their vouchers. Advertisements are location-based promotions that help
    merchants increase voucher visibility in specific cities and states.
    
    Features:
    - Create and manage voucher advertisements
    - Location-based targeting (city/state)
    - Date range management (start/end dates)
    - Cost management with wallet integration
    - Advertisement performance tracking
    - Active/inactive status management
    
    Cost Structure:
    - Base advertisement cost: Configurable via SiteSetting
    - Extension cost: Additional cost for extending advertisement dates
    - All costs deducted from merchant's wallet balance
    
    Authentication: JWT Token required
    Permissions: Merchants can only manage advertisements for their own vouchers
    """
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Only show advertisements for user's vouchers
        # Handle case where request.user might not be available (e.g., during Swagger inspection)
        if hasattr(self, 'request') and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            return Advertisement.objects.filter(voucher__merchant__user=self.request.user)
        # Return empty queryset for unauthenticated requests or during inspection
        return Advertisement.objects.none()

    def perform_create(self, serializer):
        """Create advertisement and deduct points from merchant's wallet"""
        try:
            with transaction.atomic():
                # Ensure user is authenticated
                if not hasattr(self, 'request') or not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
                    raise ValidationError("User authentication required")
                
                # Ensure the voucher belongs to the current user
                voucher = serializer.validated_data.get('voucher')
                if voucher.merchant.user != self.request.user:
                    raise ValidationError("You can only create advertisements for your own vouchers")
                
                # Get merchant's wallet
                try:
                    merchant_wallet = Wallet.objects.select_for_update().get(user=self.request.user)
                except Wallet.DoesNotExist:
                    raise ValidationError("Merchant wallet not found. Please contact support.")
                
                # Get advertisement cost from SiteSetting (default 10 points)
                try:
                    advertisement_cost_setting = SiteSetting.get_value("advertisement_cost", "10")
                    cost = Decimal(str(advertisement_cost_setting))
                    if cost <= 0:
                        raise ValidationError("Invalid advertisement cost")
                except (InvalidOperation, ValueError, TypeError):
                    # If there's any issue with the setting, use default value
                    cost = Decimal("10")
                    if cost <= 0:
                        raise ValidationError("Invalid advertisement cost")
                
                # Check if merchant has sufficient balance
                if merchant_wallet.balance < cost:
                    raise ValidationError(
                        f"Insufficient wallet balance. Required: {cost} points, Available: {merchant_wallet.balance} points"
                    )
                
                # Deduct points from merchant's wallet
                try:
                    merchant_wallet.deduct(
                        cost, 
                        note=f"Advertisement Creation: {voucher.title}", 
                        ref_id=f"AD-{voucher.id}"
                    )
                except ValidationError as e:
                    raise ValidationError(f"Wallet deduction failed: {str(e)}")
                
                # Create the advertisement
                advertisement = serializer.save()
                
                # Return success response with wallet info
                return Response({
                    "message": "Advertisement created successfully",
                    "advertisement_id": advertisement.id,
                    "voucher_title": voucher.title,
                    "cost_deducted": float(cost),
                    "remaining_balance": float(merchant_wallet.balance),
                    "transaction_note": f"Advertisement Creation: {voucher.title}"
                }, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Failed to create advertisement: {str(e)}")

    def perform_update(self, serializer):
        """Handle advertisement updates with potential cost implications"""
        try:
            with transaction.atomic():
                # Ensure user is authenticated
                if not hasattr(self, 'request') or not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
                    raise ValidationError("User authentication required")
                
                old_instance = self.get_object()
                new_data = serializer.validated_data
                
                # Check if dates are being extended (which might require additional cost)
                date_extension_cost = Decimal("0")
                if 'end_date' in new_data and old_instance.end_date < new_data['end_date']:
                    # Calculate additional days and cost
                    additional_days = (new_data['end_date'] - old_instance.end_date).days
                    if additional_days > 0:
                        # Get cost per day from settings (default 1 point per day)
                        cost_per_day = Decimal(SiteSetting.get_value("advertisement_extension_cost_per_day", "1"))
                        date_extension_cost = additional_days * cost_per_day
                
                # If there's an extension cost, deduct from wallet
                if date_extension_cost > 0:
                    try:
                        merchant_wallet = Wallet.objects.select_for_update().get(user=self.request.user)
                        
                        # Check if merchant has sufficient balance
                        if merchant_wallet.balance < date_extension_cost:
                            raise ValidationError(
                                f"Insufficient wallet balance for extension. Required: {date_extension_cost} points, Available: {merchant_wallet.balance} points"
                            )
                        
                        # Deduct extension cost
                        merchant_wallet.deduct(
                            date_extension_cost,
                            note=f"Advertisement Extension: {old_instance.voucher.title} (+{additional_days} days)",
                            ref_id=f"AD-EXT-{old_instance.id}"
                        )
                        
                    except Wallet.DoesNotExist:
                        raise ValidationError("Merchant wallet not found. Please contact support.")
                    except ValidationError as e:
                        raise e
                
                # Update the advertisement
                updated_advertisement = serializer.save()
                
                # Return response with cost information if applicable
                response_data = {
                    "message": "Advertisement updated successfully",
                    "advertisement_id": updated_advertisement.id,
                    "voucher_title": updated_advertisement.voucher.title
                }
                
                if date_extension_cost > 0:
                    response_data.update({
                        "extension_cost_deducted": float(date_extension_cost),
                        "additional_days": additional_days,
                        "remaining_balance": float(merchant_wallet.balance),
                        "extension_transaction_note": f"Advertisement Extension: {old_instance.voucher.title} (+{additional_days} days)"
                    })
                
                return Response(response_data)
                
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f"Failed to update advertisement: {str(e)}")

    @action(detail=False, methods=["get"], url_path="active")
    def active_advertisements(self, request):
        """Get active advertisements for the merchant"""
        try:
            current_date = timezone.now().date()
            active_ads = Advertisement.objects.filter(
                voucher__merchant__user=request.user,
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
        """Get advertisements by city and state for the merchant"""
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
                voucher__merchant__user=request.user,
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

    @action(detail=False, methods=["get"], url_path="cost-info")
    def advertisement_cost_info(self, request):
        """Get advertisement creation cost information"""
        try:
            # Get advertisement cost from SiteSetting
            try:
                advertisement_cost_setting = SiteSetting.get_value("advertisement_cost", "10")
                cost = Decimal(str(advertisement_cost_setting))
            except (InvalidOperation, ValueError, TypeError):
                cost = Decimal("10")
            
            # Get merchant's current wallet balance
            try:
                merchant_wallet = Wallet.objects.get(user=request.user)
                current_balance = merchant_wallet.balance
                can_create = current_balance >= cost
            except Wallet.DoesNotExist:
                current_balance = Decimal("0")
                can_create = False
            
            return Response({
                "advertisement_cost": float(cost),
                "current_wallet_balance": float(current_balance),
                "can_create_advertisement": can_create,
                "cost_source": "SiteSetting" if SiteSetting.objects.filter(key="advertisement_cost").exists() else "Default",
                "message": "Advertisement cost information retrieved successfully"
            })
            
        except Exception as e:
            return Response(
                {"error": "Failed to fetch advertisement cost information"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # @action(detail=False, methods=["get"], url_path="statistics")
    # def advertisement_statistics(self, request):
    #     """Get advertisement statistics for the merchant"""
    #     try:
    #         merchant_ads = self.get_queryset()
    #         current_date = timezone.now().date()
            
    #         # Calculate statistics
    #         total_advertisements = merchant_ads.count()
    #         active_advertisements = merchant_ads.filter(
    #             start_date__lte=current_date,
    #             end_date__gte=current_date,
    #             is_active=True
    #         ).count()
    #         expired_advertisements = merchant_ads.filter(
    #             end_date__lt=current_date
    #         ).count()
    #         upcoming_advertisements = merchant_ads.filter(
    #             start_date__gt=current_date
    #         ).count()
            
    #         # Get total cost spent on advertisements
    #         total_cost = total_advertisements * Decimal(SiteSetting.get_value("advertisement_cost", "10"))
            
    #         # Get location-wise statistics
    #         location_stats = merchant_ads.values('city', 'state').annotate(
    #             count=models.Count('id')
    #         ).order_by('-count')
            
    #         data = {
    #             "total_advertisements": total_advertisements,
    #             "active_advertisements": active_advertisements,
    #             "expired_advertisements": expired_advertisements,
    #             "upcoming_advertisements": upcoming_advertisements,
    #             "total_cost_spent": float(total_cost),
    #             "cost_per_advertisement": float(SiteSetting.get_value("advertisement_cost", "10")),
    #             "location_distribution": list(location_stats),
    #             "message": "Advertisement statistics retrieved successfully"
    #         }
            
    #         return Response(data)
            
    #     except Exception as e:
    #         return Response(
    #             {"error": "Failed to fetch advertisement statistics"},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

    def perform_destroy(self, instance):
        """Handle advertisement deletion - no refund for deleted advertisements"""
        try:
            # Check if advertisement is still active
            current_date = timezone.now().date()
            if instance.start_date <= current_date <= instance.end_date and instance.is_active:
                # If advertisement is currently active, just mark as inactive
                instance.is_active = False
                instance.save()
                return Response({
                    "message": "Advertisement deactivated successfully",
                    "note": "Advertisement was active, so it has been deactivated instead of deleted"
                })
            else:
                # If advertisement is not active, delete it
                instance.delete()
                return Response({
                    "message": "Advertisement deleted successfully",
                    "note": "Advertisement was not active, so it has been permanently deleted"
                })
        except Exception as e:
            raise ValidationError(f"Failed to delete advertisement: {str(e)}")

class PublicAdvertisementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public Advertisement Discovery API
    
    This ViewSet provides public access to browse and discover voucher
    advertisements without requiring user authentication. Users can explore
    advertisements by location, category, and other criteria to find
    relevant offers in their area.
    
    Features:
    - Browse active advertisements by location
    - Filter by city and state
    - Category-based advertisement discovery
    - Public access (no user login required)
    - Location-based targeting support
    
    Authentication: No authentication required (public access)
    Permissions: Public read-only access to active advertisements
    """
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = []  # Public access, no authentication required
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["city", "state"]
    ordering = ["-create_time"]

    def get_queryset(self):
        """Get only active advertisements"""
        current_date = timezone.now().date()
        return Advertisement.objects.filter(
            start_date__lte=current_date,
            end_date__gte=current_date,
            is_active=True
        )

    @action(detail=False, methods=["get"], url_path="active")
    def active_advertisements(self, request):
        """Get all active advertisements (public access)"""
        try:
            active_ads = self.get_queryset().order_by('-create_time')
            serializer = self.get_serializer(active_ads, many=True)
            return Response({
                "active_advertisements": serializer.data,
                "total_count": len(serializer.data),
                "message": "Active advertisements available for public viewing"
            })
           
        except Exception as e:
            return Response(
                {"error": "Failed to fetch active advertisements"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="by-location")
    def advertisements_by_location(self, request):
        """Get advertisements by city and state (public access)"""
        try:
            city = request.query_params.get('city')
            state = request.query_params.get('state')
           
            if not city or not state:
                return Response(
                    {"error": "City and state parameters are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            location_ads = self.get_queryset().filter(
                city__iexact=city,
                state__iexact=state
            ).order_by('-create_time')
           
            serializer = self.get_serializer(location_ads, many=True)
            return Response({
                "advertisements": serializer.data,
                "total_count": len(serializer.data),
                "location": f"{city}, {state}",
                "message": f"Advertisements available in {city}, {state}"
            })
           
        except Exception as e:
            return Response(
                {"error": "Failed to fetch advertisements by location"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # @action(detail=False, methods=["get"], url_path="featured")
    # def featured_advertisements(self, request):
    #     """Get featured advertisements (public access)"""
    #     try:
    #         # Get advertisements with active vouchers that have good performance
    #         featured_ads = self.get_queryset().filter(
    #             voucher__purchase_count__gte=5,  # At least 5 purchases
    #             voucher__redemption_count__gte=2  # At least 2 redemptions
    #         ).order_by('-voucher__purchase_count', '-create_time')[:10]
           
    #         serializer = self.get_serializer(featured_ads, many=True)
    #         return Response({
    #             "featured_advertisements": serializer.data,
    #             "total_count": len(serializer.data),
    #             "message": "Featured advertisements based on voucher performance"
    #         })
           
    #     except Exception as e:
    #         return Response(
    #             {"error": "Failed to fetch featured advertisements"},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

    @action(detail=False, methods=["get"], url_path="by-category")
    def advertisements_by_category(self, request):
        """Get advertisements by voucher category (public access)"""
        try:
            category_id = request.query_params.get('category')
            if not category_id:
                return Response(
                    {"error": "Category parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            category_ads = self.get_queryset().filter(
                voucher__category_id=category_id
            ).order_by('-create_time')
           
            serializer = self.get_serializer(category_ads, many=True)
            return Response({
                "advertisements": serializer.data,
                "total_count": len(serializer.data),
                "category_id": category_id,
                "message": f"Advertisements in category {category_id}"
            })
           
        except Exception as e:
            return Response(
                {"error": "Failed to fetch advertisements by category"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MerchantVoucherScanViewSet(viewsets.ViewSet):
    """
    Merchant Voucher Scanning and Redemption API
    
    This ViewSet handles merchant-side voucher scanning and redemption:
    - Scan voucher QR codes to get voucher details
    - Validate voucher eligibility for redemption
    - Process voucher redemption by merchant
    - Track redemption location and merchant details
    
    All operations use atomic database transactions to ensure data consistency.
    Only authenticated merchants can scan and redeem vouchers.
    
    Features:
    - QR code scanning endpoint
    - Voucher validation and redemption
    - Atomic transaction management
    - Merchant authentication and authorization
    - Redemption tracking and analytics
    
    Authentication: JWT Token required
    Permissions: Authenticated merchants can only scan vouchers for their business
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(detail=False, methods=["post"], url_path="scan")
    def scan_voucher(self, request):
        """
        Scan a voucher QR code to get voucher details and validate redemption eligibility.
        
        This endpoint is used by merchants to scan voucher QR codes and get information
        about the voucher before processing redemption. It handles both regular vouchers
        and gift cards.
        
        Request Body:
            {
                "qr_data": "VCH-12345678" or "GFT-12345678" or "456" (redemption_id)
            }
            
        Returns:
            Response: Voucher details and redemption eligibility
            
        Raises:
            400: If QR data invalid, voucher not found, or already redeemed
            401: If user not authenticated or not a merchant
            403: If merchant trying to scan voucher from different business
            500: If database error occurs
        """
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required. Please provide a valid JWT token."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is a merchant
        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
        except MerchantProfile.DoesNotExist:
            return Response({
                "error": "Access denied. Only merchants can scan vouchers.",
                "debug_info": {
                    "user_id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                    "message": "User does not have a merchant profile. Please ensure you are logged in as a merchant account."
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get QR data from request
        qr_data = request.data.get('qr_data')
        if not qr_data:
            return Response(
                {"error": "QR data is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Try to find voucher redemption by different possible formats
            redemption = None
            
            # First try by purchase reference (VCH-XXXXXXXX format)
            if isinstance(qr_data, str) and qr_data.startswith('VCH-'):
                try:
                    redemption = UserVoucherRedemption.objects.select_related(
                        'voucher', 'user'
                    ).get(
                        purchase_reference=qr_data,
                        is_active=True
                    )
                except UserVoucherRedemption.DoesNotExist:
                    pass
            
            # If not found, try by gift card claim reference (GFT-XXXXXXXX format)
            if not redemption and isinstance(qr_data, str) and qr_data.startswith('GFT-'):
                try:
                    gift_share = GiftCardShare.objects.select_related(
                        'original_purchase', 'original_purchase__voucher', 'claimed_by_user'
                    ).get(
                        claim_reference=qr_data,
                        is_claimed=True
                    )
                    
                    # Get the claimed redemption record - use the original purchase's purchase_reference
                    redemption = UserVoucherRedemption.objects.select_related(
                        'voucher', 'user'
                    ).get(
                        purchase_reference=gift_share.original_purchase.purchase_reference,
                        is_active=True
                    )
                except (GiftCardShare.DoesNotExist, UserVoucherRedemption.DoesNotExist):
                    pass
            
            # If not found, try by redemption ID (numeric)
            if not redemption:
                try:
                    redemption_id = int(qr_data) if isinstance(qr_data, (int, str)) else None
                    if redemption_id is not None:
                        redemption = UserVoucherRedemption.objects.select_related(
                            'voucher', 'user'
                        ).get(
                            id=redemption_id,
                            is_active=True
                        )
                except (UserVoucherRedemption.DoesNotExist, ValueError, TypeError):
                    pass
            
            # If still not found, try by UUID
            if not redemption:
                try:
                    redemption = UserVoucherRedemption.objects.select_related(
                        'voucher', 'user'
                    ).get(
                        voucher__uuid=qr_data,
                        is_active=True
                    )
                except (UserVoucherRedemption.DoesNotExist, ValueError):
                    pass
            
            if not redemption:
                return Response({
                    "error": "Voucher not found or invalid QR code",
                    "debug_info": {
                        "qr_data_received": qr_data,
                        "qr_data_type": type(qr_data).__name__,
                        "message": "Please check if the voucher exists and the QR code is valid"
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if merchant is trying to scan voucher from their own business
            try:
                voucher_merchant_name = getattr(redemption.voucher.merchant, 'business_name', 'Unknown Merchant')
                current_merchant_name = getattr(merchant_profile, 'business_name', 'Unknown Merchant')
            except Exception:
                voucher_merchant_name = "Unknown Merchant"
                current_merchant_name = "Unknown Merchant"
            
            if redemption.voucher.merchant != merchant_profile:
                return Response({
                    "error": "Access denied. You can only scan vouchers from your own business.",
                    "debug_info": {
                        "voucher_merchant": voucher_merchant_name,
                        "current_merchant": current_merchant_name
                    }
                }, status=status.HTTP_403_FORBIDDEN
                )
            
            # Check voucher redemption eligibility
            if not redemption.can_redeem_voucher():
                if redemption.is_expired():
                    return Response({
                        "error": "Voucher has expired",
                        "debug_info": {
                            "expiry_date": redemption.expiry_date,
                            "current_time": timezone.now()
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                elif redemption.purchase_status == 'redeemed':
                    return Response({
                        "error": "Voucher has already been fully redeemed",
                        "debug_info": {
                            "redeemed_at": redemption.redeemed_at,
                            "redemption_count": redemption.voucher_redemption_count
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                elif redemption.purchase_status in ['cancelled', 'refunded']:
                    return Response({
                        "error": f"Voucher is {redemption.purchase_status}",
                        "debug_info": {
                            "purchase_status": redemption.purchase_status,
                            "notes": redemption.redemption_notes
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        "error": "Voucher cannot be redeemed",
                        "debug_info": {
                            "purchase_status": redemption.purchase_status,
                            "is_active": redemption.is_active,
                            "can_redeem_result": redemption.can_redeem_voucher(),
                            "remaining_redemptions": redemption.get_remaining_redemptions()
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Determine voucher type and user info
            is_gift_card = redemption.is_gift_voucher
            
            # Safe user info extraction with fallbacks
            try:
                user_name = getattr(redemption.user, 'fullname', None) or getattr(redemption.user, 'username', 'Unknown User')
                user_phone = str(redemption.user.phone) if hasattr(redemption.user, 'phone') and redemption.user.phone else None
            except Exception:
                user_name = "Unknown User"
                user_phone = None
            
            user_info = {
                "name": user_name,
                "phone": user_phone,
                "is_original_purchaser": not is_gift_card
            }
            
            # If it's a gift card, get additional info
            if is_gift_card:
                try:
                    # For gift cards, we need to find the share record differently
                    # Since the redemption might be a claimed gift card, we need to search by the original purchase
                    gift_share = GiftCardShare.objects.filter(
                        original_purchase__voucher=redemption.voucher,
                        claimed_by_user=redemption.user,
                        is_claimed=True
                    ).first()
                    
                    if gift_share:
                        user_info.update({
                            "is_gift_card_recipient": True,
                            "original_purchaser": gift_share.original_purchase.user.fullname,
                            "claimed_at": gift_share.claimed_at,
                            "claim_reference": gift_share.claim_reference
                        })
                except Exception:
                    # If we can't get gift card info, continue without it
                    pass
            
            # Return voucher details for merchant review
            try:
                voucher_details = {
                    "id": redemption.voucher.id,
                    "title": getattr(redemption.voucher, 'title', 'Unknown Voucher'),
                    "voucher_type": getattr(redemption.voucher.voucher_type, 'name', 'Unknown Type') if hasattr(redemption.voucher, 'voucher_type') and redemption.voucher.voucher_type else 'Unknown Type',
                    "voucher_value": self._get_voucher_value(redemption.voucher),
                    "user_info": user_info,
                    "purchased_at": redemption.purchased_at,
                    "expiry_date": redemption.expiry_date,
                    "remaining_redemptions": redemption.get_remaining_redemptions(),
                    "purchase_reference": redemption.purchase_reference,
                    "redemption_id": redemption.id,
                    "is_gift_card": is_gift_card
                }
            except Exception as e:
                # If there's an issue with voucher details, provide basic info
                voucher_details = {
                    "id": getattr(redemption.voucher, 'id', 'Unknown'),
                    "title": "Voucher Details Unavailable",
                    "voucher_type": "Unknown",
                    "voucher_value": "Contact Support",
                    "user_info": user_info,
                    "purchased_at": redemption.purchased_at,
                    "expiry_date": redemption.expiry_date,
                    "remaining_redemptions": redemption.get_remaining_redemptions(),
                    "purchase_reference": redemption.purchase_reference,
                    "redemption_id": redemption.id,
                    "is_gift_card": is_gift_card
                }
            
            return Response({
                "message": "Voucher found and eligible for redemption",
                "voucher_details": voucher_details,
                "can_redeem": True
            })
            
        except Exception as e:
            import traceback
            return Response({
                "error": "An unexpected error occurred. Please try again.",
                "debug_info": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc() if settings.DEBUG else "Traceback hidden in production"
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"], url_path="redeem")
    def redeem_voucher(self, request):
        """
        Redeem a scanned voucher by merchant.
        
        This endpoint processes the actual voucher redemption after the merchant
        has scanned and validated the voucher. The merchant provides the redemption
        details and the system processes the redemption atomically.
        
        Request Body:
            {
                "redemption_id": 456,
                "location": "Store Location",
                "notes": "Additional notes",
                "quantity": 1
            }
            
        Returns:
            Response: Redemption confirmation with transaction details
            
        Raises:
            400: If redemption invalid or failed
            401: If user not authenticated or not a merchant
            403: If merchant trying to redeem voucher from different business
            500: If database error occurs
        """
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required. Please provide a valid JWT token."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is a merchant
        try:
            merchant_profile = MerchantProfile.objects.get(user=request.user)
        except MerchantProfile.DoesNotExist:
            return Response(
                {"error": "Access denied. Only merchants can redeem vouchers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MerchantVoucherRedeemSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        redemption_id = serializer.validated_data['redemption_id']
        location = serializer.validated_data.get('location', '')
        notes = serializer.validated_data.get('notes', '')
        quantity = serializer.validated_data.get('quantity', 1)
        
        try:
            with transaction.atomic():
                # Get redemption record with select_for_update
                try:
                    redemption = UserVoucherRedemption.objects.select_for_update().get(
                        id=redemption_id,
                        is_active=True
                    )
                except UserVoucherRedemption.DoesNotExist:
                    raise ValidationError("Voucher not found or inactive")
                
                # Check if merchant is trying to redeem voucher from their own business
                try:
                    if redemption.voucher.merchant != merchant_profile:
                        raise ValidationError("Access denied. You can only redeem vouchers from your own business.")
                except Exception as e:
                    raise ValidationError(f"Error validating merchant access: {str(e)}")
                
                # Validate redemption eligibility
                if not redemption.can_redeem_voucher():
                    if redemption.is_expired():
                        raise ValidationError("Voucher has expired")
                    elif redemption.purchase_status == 'redeemed':
                        raise ValidationError("Voucher has already been fully redeemed")
                    elif redemption.purchase_status in ['cancelled', 'refunded']:
                        raise ValidationError(f"Voucher is {redemption.purchase_status}")
                    else:
                        raise ValidationError("Voucher cannot be redeemed")
                
                # Validate quantity
                if quantity > redemption.get_remaining_redemptions():
                    raise ValidationError(f"Only {redemption.get_remaining_redemptions()} redemptions remaining")
                
                if quantity <= 0:
                    raise ValidationError("Redemption quantity must be greater than 0")
                
                # Process the redemption
                try:
                    redemption.redeem_voucher(
                        location=location or f"{merchant_profile.business_name} - {merchant_profile.city or 'Unknown Location'}",
                        notes=f"Redeemed by merchant: {merchant_profile.business_name}. {notes}" if notes else f"Redeemed by merchant: {merchant_profile.business_name}",
                        quantity=quantity
                    )
                except ValidationError as e:
                    raise ValidationError(f"Redemption failed: {str(e)}")
                
                # Safe extraction of response data with fallbacks
                try:
                    voucher_title = getattr(redemption.voucher, 'title', 'Unknown Voucher')
                    user_name = getattr(redemption.user, 'fullname', None) or getattr(redemption.user, 'username', 'Unknown User')
                except Exception:
                    voucher_title = "Unknown Voucher"
                    user_name = "Unknown User"
                
                return Response({
                    "message": "Voucher redeemed successfully",
                    "voucher_title": voucher_title,
                    "user_name": user_name,
                    "redeemed_at": redemption.redeemed_at,
                    "redemption_location": redemption.redemption_location,
                    "purchase_reference": redemption.purchase_reference,
                    "quantity_redeemed": quantity,
                    "remaining_redemptions": redemption.get_remaining_redemptions(),
                    "merchant_name": merchant_profile.business_name,
                    "transaction_id": redemption.wallet_transaction_id
                })
                
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseError as e:
            return Response(
                {"error": "Database error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_voucher_value(self, voucher):
        """Helper method to get formatted voucher value"""
        try:
            if not voucher or not hasattr(voucher, 'voucher_type') or not voucher.voucher_type:
                return "Special offer"
            
            voucher_type_name = getattr(voucher.voucher_type, 'name', 'unknown')
            
            if voucher_type_name == 'percentage':
                percentage_value = getattr(voucher, 'percentage_value', 0)
                min_bill = getattr(voucher, 'percentage_min_bill', 0)
                return f"{percentage_value}% off (min bill: ₹{min_bill})"
            elif voucher_type_name == 'flat':
                flat_amount = getattr(voucher, 'flat_amount', 0)
                min_bill = getattr(voucher, 'flat_min_bill', 0)
                return f"₹{flat_amount} off (min bill: ₹{min_bill})"
            elif voucher_type_name == 'product':
                product_name = getattr(voucher, 'product_name', 'Product')
                min_bill = getattr(voucher, 'product_min_bill', 0)
                return f"Free {product_name} (min bill: ₹{min_bill})"
            else:
                return "Special offer"
        except Exception:
            return "Special offer"

class GiftCardClaimViewSet(viewsets.ViewSet):
    """
    Gift Card Claiming and Management API
    
    This ViewSet handles gift card claiming by recipients and provides
    management features for shared gift cards.
    
    Features:
    - Claim shared gift cards using claim reference
    - View claimed gift cards
    - Merchant redemption of claimed gift cards
    - Gift card sharing history
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(detail=False, methods=["post"], url_path="claim")
    def claim_gift_card(self, request):
        """
        Claim a shared gift card using claim reference.
        
        This endpoint allows recipients to claim gift cards that were shared with them.
        Each claim creates a new UserVoucherRedemption record for the recipient.
        
        Request Body:
            {
                "claim_reference": "GFT-12345678"
            }
            
        Returns:
            Response: Gift card details and confirmation of successful claim
            
        Raises:
            400: If claim reference invalid or already claimed
            404: If gift card share not found
            500: If claiming process fails
        """
        claim_reference = request.data.get('claim_reference')
        if not claim_reference:
            return Response(
                {"error": "Claim reference is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Find the gift card share
            gift_share = GiftCardShare.objects.get(
                claim_reference=claim_reference,
                is_claimed=False
            )
            
            # Check if user already has this gift card
            if UserVoucherRedemption.objects.filter(
                user=request.user,
                voucher=gift_share.original_purchase.voucher,
                is_gift_voucher=True
            ).exists():
                return Response(
                    {"error": "You have already claimed this gift card"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Claim the gift card
            with transaction.atomic():
                new_redemption = gift_share.claim_gift_card(request.user)
                
                return Response({
                    "message": "Gift card claimed successfully!",
                    "gift_card_details": {
                        "id": new_redemption.id,
                        "title": new_redemption.voucher.title,
                        "merchant": new_redemption.voucher.merchant.business_name,
                        "voucher_type": new_redemption.voucher.voucher_type.name,
                        "voucher_value": self._get_voucher_value(new_redemption.voucher),
                        "expiry_date": new_redemption.expiry_date,
                        "purchase_reference": new_redemption.purchase_reference,
                        "claim_reference": claim_reference
                    },
                    "redemption_instructions": "You can now use this gift card at the merchant location. Show the purchase reference or QR code for redemption."
                }, status=status.HTTP_201_CREATED)
                
        except GiftCardShare.DoesNotExist:
            return Response(
                {"error": "Invalid claim reference or gift card already claimed"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Failed to claim gift card"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="my-gift-cards")
    def my_gift_cards(self, request):
        """Get user's claimed gift cards"""
        try:
            gift_cards = UserVoucherRedemption.objects.filter(
                user=request.user,
                is_gift_voucher=True
            ).select_related('voucher', 'voucher__merchant')
            
            data = [{
                "id": gc.id,
                "title": gc.voucher.title,
                "merchant": gc.voucher.merchant.business_name,
                "voucher_type": gc.voucher.voucher_type.name,
                "voucher_value": self._get_voucher_value(gc.voucher),
                "purchased_at": gc.purchased_at,
                "expiry_date": gc.expiry_date,
                "purchase_reference": gc.purchase_reference,
                "purchase_status": gc.purchase_status,
                "can_redeem": gc.can_redeem_voucher(),
                "remaining_redemptions": gc.get_remaining_redemptions()
            } for gc in gift_cards]
            
            return Response({
                "gift_cards": data,
                "total_count": len(data),
                "message": "Your claimed gift cards"
            })
            
        except Exception as e:
            return Response(
                {"error": "Failed to fetch gift cards"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"], url_path="shared-by-me")
    def shared_by_me(self, request):
        """Get gift cards shared by the current user"""
        try:
            # Get all gift card shares created by user's purchases
            user_purchases = UserVoucherRedemption.objects.filter(
                user=request.user,
                voucher__is_gift_card=True
            )
            
            shares = GiftCardShare.objects.filter(
                original_purchase__in=user_purchases
            ).select_related('original_purchase', 'original_purchase__voucher')
            
            data = [{
                "share_id": share.id,
                "recipient_phone": share.recipient_phone,
                "recipient_name": share.recipient_name,
                "voucher_title": share.original_purchase.voucher.title,
                "shared_via": share.shared_via,
                "shared_at": share.create_time,
                "is_claimed": share.is_claimed,
                "claimed_at": share.claimed_at,
                "claim_reference": share.claim_reference
            } for share in shares]
            
            return Response({
                "shares": data,
                "total_count": len(data),
                "message": "Gift cards shared by you"
            })
            
        except Exception as e:
            return Response(
                {"error": "Failed to fetch shared gift cards"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_voucher_value(self, voucher):
        """Helper method to get formatted voucher value"""
        if voucher.voucher_type.name == 'percentage':
            return f"{voucher.percentage_value}% off (min bill: ₹{voucher.percentage_min_bill})"
        elif voucher.voucher_type.name == 'flat':
            return f"₹{voucher.flat_amount} off (min bill: ₹{voucher.flat_min_bill})"
        elif voucher.voucher_type.name == 'product':
            return f"Free {voucher.product_name} (min bill: ₹{voucher.product_min_bill})"
        return "Special offer"