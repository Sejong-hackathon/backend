from .models import UserProfile
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # login 성공시 저장된 session 가져온다
        user_id = request.session.get('id')
        try:
            user = UserProfile.objects.get(student_id__exact=user_id)
        except UserProfile.DoesNotExist:
            return Response({"status": 401, "context": "로그인 필요"})

        return user, None
