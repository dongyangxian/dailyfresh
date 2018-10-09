from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
from users.models import User


class UserExsitView(APIView):
    """用户判断"""
    def get(self, request, username):

        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)

class PhoneExsitView(APIView):
    """手机号判断"""
    def get(self, request, phone):

        count = User.objects.filter(mobile=phone).count()

        data = {
            'phone': phone,
            'count': count
        }

        return Response(data)