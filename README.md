# Circruit
개발 팀원 모집 서비스 (숭실대 소프트웨어학부 소프트웨어 공모전)

[Docker Hub](https://cloud.docker.com/repository/docker/subacc09/circruit_flask)

## 구현사항
 - [x] GitHub 계정 연동
 - [x] 사용자 평점 기능
 - [x] 관심사 기반 피드

## 개발 시작하기 전에
**에디터: vscode, 파이썬: 3.7**
1. 마이크로소프트 스토어에서 파이썬 3.7 다운로드
2. `git clone https://github.com/5d-jh/circruit.git`로 클론 후 깃허브 아이디, 비밀번호 입력
3. 프로젝트 폴더로 이동 후 `python3 -m venv venv`실행
4. `.vscode\settings.json`에서 `python.pythonPath`값을 `venv\\Scripts\\python.exe`로 설정
5. `venv\Scripts\activate.bat` 실행
6. `pip install -r requirements.txt` 실행
7. vscode의 왼쪽 debug 탭 클릭 후 상단에 플레이 버튼 클릭

## 데이터베이스 모델
```
컬렉션명 {
    설명 "필드명": 데이터 타입
}
```

```
users {
    사용자 이름 "username": String,
    참여한 프로젝트 "joined_projects": [{
        "name": String,
        "status": String
    }]
    사용자 개발 스택 "dev_stacks": [String],
    깃허브 프로필 사진 "avatar_url": String,
    깃허브 프로필 바이오 "bio": String,
    연락처 "contacts": String,
    사용자 랭크 "rank": Number
}

projects {
    프로젝트 이름 "name": String,
    프로젝트 개발스택 "proj_stacks": [String],
    팀장 정보 "owner": users,
    프로젝트 상태 "status": "end"|"recruiting"|"ongoing",
    할 일 "todos": [{
        완료(closed) 여부 "is_closed": Boolean,
        평가한 사람 "voted": [String],
        평가 "vote": {
            긍정적 평가 "good": Number,
            부정적 평가 "bad": Number
        },
        기한 "deadline": String<"yyyy-mm-dd">,
        이슈 제목 "title": String,
        이슈 링크 "link": String,
        배정받은 멤버 이름(GitHub username) "assignees": {
            사용자 이름 "username": String,
            깃허브 프로필 사진 "avatar_url": String
        }
    }],
    참여한 사용자 정보 리스트 "collaborators": [{
        사용자 정보 "collaborator": users,
        프로젝트에서 평가된 점수 "project_rank": Number
    }]
}

devstacks {
    개발 스택 이름 "name": String
}
```
