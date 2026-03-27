# wb-done: 활용 내역 표시

커맨드 실행 후 사용된 리소스를 표시:

### code 유형
```
📊 /wb-done 실행 완료
├─ 📦 Type: code
├─ 🤖 Agents: reviewer (haiku) - 변경사항 검토
├─ 💾 Memory: ai-memory 저장 (의사결정 2건)
├─ 📚 Skills: vault-conventions
├─ 🔧 Actions:
│   ├─ 변경사항 커밋
│   ├─ TASK.md 업데이트
│   └─ history/{date}.md 기록
└─ ⏱️ 소요: 8초
```

### ops 유형
```
📊 /wb-done 실행 완료
├─ 🔧 Type: ops
├─ 🤖 Agents: reviewer (haiku) - 작업 결과 검토
├─ 💾 Memory: ai-memory 저장 (의사결정 1건)
├─ 📚 Skills: vault-conventions
├─ 🛠️ Tools: n8n-mcp (사용됨)
├─ 🔧 Actions:
│   ├─ 결과물 저장 (artifacts/)
│   ├─ TASK.md 업데이트
│   └─ history/{date}.md 기록
└─ ⏱️ 소요: 5초
```

### wait 유형
```
📊 /wb-done 실행 완료
├─ ⏳ Type: wait
├─ 💾 Memory: ai-memory 저장 (결정사항 1건)
├─ 🔓 Unblocked: 2개 서브태스크
├─ 🔧 Actions:
│   ├─ 결정 사항 기록
│   ├─ TASK.md 업데이트
│   ├─ 의존 서브태스크 unblock
│   └─ history/{date}.md 기록
└─ ⏱️ 소요: 3초
```

### doc 유형
```
📊 /wb-done 실행 완료
├─ 📝 Type: doc
├─ 💾 Memory: ai-memory 저장 (문서 요약 1건)
├─ 🔧 Actions:
│   ├─ 문서 위치 기록
│   ├─ TASK.md 업데이트
│   └─ history/{date}.md 기록
└─ ⏱️ 소요: 2초
```

### research 유형
```
📊 /wb-done 실행 완료
├─ 🔍 Type: research
├─ 💾 Memory: ai-memory 저장 (조사 결론 1건)
├─ 📎 Artifacts: 1개 저장됨
├─ 🔧 Actions:
│   ├─ 결론/추천 기록
│   ├─ TASK.md 업데이트
│   └─ history/{date}.md 기록
└─ ⏱️ 소요: 3초
```
