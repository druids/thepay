from __future__ import print_function

from datetime import datetime, date

from pytz import timezone

import unittest

from thepay.config import Config
from thepay.data_api import DataApi
from thepay.payment import Payment, ReturnPayment
from six.moves import urllib
from decimal import Decimal


class DataApiTests(unittest.TestCase):
    def setUp(self):
        super(DataApiTests, self).setUp()
        self.config = Config()
        self.data_api = DataApi(self.config)

    def test_methods(self):
        self.assertEqual(self.data_api.get_payment_methods()[0].name, 'MojePlatba')

    def test_payment_statue(self):
        self.assertEqual(self.data_api.get_payment_state(1), 2)

    def test_payment(self):
        self.assertEqual(self.data_api.get_payment(1).id, '1')

    def test_payment_info(self):
        self.data_api.get_payment_instructions(1)

    def test_credentials(self):
        self.config.set_credentials(42, 43, 'test', 'test2')

        self.assertEqual(self.config.merchant_id, 42)
        self.assertEqual(self.config.account_id, 43)
        self.assertEqual(self.config.password, 'test')
        self.assertEqual(self.config.data_api_password, 'test2')

    def test_payments(self):
        self.data_api.get_payments().pagination
        self.data_api.get_payments(value_from=100).pagination
        self.data_api.get_payments(created_on_from=datetime.now(timezone('UTC'))).pagination
        self.data_api.get_payments(created_on_to=datetime.now(timezone('UTC'))).pagination
        self.data_api.get_payments(created_on_from=datetime.now(timezone('UTC')),
                                   created_on_to=datetime.now(timezone('UTC'))).pagination
        self.data_api.get_payments(finished_on_from=datetime.now(timezone('UTC')),
                                   finished_on_to=datetime.now(timezone('UTC'))).pagination


class PaymentTests(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.payment = Payment(self.config)

    def fill_payment(self):
        self.payment.value = '123.0'
        self.payment.return_url = 'http://test.te'
        self.payment.customer_email ='test@test.te'
        self.payment.description ='Order 123 payment'
        self.payment.method_id = 1
        self.payment.merchant_data ='Order 123'

    def test_params(self):
        self.fill_payment()

        self.assertDictEqual(dict(self.payment.get_params()), {
            'value': '123.0',
            'accountId': 1,
            'merchantId': 1,
            'returnUrl': 'http://test.te',
            'customerEmail': 'test@test.te',
            'description': 'Order 123 payment',
            'methodId': 1,
            'merchantData': 'Order 123',
         })

    def test_url(self):
        self.fill_payment()
        self.assertEqual(self.payment.get_create_url(),
                         'https://www.thepay.cz/demo-gate/?merchantId=1&accountId=1&value=123.0&description=Order+123+payment&merchantData=Order+123&customerEmail=test%40test.te&returnUrl=http%3A%2F%2Ftest.te&methodId=1&signature=7450a2ca57f4a380ed7c4e71d6e0e6bf')


class ReturnPaymentTests(unittest.TestCase):
    def setUp(self):
        self.config = Config()

    def test_data(self):
        params_str = 'merchantId=1&accountId=1&value=123.00&currency=CZK&methodId=1&description=Order+123+payment&merchantData=Order+123&status=2&paymentId=34886&ipRating=&isOffline=0&needConfirm=0&signature=f38ff15cc17752a6d4035044a93deb06'
        params = urllib.parse.parse_qs(params_str, keep_blank_values=True)
        params = {key: value[0] for key, value in params.items()}

        payment = ReturnPayment(self.config, params)

        payment.check_signature()

        self.assertIsNotNone(payment.payment_id)

        self.assertEqual(payment.currency, 'CZK')
        self.assertEqual(payment.signature, 'f38ff15cc17752a6d4035044a93deb06')
        self.assertEqual(payment.value, Decimal('123.00'))
        self.assertEqual(payment.method_id, 1)
        self.assertEqual(payment.description, 'Order 123 payment')
        self.assertEqual(payment.status, 2)
