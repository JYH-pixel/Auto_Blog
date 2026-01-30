# 파일명: main.py
import os
import arxiv
import openai
import requests
import base64
import io
from datetime import datetime

# -----------------------------------------------------------
# [보안 설정] GitHub Secrets에서 값을 가져옵니다.
# -----------------------------------------------------------
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    WP_URL = os.environ["WP_URL"]
    WP_USERNAME = os.environ["WP_USERNAME"]
    WP_APP_PASSWORD = os.environ["WP_APP_PASSWORD"]
except KeyError:
    print("❌ 에러: GitHub Secrets(환경변수)가 설정되지 않았습니다.")
    exit(1)
SEARCH_TOPIC = "Large Language Models" # 검색 주제

# (아래 코드는 이전과 동일하므로 생략하지 않고 전체가 필요하지만, 
#  교수님이 Colab에서 성공한 그 로직 그대로입니다. 
#  환경변수 설정 외에는 바뀐 게 없습니다.)

# ... (중략: step1, step2, step3, step4 함수들) ...
# 교수님 편의를 위해 전체 코드를 다시 드리지 않아도, 
# 위 4줄만 바꾸시면 됩니다! 하지만 헷갈리실 수 있으니 
# 이 답변 맨 아래에 '복사 붙여넣기용 전체 코드'를 다시 드리겠습니다.
# 1. 필수 라이브러리 설치 (Colab에서 최초 1회 실행 필요, 이미 되어있다면 주석 처리)
# !pip install arxiv openai requests

# 전역 인증 헤더 설정
credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
token = base64.b64encode(credentials.encode())
WP_HEADERS = {
    "Authorization": f"Basic {token.decode('utf-8')}"
}

def step1_fetch_paper(topic):
    """[1단계] arXiv에서 최신 논문 1개를 가져옵니다."""
    print(f"\n🔍 [1단계] '{topic}' 관련 최신 논문을 검색 중입니다...")
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic, 
        max_results=1, 
        sort_by=arxiv.SortCriterion.SubmittedDate, 
        sort_order=arxiv.SortOrder.Descending
    )
    
    try:
        paper = next(client.results(search))
        print(f"   -> 논문 발견: {paper.title}")
        return {
            "title": paper.title, 
            "summary": paper.summary.replace("\n", " "), 
            "authors": ", ".join([a.name for a in paper.authors]), 
            "link": paper.entry_id, 
            "pdf": paper.pdf_url
        }
    except StopIteration:
        print("❌ 논문을 찾을 수 없습니다.")
        return None

def step2_generate_blog_text(paper_data):
    """[2단계-글] AI가 논문을 분석하여 HTML 글을 작성합니다."""
    print("🤖 [2단계-글] AI가 내용을 분석하고 글을 쓰고 있습니다... (약 1분 소요)")
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    system_prompt = r"""
    당신은 컴퓨터 공학 교수입니다. 최신 논문을 분석하여 기술 블로그에 올릴 글을 작성합니다.
    [필수 작성 규칙]
    1. 독자: 대학원생 및 현업 엔지니어
    2. 언어: 한국어 (전문 용어는 영어 병기)
    3. 형식: HTML 태그(h2, p, ul, li, blockquote)만 사용. (마크다운 금지)
    
    [⭐️ 수식 규칙 ⭐️]
    1. 인라인 수식: 반드시 \( ... \) 형식 사용.
    2. 블록 수식: 반드시 $$...$$ 형식 사용.
    3. $ 기호 단독 사용 금지.
    
    [구조]
    - 서론, 핵심 알고리즘(수식 포함), 결론
    - 마지막에 반드시 '📚 참고 문헌 및 출처' 섹션을 만들고 논문 원문 링크를 HTML 링크 태그로 포함할 것.
    """
    
    user_prompt = f"논문 제목: {paper_data['title']}\n요약: {paper_data['summary']}\n원문 링크: {paper_data['link']}\n\n위 논문을 분석하여 블로그 포스팅을 작성해 주세요."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_prompt}
            ]
        )
        # 마크다운 껍데기 제거
        return response.choices[0].message.content.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        print(f"❌ AI 글 생성 오류: {e}")
        return None

