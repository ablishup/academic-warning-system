#!/usr/bin/env python
"""
短信服务封装
支持: Mock服务(默认)、阿里云短信、腾讯云短信
"""
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict

logger = logging.getLogger(__name__)


class BaseSMSService(ABC):
    """短信服务基类"""

    @abstractmethod
    def send_sms(self, phone: str, content: str, template_code: str = None) -> Dict:
        """发送单条短信"""
        pass


class MockSMSService(BaseSMSService):
    """
    模拟短信服务（用于演示和开发环境）
    不实际发送短信，只记录日志
    """

    def send_sms(self, phone: str, content: str, template_code: str = None) -> Dict:
        logger.info("=" * 60)
        logger.info("[MOCK SMS] MoNi DuanXin FaSong")
        logger.info(f"[MOCK SMS] JieShouHaoMa: {phone}")
        logger.info(f"[MOCK SMS] NeiRong: {content[:100]}...")
        logger.info("=" * 60)

        return {
            'success': True,
            'provider': 'mock',
            'request_id': f'mock-{phone}-{hash(content) % 10000}',
            'message': 'MoNi FaSong ChengGong (ShiJi Wei FaSong, Jin Yong Yu Yan Shi)'
        }


class AliyunSMSService(BaseSMSService):
    """阿里云短信服务"""

    def __init__(self):
        self.access_key_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID', '')
        self.access_key_secret = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')
        self.sign_name = os.environ.get('SMS_SIGN_NAME', 'XueYeYuJing')
        self.enabled = bool(self.access_key_id and self.access_key_secret)

    def send_sms(self, phone: str, content: str, template_code: str = None) -> Dict:
        if not self.enabled:
            return {
                'success': False,
                'error_message': 'A Li Yun DuanXin FuWu Wei PeiZhi'
            }

        try:
            # 使用阿里云SDK
            from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
            from alibabacloud_tea_openapi import models as open_api_models
            from alibabacloud_dysmsapi20170525.client import Client

            config = open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret
            )
            config.endpoint = 'dysmsapi.aliyuncs.com'

            client = Client(config)

            send_sms_request = dysmsapi_models.SendSmsRequest(
                phone_numbers=phone,
                sign_name=self.sign_name,
                template_code=template_code or 'SMS_DEFAULT',
                template_param=json.dumps({'content': content[:100]})
            )

            response = client.send_sms(send_sms_request)

            if response.body.code == 'OK':
                return {
                    'success': True,
                    'provider': 'aliyun',
                    'request_id': response.body.request_id,
                    'message': 'DuanXin Yi FaSong'
                }
            else:
                return {
                    'success': False,
                    'provider': 'aliyun',
                    'error_message': response.body.message,
                    'code': response.body.code
                }

        except Exception as e:
            logger.error(f'A Li Yun DuanXin FaSong ShiBai: {str(e)}')
            return {
                'success': False,
                'provider': 'aliyun',
                'error_message': str(e)
            }


class TencentSMSService(BaseSMSService):
    """腾讯云短信服务"""

    def __init__(self):
        self.secret_id = os.environ.get('TENCENT_CLOUD_SECRET_ID', '')
        self.secret_key = os.environ.get('TENCENT_CLOUD_SECRET_KEY', '')
        self.app_id = os.environ.get('TENCENT_SMS_APP_ID', '')
        self.sign_name = os.environ.get('SMS_SIGN_NAME', 'XueYeYuJing')
        self.enabled = bool(self.secret_id and self.secret_key)

    def send_sms(self, phone: str, content: str, template_code: str = None) -> Dict:
        if not self.enabled:
            return {
                'success': False,
                'error_message': 'TengXun Yun DuanXin FuWu Wei PeiZhi'
            }

        try:
            from tencentcloud.common import credential
            from tencentcloud.common.profile.client_profile import ClientProfile
            from tencentcloud.common.profile.http_profile import HttpProfile
            from tencentcloud.sms.v20210111 import sms_client, models

            cred = credential.Credential(self.secret_id, self.secret_key)

            http_profile = HttpProfile()
            http_profile.reqMethod = "POST"
            http_profile.reqTimeout = 30

            client_profile = ClientProfile()
            client_profile.signMethod = "TC3-HMAC-SHA256"
            client_profile.httpProfile = http_profile

            client = sms_client.SmsClient(cred, "ap-guangzhou", client_profile)

            req = models.SendSmsRequest()
            req.SmsSdkAppId = self.app_id
            req.SignName = self.sign_name
            req.TemplateId = template_code or "123456"
            req.TemplateParamSet = [content[:100]]
            req.PhoneNumberSet = [f"+86{phone}"]

            response = client.SendSms(req)

            send_status = response.SendStatusSet[0]
            if send_status.Code == "Ok":
                return {
                    'success': True,
                    'provider': 'tencent',
                    'request_id': response.RequestId,
                    'message': 'DuanXin Yi FaSong'
                }
            else:
                return {
                    'success': False,
                    'provider': 'tencent',
                    'error_message': send_status.Message,
                    'code': send_status.Code
                }

        except Exception as e:
            logger.error(f'TengXun Yun DuanXin FaSong ShiBai: {str(e)}')
            return {
                'success': False,
                'provider': 'tencent',
                'error_message': str(e)
            }


# 根据环境变量选择短信服务
_sms_service = None


def get_sms_service():
    """获取短信服务实例（单例模式）"""
    global _sms_service
    if _sms_service is None:
        provider = os.environ.get('SMS_SERVICE', 'mock').lower()

        if provider == 'aliyun':
            _sms_service = AliyunSMSService()
        elif provider == 'tencent':
            _sms_service = TencentSMSService()
        else:
            # 默认使用Mock服务
            _sms_service = MockSMSService()

    return _sms_service


# 导出单例
sms_service = get_sms_service()
