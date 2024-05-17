from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import LoginSerializer
from bcrypt import hashpw, checkpw, gensalt
from sejong_univ_auth import auth, ClassicSession

from .models import UserProfile


def get_user_info(id, pw):
    # ClassicSession: 대양휴머니티칼리지 사이트의 세션 인증 방식
    # 이름, 학과, 학년, 재학 상태, 고전독서 인증 현황 조회 가능
    res = auth(id=id, password=pw, methods=ClassicSession)

    # 대휴칼 사이트 오류
    if res.status_code != 200:
        return "err_server"

    # 로그인 오류 (ID/PW 틀림 or 가입 불가 재학생)
    if not res.is_auth:
        return "err_auth"

    # 사용자 정보
    name = res.body["name"]
    major = res.body["major"]

    context = {
        "name": name,
        "major": major,
    }
    return context


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['id']
            user_pw = serializer.validated_data['pw']

            # 대양 휴머니티 칼리지 인증
            user_info = get_user_info(id=user_id, pw=user_pw)

            # 대양 휴머니티 칼리지 인증 오류 처리
            if user_info == 'err_auth':
                return Response({"status": 400, "context": "세종대학교 포털 ID/PW를 다시 확인하세요. / 재외국민전형 입학자, 계약학과, 편입생은 로그인이 불가합니다."})
            elif user_info == 'err_server':
                return Response({"status": 500, "context": "대양 휴머니티 칼리지 서버 오류. 잠시 후 시도해주세요."})

            # 비밀번호 암호화
            hashed_pw = hashpw(user_pw.encode('utf-8'), gensalt())

            try:
                user = UserProfile.objects.get(student_id=user_id)
                # 입력받은 pw와 db에 저장된 pw 비교 (user_pw 암호화 후 비교)
                if not checkpw(user_pw.encode('utf-8'), user.password.encode('utf-8')):
                    return Response({"status": 400, "context": "세종대학교 포털 비밀번호를 확인하세요"})
            except UserProfile.DoesNotExist:
                # 사용자가 없는 경우 회원가입 처리
                new_user = UserProfile.objects.create(
                    student_id=user_id,
                    password=hashed_pw.decode('utf-8'),  # 디코딩하여 저장
                    year=user_id[:2],
                    name=user_info.get('name'),
                    major=user_info.get('major')
                )
                new_user.save()

            # 세션 생성 또는 갱신
            request.session['id'] = user_id
            return Response({"status": 200, "context": "로그인 성공"})
        else:
            return Response({"status": 400, "context": serializer.errors})
