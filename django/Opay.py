import time
import datetime
import urllib
import urllib.parse
import hashlib
import logging
from .utilities import do_str_replace
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import OpayOrder, OpaySetting
from .setting import HASH_IV, HASH_KEY
from .setting import AIO_SANDBOX_SERVICE_URL, AIO_SERVICE_URL, ALLPAY_SANDBOX


class Opay():
    is_sandbox = ALLPAY_SANDBOX
    test_url = AIO_SANDBOX_SERVICE_URL

    def __init__(self, payment_conf, service_method='post'):
        # parameter = OpayOrder.objects.all()[0]
        # print(parameter)
        setting = OpaySetting.objects.all()[0]
        self.Opay_parameter = dict()
        # === BASIC CONFIG FOR OPAY ===
        self.service_method = service_method
        self.HASH_KEY = HASH_KEY
        self.HASH_IV = HASH_IV
        self.service_url = AIO_SANDBOX_SERVICE_URL if self.is_sandbox else AIO_SERVICE_URL
        """
        setting
        """
        # 會員代碼
        self.Opay_parameter['MerchantID'] = setting.MerchantID
        # 商店代碼
        self.Opay_parameter['StoreID'] = setting.StoreID
        # 交易類型
        self.Opay_parameter['PaymentType'] = setting.PaymentType
        # 付款完成後回傳網址
        self.Opay_parameter['ReturnURL'] = setting.ReturnURL
        # 選擇付款方式
        self.Opay_parameter['ChoosePayment'] = setting.ChoosePayment
        # 返回商店的按鈕連結(付款回傳結果網址失效)
        self.Opay_parameter['ClientBackURL'] = setting.ClientBackURL
        # 付款回傳結果網址(返回商店的按鈕連結失效)
        self.Opay_parameter['OrderResultURL'] = setting.OrderResultURL
        # 回傳額外付款資訊
        self.Opay_parameter['NeedExtraPaidInfo'] = setting.NeedExtraPaidInfo
        # 隱藏付款的方式
        self.Opay_parameter['IgnorePayment'] = '#'.join(setting.IgnorePayment)
        # 特約合作代號
        self.Opay_parameter['PlatformID'] = setting.PlatformID
        # 是否延遲付款
        self.Opay_parameter['HoldTradeAMT'] = setting.HoldTradeAMT
        # 加密
        self.Opay_parameter['EncryptType'] = setting.EncryptType
        # 是否使用購物金 / 紅包折抵
        self.Opay_parameter['UseRedeem'] = setting.UseRedeem

        # ChoosePayment = ALL or ATM
        if setting.ChoosePayment == 'ALL' or setting.ChoosePayment == 'ATM':
            # 允許繳費天數 / 上限60
            self.Opay_parameter['ExpireDate'] = setting.ExpireDate
        # ChoosePayment = ALL or CVS
        elif setting.ChoosePayment == 'ALL' or setting.ChoosePayment == 'CVS':
            # 超商繳費截止時間
            self.Opay_parameter['StoreExpireDate'] = setting.StoreExpireDate
        # ChoosePayment = ALL or ATM or CVS
        elif setting.ChoosePayment == 'ALL' or setting.ChoosePayment == 'ATM' or setting.ChoosePayment == 'CVS':
            # 訂單完成後顯示在歐付寶但資料回傳 / 非付款完成
            self.Opay_parameter['PaymentInfoURL'] = setting.PaymentInfoURL
            # 訂單完成後跳轉指定網址 / 非付款完成
            self.Opay_parameter['ClientRedirectURL'] = setting.ClientRedirectURL
        # ChoosePayment = ALL or Credit
        elif setting.ChoosePayment == 'ALL' or setting.ChoosePayment == 'Credit':
            # 是否允許使用信用卡紅利
            self.Opay_parameter['Redeem'] = setting.Redeem
            # ---------------------------------------------------------------
            # Pay on installment(分期付款)
            # If you want open installment, CreditInstallment must be having.
            if setting.CreditInstallment:
                # 刷卡允許分期期數
                self.Opay_parameter['CreditInstallment'] = setting.CreditInstallment
            # ---------------------------------------------------------------
            # period ordering(定期定額/訂閱制)
            elif not setting.CreditInstallment:
                # 每次授權金額
                self.Opay_parameter['PeriodAmount'] = setting.PeriodAmount
                # 週期種類
                self.Opay_parameter['PeriodType'] = setting.PeriodType
                # 執行頻率
                self.Opay_parameter['Frequency'] = setting.Frequency
                # 執行次數
                self.Opay_parameter['ExecTimes'] = setting.ExecTimes
                # 定期定額回傳網址
                self.Opay_parameter['PeriodReturnURL'] = setting.PeriodReturnURL

        """
        資料串接您的商店
        """
        # 交易編號
        self.Opay_parameter['MerchantTradeNo'] = hashlib.sha224(
            str(datetime.datetime.now()).encode('utf-8')).hexdigest().capitalize()[0:19]
        # 交易時間
        self.Opay_parameter['MerchantTradeDate'] = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        # 交易金額
        self.Opay_parameter['TotalAmount'] = 10 if not (
                'TotalAmount' in payment_conf) else payment_conf['TotalAmount']
        # 交易描述
        self.Opay_parameter['TradeDesc'] = '預設文字，交易描述' if not (
                'TradeDesc' in payment_conf) else payment_conf['TradeDesc']
        # 商品名稱
        self.Opay_parameter['ItemName'] = '預設文字，商品名稱' if not (
                'ItemName' in payment_conf) else payment_conf['ItemName']

        # 商品銷售網址
        self.Opay_parameter['ItemURL'] = '商品網址' if not (
                'ItemURL' in payment_conf) else payment_conf['ItemURL']
        # 備註欄位
        self.Opay_parameter['Remark'] = '' if not (
                'Remark' in payment_conf) else payment_conf['Remark']
        # 付款子項目
        self.Opay_parameter['ChooseSubPayment'] = '' if not (
                'ChooseSubPayment' in payment_conf) else payment_conf['ChooseSubPayment']
        # 裝置來源
        self.Opay_parameter['DeviceSource'] = '' if not (
                'DeviceSource' in payment_conf) else payment_conf['DeviceSource']

        if setting.ChoosePayment == 'ALL' or setting.ChoosePayment == 'CVS':
            # 交易描述1
            self.Opay_parameter['Desc_1'] = '' if not (
                    'Desc_1' in payment_conf) else payment_conf['Desc_1']
            # 交易描述2
            self.Opay_parameter['Desc_2'] = '' if not (
                    'Desc_2' in payment_conf) else payment_conf['Desc_2']
            # 交易描述3
            self.Opay_parameter['Desc_3'] = '' if not (
                    'Desc_3' in payment_conf) else payment_conf['Desc_3']
            # 交易描述4
            self.Opay_parameter['Desc_4'] = '' if not (
                    'Desc_4' in payment_conf) else payment_conf['Desc_4']

        """
        client
        """

    def check_out(self):
        sorted_dict = sorted(self.Opay_parameter.items())

        # insert the HashKey to the head of dictionary & HashIV to the end
        sorted_dict.insert(0, ('HashKey', self.HASH_KEY))
        sorted_dict.append(('HashIV', self.HASH_IV))
        result_request_str = do_str_replace(urllib.parse.quote(urllib.parse.urlencode(sorted_dict), '+%').lower())
        logging.info(urllib.parse.quote(urllib.parse.urlencode(sorted_dict), '+').lower())
        # sha256 encoding
        checkvl = hashlib.sha256(result_request_str.encode('utf-8'))
        check_mac_value = checkvl.hexdigest().upper()
        # 檢查碼
        self.Opay_parameter['CheckMacValue'] = check_mac_value
        return self.Opay_parameter

    @classmethod
    def checkout_feedback(cls, post):
        """
        :param post: post is a dictionary which allPay server sent to us.
        :return: a dictionary containing data the allpay server return to us.
        """
        logging.info('inside the feedback')
        returns = {}
        ar_parameter = {}
        check_mac_value = ''
        try:
            payment_type_replace_map = {'_CVS': '', '_BARCODE': '', '_Alipay': '', '_Tenpay': '', '_CreditCard': ''}
            period_type_replace_map = {'Y': 'Year', 'M': 'Month', 'D': 'Day'}
            for key, val in post.items():

                # print(key, val)
                if key == 'CheckMacValue':
                    check_mac_value = val
                else:
                    ar_parameter[key.lower()] = val
                    if key == 'PaymentType':
                        for origin, replacement in payment_type_replace_map.items():
                            val = val.replace(origin, replacement)
                    elif key == 'PeriodType':
                        for origin, replacement in period_type_replace_map.items():
                            val = val.replace(origin, replacement)
                    returns[key] = val

            sorted_returns = sorted(ar_parameter.items())
            sz_confirm_mac_value = "HashKey=" + HASH_KEY

            for val in sorted_returns:
                sz_confirm_mac_value = "".join((str(sz_confirm_mac_value), "&", str(val[0]), "=", str(val[1])))

            sz_confirm_mac_value = "".join((sz_confirm_mac_value, "&HashIV=", HASH_IV))
            sz_confirm_mac_value = do_str_replace((urllib.parse.quote_plus(sz_confirm_mac_value)).lower(), False)
            sz_confirm_mac_value = hashlib.sha256(sz_confirm_mac_value.encode('utf-8')).hexdigest().upper()

            logging.info('sz-checkMacValue: %s & checkMacValue: %s' % (sz_confirm_mac_value, check_mac_value))
            print(sz_confirm_mac_value)
            if sz_confirm_mac_value != check_mac_value:
                print('BBQ了')
                return False
            else:
                print('看我返回')
                return returns
        except:
            logging.info('Exception!')

    @classmethod
    def query_payment_info(cls, merchant_trade_no):
        """
        Implementing ...
        :param merchant_trade_no:
        :return:
        """
        logging.info('== Query the info==')
        returns = {}
        logging.info(merchant_trade_no)

        return returns
