class Config(object):

    # ThePay API
    gate_url = 'https://www.thepay.cz/demo-gate/'
    merchant_id = 1
    account_id = 1
    password = 'my$up3rsecr3tp4$$word'

    # Data API
    data_api_password = 'my$up3rsecr3tp4$$word'
    web_services_wsdl = 'https://www.thepay.cz/demo-gate/api/api-demo.wsdl'
    data_web_services_wsdl = 'https://www.thepay.cz/demo-gate/api/data-demo.wsdl'

    def set_credentials(self, merchantId, accountId, password, data_api_password=None):
        """ Set credentials for production server

        :param merchantId:
        :param accountId:
        :param password:
        :param dataApiPassword:
        """
        self.gate_url = 'https://www.thepay.cz/gate/'
        self.web_services_wsdl = 'https://www.thepay.cz/gate/api/api.wsdl'
        self.data_web_services_wsdl = 'https://www.thepay.cz/gate/api/data.wsdl'
        self.merchant_id = merchantId
        self.account_id = accountId
        self.password = password
        self.data_api_password = data_api_password
