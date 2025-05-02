import re
import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

OPEN_WEB_UI_TOKEN = os.getenv('OPEN_WEB_UI_TOKEN')
BASE_URL = os.getenv('BASE_URL')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {OPEN_WEB_UI_TOKEN}'
}


def extract_json_array(text):
    pattern = re.compile(
        r"```json\s*(\[\s*\{(?:.|\n)*?\}\s*\])\s*```",
        re.DOTALL
    )

    match = pattern.search(text)
    if match:
        return json.loads(match.group(1))
    else:
        print("❌ JSON 블록을 찾을 수 없습니다.")
        return None


def format_duration(seconds: float) -> str:
    if seconds >= 60:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}분 {secs:.2f}초"
    return f"{seconds:.2f}초"


def format_duration(seconds: float) -> str:
    if seconds >= 60:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}분 {secs:.2f}초"
    return f"{seconds:.2f}초"

def AI(userNickname, userMBTI, partnerName, partnerMBTI, chat_dict):
    total_start = time.time()
    print("📤 채팅 데이터 기반 분석 시작")

    try:
        mbti_template = [
            {
                "type": "user",
                "mbti": userMBTI,
                "name": userNickname,
                "chat": [msg['message'] for msg in chat_dict.get(userNickname, [])]
            },
            {
                "type": "observer",
                "mbti": partnerMBTI,
                "name": partnerName,
                "chat": [msg['message'] for msg in chat_dict.get(partnerName, [])]
            }
        ]
        print("📝 MBTI 템플릿 생성 완료")

        api_url = f"{BASE_URL}/api/chat/completions"
        final_payload = {
            "model": "deepseek-r1:14b-qwen-distill-q4_K_M",
            "messages": [{
                "role": "user",
                "content": json.dumps(mbti_template, ensure_ascii=False) + '''
                
                [{"type": "user","charmScore": 0~100 사이의 감정 점수,"feedbackTitle": "감정적 소통에 대한 한 줄 요약 피드백","feedbackContent": "감정적 소통에 대한 상세 피드백","charmPointTitle": "감정적 매력 포인트 한 줄 요약","charmPointContent": ["감정적 매력 포인트에 대한 구체적 설명 (3개 이상)"],"chat": [{"text": "실제 발화 메시지","meaning": "해당 메시지의 감정적 의미 해석"}// 총 3-5개]},{"type": "observer","charmScore": 0~100 사이의 감정 점수,"feedbackTitle": "감정적 소통에 대한 한 줄 요약 피드백","feedbackContent": "감정적 소통에 대한 상세 피드백","tipTitle": "더 가까워질 수 있는 팁의 제목","tipContent": ["더 가까워질 수 있는 구체적 팁 (3개 이상)"],"cautionTitle": "주의해야 할 점의 제목","cautionContent": ["주의해야 할 점에 대한 구체적 설명 (3개 이상)"],"chat": [{"text": "실제 발화 메시지","meaning": "해당 메시지의 감정적 의미 해석"}// 총 3-5개]}]
                
                이 형식 외에 다른 필드가 들어가면 안되
                모든 설명, 분석, 피드백, 조언, 주의사항 등은 반드시 한국어 또는 영어로만 작성할 것.
                중요: JSON 키값에는 영어, 벨류값에는 영어로만 작성해야해
                채팅은 둘 다 있어야 하고 무조건 3개 이상 이어야해
                이 형식을 무조건 지켜서 JSON 형식으로 알려줘
                '''
            }]
        }
        final_api_start = time.time()
        print("🛰️  최종 분석 요청 전송")
        final_response = requests.post(
            api_url,
            headers=headers,
            json=final_payload
        )
        final_api_duration = time.time() - final_api_start
        print(f"⏱️ 최종 API 응답 시간: {format_duration(final_api_duration)}")
        print("📨 최종 응답 수신 완료")

        response_data = final_response.json()
        raw_content = response_data['choices'][0]['message']['content']
        print("🟢 최종 응답 content:")
        result = extract_json_array(raw_content)
        total_duration = time.time() - total_start
        print(f"\n✅ 총 소요 시간: {format_duration(total_duration)}")
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        total_duration = time.time() - total_start
        print(f"\n🚨 에러 발생 시 경과 시간: {format_duration(total_duration)}")
        print(f"🚨 분석 오류: {str(e)}")
        raise