def step2_generate_blog_text(paper_data):
    print("🤖 [2단계-글] AI가 내용을 분석하고 글을 쓰고 있습니다...")
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    # ---------------------------------------------------------
    # [SEO 피드백 반영 완료]
    # 1. 실제 예시 추가 요청 -> "예시: ..." 섹션 강제
    # 2. 제목 명확화 -> h2 태그에 구체적 내용 포함 지시
    # 3. 비전공자 배려 -> 기술 용어 설명(Glossary) 추가
    # 4. 결론 보강 -> 실질적 적용 사례(Use Case) 및 미래 전망 포함
    # 5. 출처 통일 -> 참고 문헌 포맷 표준화
    # ---------------------------------------------------------
    
    system_prompt = r"""
    당신은 컴퓨터 공학 교수이자 베스트셀러 기술 작가입니다. 최신 논문을 분석하여 기술 블로그에 올릴 글을 작성합니다.
    
    [핵심 작성 전략: SEO 및 독자 친화성]
    1. **풍부한 예시**: 추상적인 개념 설명 후에는 반드시 "예를 들어..."를 사용하여 현실 세계의 구체적인 사례(Use Case)를 덧붙이세요.
    2. **용어 풀이**: 어려운 전문 용어가 나오면 괄호 안에 간단한 설명을 추가하거나, 글 중간에 '💡 용어 설명' 섹션을 활용하세요.
    3. **명확한 소제목**: 단순히 '서론', '본론'이라고 쓰지 말고, '왜 이 기술이 필요한가?', 'RedSage의 핵심 아키텍처 분석'과 같이 구체적이고 흥미로운 제목(h2)을 사용하세요.
    
    [작성 포맷 규칙]
    1. 형식: HTML 태그(h2, h3, p, ul, li, blockquote)만 사용. (마크다운 ``` 금지)
    2. 수식: 인라인 수식은 \( ... \), 블록 수식은 $$...$$ 형식을 엄격히 준수.
    
    [글의 구조 가이드]
    1. **도입부**: 이 연구가 왜 중요한지 비유나 실제 문제 상황을 들어 설명하세요.
    2. **핵심 기술 심층 분석**: 알고리즘과 수식을 설명하되, 이것이 실제로 어떻게 작동하는지 단계별로 풀어서 서술하세요.
    3. **실제 적용 사례 (필수)**: 이 기술이 실제 산업이나 서비스에 적용된다면 어떤 모습일지 구체적인 시나리오를 제시하세요.
    4. **결론 및 미래 전망**: 단순 요약이 아니라, 이 기술의 한계점과 향후 발전 방향(Future Work)을 통찰력 있게 제시하세요.
    5. **참고 문헌**: 마지막에 <ul> 태그를 사용하여 저자, 제목, 연도, 링크 순으로 포맷을 통일하여 나열하세요.
    """
    
    user_prompt = f"""
    분석할 논문 정보:
    - 제목: {paper_data['title']}
    - 요약: {paper_data['summary']}
    - 링크: {paper_data['link']}
    
    위 논문을 바탕으로 SEO에 최적화된 블로그 포스팅을 작성해 주세요. 
    특히 '실제 적용 예시'를 풍부하게 포함하여 독자의 이해를 높여주세요.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_prompt}
            ]
        )
        # 마크다운 껍데기 제거
        return response.choices[0].message.content.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        print(f"❌ AI 글 생성 오류: {e}"); return None

def step3_upload_media(image_data, title):
    """[3단계-업로드] 이미지를 워드프레스 서버로 전송하고 ID와 URL을 반환합니다."""
    print("📤 [3단계-업로드] 이미지를 워드프레스 서버로 전송 중입니다...")
    
    media_url = f"{WP_URL}/wp-json/wp/v2/media"
    headers = WP_HEADERS.copy()
    headers["Content-Type"] = "image/png"
    headers["Content-Disposition"] = f'attachment; filename="{title[:20].replace(" ","_")}_thumbnail.png"'
    
    try:
        response = requests.post(media_url, headers=headers, data=image_data.getvalue())
        if response.status_code == 201:
            data = response.json()
            media_id = data['id']
            image_src_url = data['source_url']
            print(f"   -> 이미지 업로드 성공 (ID: {media_id})")
            return media_id, image_src_url
        else: 
            print(f"❌ 이미지 업로드 실패: {response.text}")
            return None, None
    except Exception as e: 
        print(f"❌ 미디어 업로드 연결 오류: {e}")
        return None, None

def step4_upload_post(title, content, media_id=None):
    """[4단계-최종] 글과 이미지를 합쳐서 워드프레스에 임시저장합니다."""
    print("🚀 [4단계-최종] 완성된 포스팅을 워드프레스로 전송합니다...")
    
    posts_url = f"{WP_URL}/wp-json/wp/v2/posts"
    headers = WP_HEADERS.copy()
    headers["Content-Type"] = "application/json"
    
    post_data = {
        "title": f"[논문리뷰] {title}", 
        "content": content, 
        "status": "draft" # 안전하게 임시저장
    }
    
    if media_id:
        post_data["featured_media"] = media_id
        
    try:
        response = requests.post(posts_url, headers=headers, json=post_data)
        if response.status_code == 201:
            print("\n🎉 모든 작업 완료! 블로그에 글이 등록되었습니다.")
            print(f"🔗 확인 링크: {response.json()['link']}")
        else: 
            print(f"\n❌ 포스팅 전송 실패: {response.text}")
    except Exception as e: 
        print(f"\n❌ 포스팅 연결 오류: {e}")

# --- 메인 실행 흐름 ---
if __name__ == "__main__":
    # 1. 논문 수집
    paper = step1_fetch_paper(SEARCH_TOPIC)
    
    if paper:
        # 2. 글 작성 및 이미지 생성 (병렬 처리 대신 순차 처리로 안정성 확보)
        blog_html = step2_generate_blog_text(paper)
        image_data = step2_generate_image(paper)
        
        media_id = None
        media_url = None
        
        # 3. 이미지가 생성되었다면 업로드
        if image_data:
            media_id, media_url = step3_upload_media(image_data, paper['title'])
            
        # 4. 글 본문에 이미지 강제 삽입 및 최종 업로드
        if blog_html and blog_html.strip():
            if media_url:
                # 테마 무시하고 강제로 이미지 보여주기
                img_tag = f'<img src="{media_url}" alt="썸네일" style="width:100%; height:auto; margin-bottom:30px; border-radius:10px;">'
                blog_html = img_tag + blog_html 

            step4_upload_post(paper['title'], blog_html, media_id)
        else:
            print("❌ 생성된 글 내용이 비어있어 업로드를 중단합니다.")
