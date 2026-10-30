# report-relay

암호화된 보고서를 텔레그램으로 보내는 전달용 저장소입니다.

- `outbox/*.cms` 는 공개키로 암호화된 파일이라 이 저장소를 봐도 내용을 읽을 수 없습니다.
- 푸시되면 `Send encrypted outbox` 워크플로가 시크릿 `RELAY_KEY`(비밀키)로 풀어서 텔레그램으로 한 번 보냅니다.
- 필요한 시크릿: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_IDS`, `RELAY_KEY`

## 수집 작업 (Run job)

- `jobs/queue/*.txt` 가 푸시되면 비공개 reports 저장소의 `jobs/*.py` 를 이 러너에서 실행하고, 결과를 reports 저장소 `jobs/out/` 에 커밋합니다.
- queue 파일 형식: `branch=<브랜치>` 와 `script=jobs/<이름>.py` (여러 줄 가능)
- 필요한 시크릿: `REPORTS_TOKEN` (reports 저장소 Contents 읽기·쓰기 권한만 있는 fine-grained 토큰)
