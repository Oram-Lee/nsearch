# 🏢 네이버 부동산 상업용 크롤러

네이버 부동산에서 상업용 부동산 매물 정보를 검색하고 엑셀로 다운로드할 수 있는 웹 애플리케이션입니다.

## ⚡ 빠른 시작

**처음 사용하시나요?** → [START_HERE.md](./START_HERE.md) 먼저 읽어보세요!

```bash
# 5분 안에 시작하기
pip install -r requirements.txt
python app.py
# http://localhost:5000 접속
```

## ✨ 주요 기능

- 🔍 **지역별 검색**: 서울시 25개 구 선택 가능
- 🏢 **부동산 구분**: 사무실, 상가, 건물, 지식산업센터
- 💰 **거래 유형**: 매매, 전세, 월세, 단기임대
- 📐 **면적 필터링**: 평 단위로 최소/최대 면적 설정
- 📊 **실시간 결과**: 웹에서 바로 확인 가능
- 📥 **엑셀 다운로드**: 검색 결과를 Excel 파일로 저장

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/naver-realestate-crawler.git
cd naver-realestate-crawler
```

### 2. 가상환경 생성 및 활성화

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

```bash
python app.py
```

### 5. 브라우저에서 접속

```
http://localhost:5000
```

## 📦 배포하기

### Render.com 배포 (추천)

1. [Render.com](https://render.com) 가입
2. New Web Service 클릭
3. GitHub 저장소 연결
4. 설정:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3

### Railway 배포

1. [Railway.app](https://railway.app) 가입
2. New Project > Deploy from GitHub
3. 저장소 선택 및 배포

### Vercel 배포

1. `vercel.json` 파일 생성:
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

2. Vercel CLI로 배포:
```bash
npm i -g vercel
vercel
```

## 🛠️ 기술 스택

### Backend
- **Flask**: Python 웹 프레임워크
- **Pandas**: 데이터 처리
- **Requests**: HTTP 통신
- **OpenPyXL**: Excel 파일 생성

### Frontend
- **HTML5**: 구조
- **CSS3**: 스타일링 (Gradient, Flexbox, Grid)
- **Vanilla JavaScript**: 인터랙션

## 📋 사용 방법

1. **지역 선택**: 드롭다운에서 원하는 서울시 구 선택
2. **부동산 구분**: 사무실, 상가, 건물, 지식산업센터 중 선택
3. **거래 유형**: 매매, 전세, 월세, 단기임대 중 선택
4. **면적 설정**: 최소/최대 평수 입력
5. **검색**: 검색하기 버튼 클릭
6. **결과 확인**: 테이블에서 매물 정보 확인
7. **다운로드**: 엑셀 다운로드 버튼으로 파일 저장

## 🔧 커스터마이징

### 지역 추가

`app.py`의 `REGION_COORDS` 딕셔너리에 새로운 지역 코드와 좌표 추가:

```python
REGION_COORDS = {
    "1168000000": {"name": "강남구", "lat": 37.5172, "lon": 127.0473},
    # 여기에 새로운 지역 추가
}
```

### API 설정 변경

크롤링 속도 조절 (`app.py`):

```python
time.sleep(random.uniform(1, 2))  # 대기 시간 조절
```

최대 페이지 수 변경:

```python
while len(all_results) < max_results and page <= 10:  # 10을 원하는 숫자로 변경
```

## ⚠️ 주의사항

- 네이버 부동산 API는 공식 API가 아니므로 구조가 변경될 수 있습니다
- 과도한 요청은 IP 차단의 원인이 될 수 있습니다
- 개인적인 용도로만 사용하세요

## 📄 라이선스

MIT License

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 문의

문제가 발생하거나 제안사항이 있으시면 Issue를 등록해주세요.

---

Made with ❤️ by Oram
