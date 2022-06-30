import datetime
import time

from django.db import models
from multiselectfield import MultiSelectField


# Create your models here.
class OpaySetting(models.Model):
    """choose List"""
    ChooseSubPaymentList = (('TAISHIN', 'WebATM_台新銀行'),
                            ('SHINKONG', 'WebATM_新光銀行'),
                            ('FIRST', 'WebATM_第一銀行'),
                            ('MEGA', 'WebATM_兆豐銀行'),
                            ('TAISHIN', 'ATM_台新銀行'),
                            ('ESUN', 'ATM_玉山銀行'),
                            ('FIRST', 'ATM_第一銀行'),
                            ('CHINATRUST', 'ATM_中國信託銀行'),
                            ('CVS', '超商繳款'),
                            ('OK', 'OK超商繳款'),
                            ('FAMILY', '全家超商繳款'),
                            ('HILIFE', '萊爾富超商繳款'),
                            ('IBON', '7-11超商繳款'),
                            ('Credit', '信用卡'),
                            ('Allpay', '歐付寶'),)
    NeedExtraPaidInfoList = (('N', 'N'),
                             ('Y', 'Y'),)
    IgnorePaymentList = (('Credit', '隱藏信用卡'),
                         ('WebATM', '隱藏網路ATM'),
                         ('ATM', '隱藏ATM'),
                         ('CVS', '隱藏超商代碼'),
                         ('AccountLink', '隱藏銀行快付'),
                         ('TopUpUsed', '隱藏儲值消費'),)
    HoldTradeAMTList = ((0, '不延遲付款'), (1, '延遲付款'),)
    UseRedeemList = (('Y', 'Y'), ('N', 'N'))
    CreditInstallmentList = ((3, 3), (6, 6), (12, 12), (18, 18), (24, 24),)
    PeriodTypeList = (('D', '以天為週期'), ('M', '以月為週期'), ('Y', '以年為週期'),)
    ChoosePaymentList = (('Credit', '信用卡'),
                         ('WebATM', '網路ATM'),
                         ('ATM', 'ATM'),
                         ('CVS', '超商代碼'),
                         ('AccountLink', '銀行快付'),
                         ('TopUpUsed', '儲值消費(歐付寶)',),
                         ('WeiXinpay', '微信支付',),
                         ('ALL', '不指定付款方式',),)
    """Opay Setting"""
    MerchantID = models.CharField(max_length=10, verbose_name='*會員代碼')
    StoreID = models.CharField(max_length=20, blank=True, verbose_name='商店代碼')
    PaymentType = models.CharField(max_length=20, default='aio', verbose_name='*交易類型')  # don't change this value
    ReturnURL = models.CharField(max_length=200, verbose_name='*付款完成後回傳網址')
    ChoosePayment = models.CharField(max_length=20, choices=ChoosePaymentList, verbose_name='*選擇付款方式')
    ClientBackURL = models.CharField(max_length=200, blank=True, verbose_name='返回商店的按鈕連結(付款回傳結果網址失效)')
    OrderResultURL = models.CharField(max_length=200, blank=True, verbose_name='付款回傳結果網址(返回商店的按鈕連結失效)')
    NeedExtraPaidInfo = models.CharField(max_length=1, default='N', blank=True, choices=NeedExtraPaidInfoList,
                                         verbose_name='回傳額外付款資訊')
    IgnorePayment = MultiSelectField(max_length=100, blank=True, choices=IgnorePaymentList, verbose_name='隱藏付款的方式')
    PlatformID = models.CharField(max_length=10, blank=True, verbose_name='特約合作代號')
    HoldTradeAMT = models.IntegerField(default=0, blank=True, choices=HoldTradeAMTList, verbose_name='是否延遲付款')
    EncryptType = models.IntegerField(default=1, verbose_name='加密')  # don't change this value
    UseRedeem = models.CharField(max_length=1, default='N', blank=True, choices=UseRedeemList,
                                 verbose_name='是否使用購物金/紅包折抵')

    """
    ChoosePayment = ALL or ATM
    """
    ExpireDate = models.IntegerField(default=3, blank=True, verbose_name='允許繳費天數/上限60')  # range(1~60)day

    """
    ChoosePayment = ALL or CVS
    """
    # StoreExpireDate range example
    # if int > 100 (min)
    # if int <= 100 (day)
    StoreExpireDate = models.IntegerField(default=7, blank=True, verbose_name='超商繳費截止時間')

    """
    ChoosePayment = ALL or ATM or CVS
    """
    PaymentInfoURL = models.CharField(max_length=200, blank=True, verbose_name='訂單完成後顯示在歐付寶/非付款完成')
    ClientRedirectURL = models.CharField(max_length=200, blank=True, verbose_name='訂單完成後跳轉指定網址/非付款完成')

    """
    ChoosePayment = ALL or Credit
    """
    # Pay in full
    Redeem = models.CharField(max_length=1, default='N', blank=True, choices=UseRedeemList, verbose_name='是否允許使用信用卡紅利')
    # ---------------------------------------------------------------
    # Pay on installment
    # If you want open installment, CreditInstallment must be having.
    CreditInstallment = MultiSelectField(max_length=10, blank=True, choices=CreditInstallmentList,
                                         verbose_name='*刷卡允許分期期數')
    # ---------------------------------------------------------------
    # period ordering
    PeriodAmount = models.IntegerField(default=0, blank=True, verbose_name='*每次授權金額')  # TWD,INT
    PeriodType = models.CharField(max_length=1, blank=True, choices=PeriodTypeList,
                                  verbose_name='*週期種類')  # D(Day) or M(Month) or Y(Year)
    Frequency = models.IntegerField(default=0,
                                    blank=True,
                                    verbose_name='*執行頻率')  # Frequency  >= 1 and if PeriodType D (max = 365),M (max = 12),Y (max = 1)
    ExecTimes = models.IntegerField(default=0, blank=True,
                                    verbose_name='*執行次數')  # ExecTimes>=1 and if PeriodType D (max = 999),M (max = 99),Y (max = 9)
    PeriodReturnURL = models.CharField(max_length=200, blank=True, verbose_name='定期定額回傳網址')


