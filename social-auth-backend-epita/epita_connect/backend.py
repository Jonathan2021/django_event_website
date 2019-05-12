"""
Epita OpenIdConnect:
"""
from social_core.backends.open_id_connect import OpenIdConnectAuth


class EpitaOpenIdConnect(OpenIdConnectAuth):
    name = 'epita'
    OIDC_ENDPOINT = 'https://intra.cri.epita.net/oidc'

    def oidc_config(self):
        if self.setting('BETA', default=False):
            endpoint = 'https://accounts-beta.cri.epita.net/oidc'
        else:
            endpoint = self.OIDC_ENDPOINT
        return self.get_json(endpoint +
                             '/.well-known/openid-configuration')
