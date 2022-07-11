# Create your views here.
# -*- coding: UTF-8 -*-
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Song_list.views import is_ajax
# allPay setting.
from .Opay import Opay
from .models import OpayOrder

import logging

"""
    Example of Django view using OPay.
"""


def donate(request):
    return render(request, 'test/test.html')


@csrf_exempt
def create_payment(request):
    # Initialize the OPay config.
    if is_ajax(request=request):
        amount = request.POST.get('amount')
        sponsor = request.POST.get('sponsor')
        message = request.POST.get('message')
        "回傳post資訊"
        op = Opay({'TotalAmount': amount,
                   'ItemName': '破破的贊助費',
                   'TradeDesc': '給予實況主暖心照顧',
                   })
        dict_url = op.check_out()
        create_order = OpayOrder.objects.create(
            Sponsor=sponsor,
            Message=message,
            MerchantTradeNo=dict_url['MerchantTradeNo'],
            MerchantTradeDate=dict_url['MerchantTradeDate'],
            TotalAmount=dict_url['TotalAmount'],
            TradeDesc=dict_url['TradeDesc'],
            ItemName=dict_url['ItemName'],
            CheckMacValue=dict_url['CheckMacValue'])
        create_order.save()
        return JsonResponse({'data': dict_url})
    context = {
        'url': Opay.service_url,
    }
    return render(request, 'html/opay/opay_create_order.html', context)


@csrf_exempt
def get_ReturnURL(request):
    return render(request, 'test/test.html')


@csrf_exempt
def get_feedback(request):
    """
    Feedback from allpay after the customer paid.
    :param request:
    :return:
    """
    req_post = request.POST
    response = Opay.checkout_feedback(req_post)
    RtnMsg = response['RtnMsg']
    if response:
        if response['RtnCode'] == '1':
            paymentTypeDict = {
                'WebATM_TAISHIN': 'WebATM_台新銀行',
                'WebATM_SHINKONG': 'WebATM_新光銀行',
                'WebATM_FIRST': 'WebATM_第一銀行',
                'WebATM_MEGA': 'WebATM_兆豐銀行',
                'ATM_TAISHIN': 'ATM_台新銀行',
                'ATM_ESUN': 'ATM_玉山銀行',
                'ATM_FIRST': 'ATM_第一銀行',
                'ATM_CHINATRUST': 'ATM_中國信託銀行',
                'CVS_CVS': '超商繳款',
                'CVS_OK': 'OK超商繳款',
                'CVS_FAMILY': '全家超商繳款',
                'CVS_HILIFE': '萊爾富超商繳款',
                'CVS_IBON': '7-11超商繳款',
                'Credit': '信用卡',
                'TopUpUsed_AllPay': '歐付寶帳戶',
            }
            """ response 參數化 """
            MerchantTradeNo = response['MerchantTradeNo']
            TradeAmt = response['TradeAmt']
            PayAmt = response['PayAmt']
            PaymentType = response['PaymentType']
            context = {
                'MerchantTradeNo': MerchantTradeNo,
                'TradeAmt': TradeAmt,
                'PayAmt': PayAmt,
                'PaymentType': paymentTypeDict[PaymentType],
            }
            return render(request, 'html/opay/opay_order_success.html', context)
        else:
            return HttpResponse(RtnMsg)
    else:
        return HttpResponse(RtnMsg)
