import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(label='验证码', max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(write_only=True)

    # 添加token
    token = serializers.CharField(label='登录状态token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'mobile', 'username', 'password', 'password2', 'sms_code', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'max_length': '名字过长',
                    'min_length': '名字过短'
                }
            },
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
                'error_messages': {
                    'max_length': '密码过长',
                    'min_length': '密码过短'
                }
            }
        }

    def validate(self, attrs):
        # 手机格式判断
        mobile = attrs['mobile']
        if not re.match(r'1[3-9]\d{9}$', mobile):
            return serializers.ValidationError('手机格式不正确')

        # 密码判断
        if attrs['password'] != attrs['password2']:
            return serializers.ValidationError('密码不一致')

        # 短信判断
        # 先获取缓存
        conn = get_redis_connection('session')
        # 取出数据，进行判断
        real_sms_code = conn.get('sms_code_%s' % attrs['mobile'])

        if not real_sms_code:
            return serializers.ValidationError('短信验证码失效')

        if attrs['sms_code'] != real_sms_code.decode():
            return serializers.ValidationError('短信验证码错误')
        # 返回
        return attrs

    def create(self, validated_data):
        """创建用户对象"""
        # 1. 删除用户表中没有的字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 2. 保存用户
        user = super().create(validated_data)
        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()

        # 3. 写入token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token

        # 4. 返回创建的用户
        return user
