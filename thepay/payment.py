from collections import OrderedDict
import hashlib
from urllib.parse import urlencode

from decimal import Decimal
from thepay.utils import SignatureMixin
from thepay.exceptions import InvalidSignature, MissingParameter


class Payment(SignatureMixin):
    """
    Class representing single Payment

    Payment parameters:
        value: Float value indicating the amount of money that should be paid
        currency: Currency identifier. Not used so far, reserved for future use
        description: Payment description that should be visible to the customer
        merchantData: Any merchant-specific data, that will be returned to the site after the payment has been completed
        returnUrl: URL where to redirect the user after the payment has been completed. It defaults to value configured 
                in administration interface, but can be overwritten using this property
        methodId: ID of payment method to use for paying. Setting this argument should be result of user's selection, 
                not merchant's selection
        customerData: Optional data about customer. Required for FerBuy method
        customerEmail: Customers e-mail address. Used to send payment info and payment link from the payment info page
        deposit: If card payment will be charged immediately or only blocked and charged later by paymentDeposit 
                operation 
        isRecurring: If card payment is recurring
        merchantSpecificSymbol: specific symbol (used only if payment method supports it)
    """

    mapping = OrderedDict((
        ('value', 'value'),
        ('currency', 'currency'),
        ('description', 'description'),
        ('merchantData', 'merchant_data'),
        ('customerData', 'customer_data'),
        ('customerEmail', 'customer_email'),
        ('returnUrl', 'return_url'),
        ('methodId', 'method_id'),
        ('deposit', 'deposit'),
        ('isRecurring', 'is_recurring'),
        ('merchantSpecificSymbol', 'merchant_specific_symbol'),
    ))

    def __init__(self, config):
        self.config = config
        self.value = None
        self.currency = None
        self.description = None
        self.merchant_data = None
        self.customer_data = None
        self.customer_email = None
        self.return_url = None
        self.method_id = None
        self.deposit = None
        self.is_recurring = None
        self.merchant_specific_symbol = None

    def get_params(self):
        """
        List arguments to put into the URL. Returns associative array of
        arguments that should be contained in the ThePay gate call.
        """
        params = OrderedDict()

        params['merchantId'] = self.config.merchant_id
        params['accountId'] = self.config.account_id

        for api_key, attr_name in self.mapping.items():
            value = getattr(self, attr_name)
            if value is not None:
                params[api_key] = value
        return params

    def _hash_param(self, params):
        # this interface is using deprecated md5 hashing
        return hashlib.md5(params).hexdigest()

    def get_create_url(self):
        """
        Returns absolute url that creates this payment

        :return: url-encoded string
        """
        params = self._sign_params(self.get_params(), self.config.password)
        return "{}?{}".format(self.config.gate_url, urlencode(params))


class ReturnPayment(SignatureMixin):
    required_data = OrderedDict((
        ('value', 'value'),
        ('currency', 'currency'),
        ('methodId', 'method_id'),
        ('description', 'description'),
        ('merchantData', 'merchant_data'),
        ('status', 'status'),
        ('paymentId', 'payment_id'),
        ('ipRating', 'ip_rating'),
        ('isOffline', 'is_offline'),
        ('needConfirm', 'need_confirm'),
    ))

    optional_data = OrderedDict((
        ('isConfirm', 'is_confirm'),
        ('variableSymbol', 'variable_symbol'),
        ('specificSymbol', 'specific_symbol'),
        ('deposit', 'deposit'),
        ('isRecurring', 'is_rcurring'),
        ('customerAccountNumber', 'customer_account_number'),
        ('customerAccountName', 'customer_account_name'),
    ))

    def __init__(self, config, data):
        self.config = config
        self.signature = None
        self.data = data
        self._parse_data(data)

    def _parse_data(self, data):
        for api_key, attr_name in self.required_data.items():
            if api_key not in data:
                raise MissingParameter(api_key)

            value = data[api_key]
            if hasattr(self, '_clean_{}'.format(attr_name)):
                value = getattr(self, '_clean_{}'.format(attr_name))(value)
            setattr(self, attr_name, value)

        for api_key, attr_name in self.optional_data.items():
            value = data.get(api_key, None)
            if hasattr(self, '_clean_{}'.format(attr_name)):
                value = getattr(self, '_clean_{}'.format(attr_name))(value)
            setattr(self, attr_name, value)
        self.signature = data.get('signature', None)

    def _hash_param(self, params):
        # this interface is using deprecated md5 hashing
        return hashlib.md5(params).hexdigest()

    def check_signature(self):
        params = OrderedDict()

        params['merchantId'] = self.config.merchant_id
        params['accountId'] = self.config.account_id

        data_keys = list(self.required_data.keys()) + list(self.optional_data.keys())
        for key in data_keys:
            if key not in self.data:
                continue

            params[key] = self.data[key]

        signed_params = self._sign_params(params, self.config.password)

        if self.signature != signed_params['signature']:
            raise InvalidSignature()

        return True

    def _clean_value(self, value):
        return Decimal(value)

    def _clean_method_id(self, value):
        return int(value)

    def _clean_currency(self, value):
        return 'CZK' if value is None else value

    def _clean_status(self, value):
        return int(value)
