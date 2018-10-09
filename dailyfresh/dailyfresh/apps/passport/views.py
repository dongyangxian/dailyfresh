from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# def image_id(request, image_id):
#     print(image_id)
#     return Response('ok')
from dailyfresh.libs.captcha.captcha import captcha
from passport.serializers import CodeImageSerializer

class SendImageIdView(APIView):
    """发送图片验证码"""
    def get(self, request, image_id):
        """获取图片验证码"""
        # 1. 获取到当前的图片编号id
        code_id = image_id
        conn = get_redis_connection("session")
        # 2. 生成验证码
        name, text, image = captcha.generate_captcha()

        # 3. 保存当前生成的图片验证码内容
        try:
            conn.setex('Code_%s' % code_id, 60, text)
        except:
            return Response({'message': '服务器内部错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

        return HttpResponse(image)
