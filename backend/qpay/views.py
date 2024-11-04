from django.shortcuts import render, redirect
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from time import time
from datetime import datetime
from revenues.models import Transactions
from devices.models import Device
from django.conf import settings
import json, hmac, hashlib, urllib.request, urllib, urllib.parse, random
import requests

# Create your views here.

# Global variable to store token and expiration time
token_data = {
    "access_token": None,
    "expires_at": None  # Store expiration timestamp
}

def get_access_token():
    # Check if token exists and hasn't expired
    if token_data["access_token"] and token_data["expires_at"] > time():
        return token_data["access_token"]

    # If token is missing or expired, request a new one
    auth_url = settings.QPAY_AUTH_URL
    auth_response = requests.post(
        url=auth_url,
        auth=(settings.QPAY_USERNAME, settings.QPAY_PASSWORD)
    )

    if auth_response.status_code == 200:
        auth_json = auth_response.json()
        token_data["access_token"] = auth_json.get("access_token")
        expires_in = auth_json.get("expires_in", 3600)  # Assume 1 hour if not provided
        token_data["expires_at"] = time() + expires_in
        return token_data["access_token"]
    else:
        raise Exception("Failed to authenticate with QPay")

class QPayAPI(APIView):
    def get(self, request, *args, **kwargs):

        # Generate unique transaction ID
        transID = random.randrange(1000000)

        # Create the order request data
        invoice_data = {
            "invoice_code": "TEST_INVOICE",  # Provided invoice code
            "sender_invoice_no": str(transID),
            "invoice_receiver_code": "terminal",
            "sender_branch_code": "BRANCH1",
            "invoice_description": f"Order #{transID} Payment",
            "amount": request.GET.get("amount"),
            "callback_url":f"{settings.DOMAIN_URL}/qpay/api/webhook?payment_id={str(transID)}"
        }

        # Send the authentication request to QPay
        try:
            access_token = get_access_token()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Send invoice creation request
        invoice_response = requests.post(
            url=settings.QPAY_INVO_URL,
            headers=headers,
            data=json.dumps(invoice_data),
        )

        if invoice_response.status_code == 200:
            result = invoice_response.json()
            
            return Response({
                    "order_code": transID,
                    "invoice_id": result.get("invoice_id"),
                    "qr_code": result.get("qr_text"),
                    "payment_url": result.get("invoice_url"),
                    "status": "success",
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to create invoice",
                "details": invoice_response.text
            }, status=invoice_response.status_code)
    
    def post(self, request, *args, **kwargs):
        order_code = request.GET.get("order")
        invoice_id = request.GET.get("invoice_id")

        if not order_code or not invoice_id:
            return Response({"error": "Missing info"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order request data
        invoice_data = {
            "object_type": "INVOICE",
            "object_id"  : invoice_id,
            "offset"     : {
                "page_number": 1,
                "page_limit" : 100
	        }
        }

        # Send the authentication request to QPay
        try:
            access_token = get_access_token()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Send invoice creation request
        invoice_response = requests.post(
            url=settings.QPAY_INVO_URL,
            headers=headers,
            data=json.dumps(invoice_data),
        )

        if invoice_response.status_code == 200:
            result = invoice_response.json()
            
            if result.get("rows"):
                if result["rows"][0]["payment_status"] == "PAID":
                    return Response({
                            "status": "PAID",
                            "amount": result["paid_amount"]
                        }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to request info",
                "details": invoice_response.text
            }, status=invoice_response.status_code)

        return Response({
            "status": "NOT PAID"
        }, status=status.HTTP_402_PAYMENT_REQUIRED)

class QPayUpdateAPI(APIView):
    def post(self, request, order_code, *args, **kwargs):
        # Process and update the status of the order
        order_status = request.data.get("status")
        if order_code:
            order = Order.objects.filter(order_code=order_code).first()
            if order:
                order.status = order_status
                order.save()
        return Response({
            "order_code": order_code,
            "status": order.status,
        }, status=status.HTTP_200_OK)

class QPayWebhookAPI(APIView):
    def get(self, request, *args, **kwargs):
        # Handle webhook notifications from QPay
        invoice_id = request.GET.get("payment_id")

        if not invoice_id:
            return Response({"error": "Missing info"}, status=status.HTTP_400_BAD_REQUEST)

        # Implement logic to check order status and update database
        order = Order.objects.filter(order_code=order_code).first()

        # Create the order request data
        invoice_data = {
            "object_type": "INVOICE",
            "object_id"  : invoice_id,
            "offset"     : {
                "page_number": 1,
                "page_limit" : 100
	        }
        }

        # Send the authentication request to QPay
        try:
            access_token = get_access_token()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Send invoice creation request
        invoice_response = requests.post(
            url=settings.QPAY_INVO_URL,
            headers=headers,
            data=json.dumps(invoice_data),
        )

        if invoice_response.status_code == 200:
            result = invoice_response.json()
            
            if result.get("rows"):
                if result["rows"][0]["payment_status"] == "PAID":
                    Transactions.objects.create(
                        order_id=order,
                        payment_id=Payment.objects.filter(code='qpay').first(),
                        amount=order.total_price,
                        transaction_status="Success",
                    )

            return Response({
                    "invoice_id": result.get["invoice_id"],
                    "qr_code": result.get("qr_text"),
                    "payment_url": result.get("invoice_url"),
                    "status": "success",
                    "order_id": order_code,
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to create invoice",
                "details": invoice_response.text
            }, status=invoice_response.status_code)

        return Response({
            "SUCCESS"
        }, status=status.HTTP_200_OK)