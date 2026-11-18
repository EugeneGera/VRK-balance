import io
import json
import unittest
from unittest.mock import patch

from flask import Flask
from app.analytics.assistant import assistant_blueprint


class FakeResponse(io.BytesIO):
    code=200


class AssistantGatewayTests(unittest.TestCase):
    def setUp(self):
        self.app=Flask(__name__)
        self.app.config.update(TESTING=True,BALANCE_ANALYTICS_TOKENS={
            'public-web':dict(subject='web-analyst',scopes=['balance:read']),
            'limited-user':dict(subject='limited',scopes=['balance:read'],product_ids=[1]),
        },BALANCE_ASSISTANT_TOKEN='public-web')
        self.app.register_blueprint(assistant_blueprint)
        self.client=self.app.test_client()

    def test_configured_web_role_is_used_without_exposing_its_key(self):
        captured=[]
        class Opener:
            def open(self,request,timeout):
                captured.append(request)
                return FakeResponse(json.dumps(dict(status='ok',data=dict(ready=False))).encode())
        with patch('app.analytics.assistant.build_opener',return_value=Opener()):
            response=self.client.get('/assistant/status')
        self.assertEqual(response.status_code,200)
        self.assertEqual(captured[0].get_header('Authorization'),'Bearer public-web')
        self.assertNotIn('public-web',response.text)

    def test_explicit_invalid_identity_never_falls_back_to_web_role(self):
        with patch('app.analytics.assistant.build_opener') as opener:
            response=self.client.get('/assistant/status',headers={'Authorization':'Bearer invalid'})
        self.assertEqual(response.status_code,401)
        opener.assert_not_called()

    def test_limited_caller_is_forwarded_as_the_same_caller(self):
        captured=[]
        class Opener:
            def open(self,request,timeout):
                captured.append(request)
                return FakeResponse(b'{"status":"ok","data":{}}')
        with patch('app.analytics.assistant.build_opener',return_value=Opener()):
            response=self.client.post('/assistant/chat',json=dict(action='summary'),headers={'Authorization':'Bearer limited-user'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(captured[0].get_header('Authorization'),'Bearer limited-user')

    def test_unconfigured_gateway_is_explicit(self):
        self.app.config['BALANCE_ASSISTANT_TOKEN']=''
        with patch.dict('os.environ',{},clear=True):
            response=self.client.get('/assistant/status')
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json['error']['code'],'assistant_not_configured')

    def test_upstream_error_is_not_returned_as_an_empty_success(self):
        with patch('app.analytics.assistant.build_opener',side_effect=OSError('private-address')):
            response=self.client.get('/assistant/status')
        self.assertEqual(response.status_code,503)
        self.assertNotIn('private-address',response.text)


if __name__=='__main__':unittest.main()
