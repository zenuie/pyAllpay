# Create your views here.
# -*- coding: UTF-8 -*-
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# allPay setting.
from .Opay import Opay

import logging

"""
    Example of Django view using OPay.
"""

def donate(request):
    return render(request, 'test/test.html')

@csrf_exempt
def create_payment(request):
    # Initialize the OPay config.
    ap = Opay({'TotalAmount': 45})
    print(Opay.test_url)
    dict_url = ap.check_out()
    dict_value = dict_url.values()
    context = {
        'datas': zip(dict_url, dict_value),
        'test_url': Opay.test_url,
    }

    return render(request, 'test/test.html', context)


@csrf_exempt
def get_ReturnURL(request):
    print(request.body)
    return HttpResponse('')


@csrf_exempt
def get_feedback(request):
    """
    Feedback from allpay after the customer paid.
    :param request:
    :return:
    """
    print(request.body)
    req_post = request.POST

    returns = Opay.checkout_feedback(req_post)
    print(returns)
    logging.info(str(returns))
    if returns:
        if returns['RtnCode'] == '1':
            """
              payment is paid by customer.
            """
            # do your work here.
            return HttpResponse('1|OK')
        else:
            return HttpResponse('0|Bad Request')
    else:
        return HttpResponse('0|Bad Request')
