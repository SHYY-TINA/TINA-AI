import ast
import json

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from collections import defaultdict, deque
from AIModule import AI
import re

app = FastAPI()

def parse_kakao_chat(text, max_count=100):
    speakers = defaultdict(lambda: deque(maxlen=max_count))
    msg_pattern = re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4}) (\d{1,2}:\d{2}), ([^:]+) : (.*)')
    skip_messages = {"사진", "삭제된 메시지입니다.", "이모티콘"}

    for line in text.splitlines():
        for match in msg_pattern.finditer(line):
            date, time, name, message = match.groups()
            if message in skip_messages:
                continue
            speakers[name].append({
                "message": message
            })
    return {name: list(msgs) for name, msgs in speakers.items()}

@app.get("/health", tags=["Healthcheck"])
async def healthcheck():
    return JSONResponse(content={"status": "ok"})

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    userNickname: str = Form(...),
    userMBTI: str = Form(...),
    partnerName: str = Form(...),
    partnerMBTI: str = Form(...)
):
    text = (await file.read()).decode("utf-8", errors="ignore")
    speakers = parse_kakao_chat(text, max_count=100)

    raw = AI(
        userNickname=userNickname,
        userMBTI=userMBTI,
        partnerName=partnerName,
        partnerMBTI=partnerMBTI,
        chat_dict={
            userNickname: speakers.get(userNickname, []),
            partnerName: speakers.get(partnerName, [])
        }
    )

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        inner = ast.literal_eval(raw)
        data = json.loads(inner)

    return JSONResponse(content=data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