class OpayOrder(models.Model):
    DeviceSourceList = (('', '預設版型'), ('APP', 'APP版型'),)

    MerchantTradeNo = models.CharField(max_length=64, unique=True, verbose_name='*交易編號')
    MerchantTradeDate = models.CharField(max_length=20, default=time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())), verbose_name='*交易時間')
    TotalAmount = models.IntegerField(default=10, verbose_name='*交易金額')
    TradeDesc = models.CharField(max_length=200, default='oPay購物商城', verbose_name='*交易描述')
    ItemName = models.CharField(max_length=200, default='item1#item2#item3', verbose_name='*商品名稱')
    CheckMacValue = models.CharField(max_length=256, verbose_name='*檢查碼')
    ItemURL = models.CharField(max_length=200, blank=True, verbose_name='商品銷售網址')
    Remark = models.CharField(max_length=100, blank=True, verbose_name='備註欄位')
    ChooseSubPayment = models.CharField(max_length=20, blank=True, verbose_name='付款子項目')
    DeviceSource = models.CharField(max_length=10, blank=True, choices=DeviceSourceList, verbose_name='裝置來源')

    Desc_1 = models.CharField(max_length=20, blank=True, verbose_name='交易描述1')
    Desc_2 = models.CharField(max_length=20, blank=True, verbose_name='交易描述2')
    Desc_3 = models.CharField(max_length=20, blank=True, verbose_name='交易描述3')
    Desc_4 = models.CharField(max_length=20, blank=True, verbose_name='交易描述4')

    def __str__(self):
        return self.MerchantTradeNo


