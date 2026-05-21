import hashlib
import requests
import json
from datetime import datetime
from typing import Optional

# KHQR Configuration
KHQR_GATEWAY_URL = "https://khqr.cc/api/payment/request"
KHQR_PROFILE_ID = "cIPtKKpjYdQDbp17mLOoYlUgPqExna9G"
KHQR_SECRET_KEY = "ly5yujCeIZ906ERbc57a3nWJpr4ddOsi"  # ប្តូរទៅជា Secret Key របស់អ្នក
KHQR_PROFILE_KEY = "ly5yujCeIZ906ERbc57a3nWJpr4ddOsi"  # ប្តូរទៅជា Profile Key របស់អ្នក
KHQR_VERIFY_URL = "https://khqr.cc/api/cIPtKKpjYdQDbp17mLOoYlUgPqExna9G/payment-gateway/v1/payments/check-trans"

def generate_khqr_payment_url(transaction_id: str, amount: float, success_url: str, remark: str = "") -> str:
    """
    Generate KHQR payment redirect URL
    """
    # Create hash
    raw_string = KHQR_SECRET_KEY + transaction_id + str(amount) + success_url + remark
    payment_hash = hashlib.sha1(raw_string.encode()).hexdigest()
    
    # Build payment URL
    payment_data = {
        "transaction_id": transaction_id,
        "amount": amount,
        "success_url": success_url,
        "remark": remark,
        "hash": payment_hash
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in payment_data.items()])
    payment_url = f"{KHQR_GATEWAY_URL}/{KHQR_PROFILE_ID}?{query_string}"
    
    return payment_url

def verify_khqr_payment(transaction_id: str) -> dict:
    """
    Verify payment status with KHQR gateway
    """
    # Create hash
    hash_string = hashlib.sha1((KHQR_PROFILE_KEY + transaction_id).encode()).hexdigest()
    
    # Send verification request
    post_data = {
        "transaction_id": transaction_id,
        "hash": hash_string
    }
    
    try:
        response = requests.post(KHQR_VERIFY_URL, data=post_data, timeout=30)
        result = response.json()
        
        # Check if payment is successful
        is_paid = (
            result.get('responseCode') == 0 and
            result.get('data', {}).get('status', '').lower() == 'success'
        )
        
        return {
            "success": is_paid,
            "data": result.get('data', {}),
            "response_code": result.get('responseCode'),
            "response_message": result.get('responseMessage')
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }