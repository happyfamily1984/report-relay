# report-relay

암호화된 보고서를 텔레그램으로 보내는 전달용 저장소입니다.

- `outbox/*.cms` 는 공개키로 암호화된 파일이라 이 저장소를 봐도 내용을 읽을 수 없습니다.
- 푸시되면 `Send encrypted outbox` 워크플로가 시크릿 `RELAY_KEY`(비밀키)로 풀어서 텔레그램으로 한 번 보냅니다.
- 필요한 시크릿: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_IDS`, `RELAY_KEY`