# ReturnURL Response
class OrderResponse(models.Model):
    MerchantID = models.CharField(max_length=10)
    MerchantTradeNo = models.ForeignKey(OpayOrder, models.CASCADE)
    StoreID = models.CharField(max_length=20)
    RtnCode = models.IntegerField()
    RtnMsg = models.CharField(max_length=200)
    TradeNo = models.CharField(max_length=20)
    TradeAmt = models.IntegerField()
    PayAmt = models.IntegerField()
    RedeemAmt = models.IntegerField()
    PaymentDate = models.CharField(max_length=20)
    PaymentType = models.CharField(max_length=20)
    PaymentTypeChargeFee = models.IntegerField()
    TradeDate = models.CharField(max_length=20)
    SimulatePaid = models.IntegerField()
    CheckMacValue = models.CharField(max_length=256)
    """
    NeedExtraPaidInfo = Y
    """
    WebATMAccBank = models.CharField(max_length=3, blank=True)
    WebATMAccNo = models.CharField(max_length=5, blank=True)
    WebATMBankName = models.CharField(max_length=10, blank=True)
    ATMAccBank = models.CharField(max_length=3, blank=True)
    ATMAccNo = models.CharField(max_length=5, blank=True)
    PaymentNo = models.CharField(max_length=14, blank=True)
    PayFrom = models.CharField(max_length=10, blank=True)
    TenpayTradeNo = models.CharField(max_length=10, blank=True)
    gwsr = models.IntegerField()
    process_date = models.CharField(max_length=20, blank=True)
    auth_code = models.CharField(max_length=20, blank=True)
    amount = models.IntegerField()
    stage = models.IntegerField()
    stast = models.IntegerField()
    staed = models.IntegerField()
    eci = models.IntegerField()
    card4no = models.CharField(max_length=4, blank=True)
    card6no = models.CharField(max_length=6, blank=True)
    red_dan = models.IntegerField()
    red_de_amt = models.IntegerField()
    red_ok_amt = models.IntegerField()
    red_yet = models.IntegerField()
    PeriodType = models.CharField(max_length=1, blank=True)
    Frequency = models.IntegerField()
    ExecTimes = models.IntegerField()
    PeriodAmount = models.IntegerField()
    TotalSuccessTimes = models.IntegerField()
    TotalSuccessAmount = models.IntegerField()
    WeiXinpayTradeNo = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.MerchantTradeNo


# PeriodReturnURL Response
class PeriodOrderResponse(models.Model):
    MerchantID = models.CharField(max_length=10)
    MerchantTradeNo = models.CharField(max_length=64, unique=True)
    StoreID = models.CharField(max_length=20)
    RtnCode = models.IntegerField()
    RtnMsg = models.CharField(max_length=200)
    PeriodType = models.CharField(max_length=1, blank=True)
    Frequency = models.IntegerField()
    ExecTimes = models.IntegerField(blank=True)
    Amount = models.IntegerField()
    Gwsr = models.IntegerField()
    ProcessDate = models.CharField(max_length=20)
    AuthCode = models.CharField(max_length=6)
    FirstAuthAmount = models.IntegerField()
    TotalSuccessTimes = models.IntegerField()
    SimulatePaid = models.IntegerField()
    CheckMacValue = models.CharField(max_length=256)

    def __str__(self):
        return self.MerchantTradeNo


# PaymentInfoURL Response
class ATMCVSResponse(models.Model):
    MerchantID = models.CharField(max_length=10)
    MerchantTradeNo = models.CharField(max_length=64, unique=True)
    StoreID = models.CharField(max_length=20)
    RtnCode = models.IntegerField()
    RtnMsg = models.CharField(max_length=200)
    TradeNo = models.CharField(max_length=20)
    TradeAmt = models.IntegerField()
    PayAmt = models.IntegerField()
    RedeemAmt = models.IntegerField()
    PeriodType = models.CharField(max_length=1)
    TradeDate = models.CharField(max_length=20)
    Barcode1 = models.CharField(max_length=20)
    Barcode2 = models.CharField(max_length=20)
    Barcode3 = models.CharField(max_length=20)
    CheckMacValue = models.CharField(max_length=256)
    """
    ATM
    """
    BankCode = models.CharField(max_length=3, blank=True)
    vAccount = models.CharField(max_length=16, blank=True)
    ExpireDate_ATM = models.CharField(max_length=10, blank=True)
    """
    CVS
    """
    PaymentNo = models.CharField(max_length=14, blank=True)
    ExpireDate_CVS = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.MerchantTradeNo
