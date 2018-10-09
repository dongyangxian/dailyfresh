import random

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

class SendSMSView(APIView):
    """发送短信验证码"""
    def get(self, request, mobile):

        # 1. 获取前端参数
        text = request.GET.get('text')
        image_code_id = request.GET.get('image_code_id')

        if not image_code_id:
            return Response({"message": "image_code_id is NULL"})

        # 2. 判断图片验证码是否正确
        conn = get_redis_connection('session')

        # 2.1 取出验证码(取出的验证码为byte类型，所以需要解码)
        image_code = conn.get('Code_%s' % image_code_id).decode()

        if not image_code:
            return Response({"message": "图片已过期"})

        # 2.2 将取出的图片内容与输入的对比
        if text.lower() != image_code.lower():
            return Response({"message": "图片内验证码输入错误"})

        # 2.3 如果对比成功，就将其删除
        conn.delete('Code_%s' % image_code_id)

        # 3. 生成短信验证码
        sms_code = random.randint(0, 99999)
        sms_code = '%06d' % sms_code
        print(sms_code)

        # 3.1 保存短信验证码
        conn.setex("sms_code_%s" % mobile, 300, sms_code)
        conn.setex("sms_flag_%s" % mobile, 60, 1)

        # 4. 返回结果
        return Response({"message": "OK"})
