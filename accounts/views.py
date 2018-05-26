from django.shortcuts import render, redirect

from dataParser.models import StudentInfo
from dataParser.parser import *
from accounts.forms import LoginForm, AgreeForm
from accounts.my_auth import UserBackend
from accounts.custom_auth import check_if_user
from django.contrib.auth import login as django_login, logout

hukbunToSave = ''
passwordToSave = ''

def agree(request):
    global hukbunToSave, passwordToSave
    if request.method == 'POST':
        agreeDataUsing = request.POST.get('agreeDataUsing','')
        if agreeDataUsing:
            if hukbunToSave == '' or passwordToSave == '': #혹시 모를 에러 검사
                print('데이터 저장 안됨')
                return redirect('accounts:login')
            test = StudentParser(hukbunToSave, passwordToSave)
            test.save_info(test.parse_info())
            test.save_grade(hukbunToSave, test.parse_grade())
            # TO-DO : 동의성공 창 띄우기
            # TO-DO : 디비에 데이터 저장하기
            userBackend = UserBackend()
            django_login(request, userBackend.get_user(hukbunToSave)) #로그인
            hukbunToSave = ''
            passwordToSave = ''
            return redirect('index')
    else:
        form = AgreeForm()
        return render(request, 'agree.html', {'form': form})

def login(request):
    global hukbunToSave, passwordToSave
    if request.method == 'POST':
        # Data bounded form인스턴스 생성
        login_form = LoginForm(request.POST)

        # 유효성 검증에 성공할 경우
        # form으로부터 username, password값을 가져옴
        hukbun = request.POST.get('hukbun', '')
        print(hukbun)
        password = request.POST.get('password', '')
        print(password)
        userBackend = UserBackend()

        kutis_login_success = check_if_user(hukbun, password)  # 쿠티스 로그인 시도
        if kutis_login_success:  # 쿠티스 로그인에 성공했다면
            user = userBackend.authenticate(hukbun=hukbun)  # DB 조사
            if user: # 모든 로그인 성공('user'변수안에 내용이 존재하지 않으면 None임)
                django_login(request, user)
                return redirect('index')
                #return render(request, 'index.html', {})
            # 첫 사용자
            else:
                hukbunToSave = hukbun
                passwordToSave = password
                return redirect('accounts:agree')
                #agree(request, hukbun, password)
        else:
            return redirect('accounts:login')

    else:
        form = LoginForm()
        return render(request, 'loginTest.html', {'form': form})

def get_queryset(self):
    return StudentInfo.objects.all()