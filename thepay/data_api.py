from collections import OrderedDict
import suds.client

from thepay.utils import SignatureMixin


class DataApi(SignatureMixin):
    def __init__(self, config):
        """

        :param config: Config
        """
        self.config = config
        self.client = None

        self.connect()

    def connect(self):
        self.client = suds.client.Client(self.config.dataWebServicesWsdl)

    def get_payment_methods(self):
        params = self._signParams(OrderedDict((
            ('merchantId', self.config.merchant_id),
            ('accountId', self.config.account_id),
        )), self.config.data_api_password)
        return self.client.service.getPaymentMethods(**params).methods[0]

    def get_payment_state(self, payment_id):
        params = self._signParams(OrderedDict((
            ('merchantId', self.config.merchant_id),
            ('paymentId', payment_id),
        )), self.config.data_api_password)
        return int(self.client.service.getPaymentState(**params).state)

    def get_payment(self, payment_id):
        params = self._signParams(OrderedDict((
            ('merchantId', self.config.merchant_id),
            ('paymentId', payment_id),
        )), self.config.data_api_password)
        return self.client.service.getPayment(**params).payment

    def get_payment_instructions(self, payment_id):
        params = self._signParams(OrderedDict((
            ('merchantId', self.config.merchant_id),
            ('paymentId', payment_id),
        )), self.config.data_api_password)
        return self.client.service.getPaymentInstructions(**params).paymentInfo
