import hashlib
import six
from collections import OrderedDict


class SignatureMixin(object):

    def _build_query(self, params):
        results = []
        for key, val in params.items():
            if isinstance(val, dict):
                val = self._hash_param(self._build_query(val))
            elif isinstance(val, (list, tuple)):
                val = '|'.join(map(six.text_type, val))
            else:
                val = six.text_type(val)
            results.append('='.join((six.text_type(key), val)))
        return '&'.join(results)

    def _sign_params(self, params, password):
        """
        Calculate signature of all @params and append to param @OrderedDict

        :type params: OrderedDict
        """
        hash_params = OrderedDict(params)
        hash_params['password'] = password

        param_str = self._build_query(hash_params)
        params['signature'] = self._hash_param(param_str.encode('utf-8'))

        return params

    def _hash_param(self, params):
        return hashlib.sha256(params).hexdigest()
