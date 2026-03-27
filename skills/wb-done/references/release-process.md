# Release Process (Code Type)

wb-done(code) 실행 시 자동 검증되는 체크리스트입니다.

## 체크리스트

### 1. 코드 품질
- [ ] lint 통과
- [ ] type-check 통과
- [ ] build 성공

### 2. 테스트
- [ ] 기존 테스트 통과 (회귀 없음)
- [ ] 신규 코드 테스트 작성
- [ ] 커버리지 >= 80% (신규 코드)

### 3. 커밋
- [ ] Conventional Commits 형식
- [ ] 민감 정보 미포함
- [ ] 불필요한 파일 미포함

### 4. 문서
- [ ] README 갱신 필요 여부 확인
- [ ] 마이그레이션 파일 필요 여부 확인
- [ ] 버전 범프 필요 여부 확인

## wb-done 실행 흐름

```
/wb-done (code)
├─ [1] wb-check 자동 호출 (Match Rate + Coverage)
├─ [2] Release 체크리스트 검증
│   ├─ ✅ 통과 → 완료 처리
│   └─ ⚠️ 미충족 → "진행하시겠습니까?" 확인
└─ [3] TASK.md 업데이트 + history 기록
```

## 레포별 커스터마이제이션

`.claude/config.json`에서 명령어 오버라이드:
```json
{
  "release-check": {
    "lint-cmd": "npm run lint",
    "test-cmd": "npm run test",
    "build-cmd": "npm run build",
    "coverage-min": 80
  }
}
```
