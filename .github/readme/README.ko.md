<p align="center">
  <strong>Attention Control</strong><br>
  <em>항공 교통 관제의 규율을 AI 출력에.</em>
</p>

<p align="center">
  <a href="../../README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <strong>한국어</strong> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt-BR.md">Português (BR)</a>
</p>

## 설치

<details open>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add aaddrick/attention-control
claude plugin install attention-control@attention-control
```

그다음 `/config`를 실행하고 **Output style**에서 **Attention Control**을 선택하세요.
`/clear` 또는 다음 세션부터 적용됩니다.

메뉴를 건너뛰려면 `~/.claude/settings.json`에 다음을 추가하세요.

```json
{ "outputStyle": "Attention Control" }
```

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add aaddrick/attention-control --ref main
codex plugin add attention-control@attention-control
```

그다음 `$attention-control`을 입력해 스타일을 적용하세요.

</details>

<details>
<summary><strong>Cursor, Gemini CLI, 수동 설치</strong></summary>

[INSTALL.md](../../INSTALL.md)를 참고하세요.

</details>

## 무엇을 하는가

항공 교통 관제 용어가 존재하는 이유는 하나입니다. 부하가 걸린 사람은 지시를 잘못
듣습니다. 항공 업계는 두 가지 규율로 이 문제를 해결했습니다. 통제된 어휘는 한 단어에
한 가지 뜻만 부여합니다. 고정된 문장 구조는 지시를 앞에, 배경을 뒤에 둡니다.

이 스타일은 같은 두 규율을 코딩 에이전트에 적용합니다. 에이전트는 바로 실행할 수 있는
동작을 먼저 제시하고, 한 단어가 한 가지 뜻만 갖도록 각 문장을 씁니다.

## 무엇이 달라지는가

<table>
<tr>
<td width="50%">

### 이전

> 좋은 질문입니다! 한번 살펴보겠습니다. 인증 흐름에는 여러 요소가 얽혀 있는 것
> 같습니다. `src/auth.ts`를 보면 토큰 검증 로직이 더 이상 권장되지 않는 API를
> 사용하고 있을 수 있습니다. 42~58행 근처의 `verifyToken` 함수가 예전
> `jsonwebtoken` 시그니처에 맞춰 구현된 것으로 보입니다. 고려해 볼 만한 방법 중
> 하나는 패키지를 업데이트하고 그 함수를 리팩터링하는 것입니다. 참고로 전반적인
> 의존성 버전도 언젠가 한 번 점검하시면 좋을 것 같습니다. 도움이 되었으면
> 좋겠습니다! 더 자세히 파고들고 싶은 부분이 있으면 알려 주세요.

</td>
<td width="50%">

### 이후

> `npm install jsonwebtoken@latest`를 실행한 다음 `src/auth.ts:42`를 편집하세요.
>
> 1. `src/auth.ts`를 엽니다
> 2. `verifyToken`(42~58행)을 아래 코드로 교체합니다
> 3. `npm test -- auth.spec.ts`를 실행합니다
>
> 예전 시그니처가 실패의 원인입니다. `jsonwebtoken` v9는 47행이 사용하는 콜백
> 형식을 제거했습니다.
>
> 다음: 테스트가 실패하면 첫 번째 오류 줄을 붙여 넣으세요.

</td>
</tr>
</table>

## 두 개의 층

**형태**는 무엇을 어떤 순서로 말할지 정합니다. 규칙 10개.

1. 다음 동작으로 시작한다.
2. 여러 단계 작업에 번호를 매긴다.
3. 구체적인 다음 동작 하나로 끝낸다.
4. 곁가지를 억제한다.
5. 매 턴마다 상태를 다시 말한다.
6. 소요 시간은 구체적인 단위로 제시한다.
7. 지금 무엇이 동작하는지 보여 준다.
8. 오류는 담담하게 서술한다.
9. 목록은 5개까지만 쓴다.
10. 서두도, 요약도, 마무리 인사도 없다.

**언어**는 각 문장을 어떻게 쓸지 정합니다.

- 한 단어에 한 가지 뜻. 한 동작에 한 동사. 동의어를 돌려쓰지 않는다.
- 표준 동사: check, make sure, start, stop, use, show, find, change, remove, need.
- 능동태를 쓰고 행위자를 밝힌다.
- 단순 시제만 쓴다. 완료 시제도, 조동사 중첩도 쓰지 않는다.
- 지시문은 문장당 20단어, 설명은 25단어까지. 명사 나열은 3단어까지.

전문은 [`output-styles/attention-control.md`](../../output-styles/attention-control.md)에 있습니다.

## 절대 건드리지 않는 것

코드, 명령, 파일 경로, 식별자, 오류 메시지, 인용문은 글자 하나까지 그대로 옮깁니다.
이 스타일은 에이전트가 직접 쓰는 산문만 다룹니다.

정확성이 간결함보다 우선합니다. 문장을 줄이려고 사실, 숫자, 조건, 적용 범위를 빼지
않습니다. 실제 불확실성을 담은 표현은 그대로 남깁니다.

## 평가

평가 하니스는 스타일을 적용하지 않은 기준선과 응답 품질을 비교합니다. 길이를 재지
않습니다.

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3
```

20개 사례, 6개 채점 항목, 그리고 정확성이나 안전성 퇴보를 막는 릴리스 게이트.
[evals/README.md](../../evals/README.md)를 참고하세요.

## 크레딧

이 스타일은 기존의 두 작업을 합친 것입니다. 두 저자 모두 이 프로젝트에 관여하지
않았습니다.

**형태 층:** Ayoub G.의 [`i-have-adhd`](https://github.com/ayghri/i-have-adhd)(MIT).
평가 하니스도 같은 프로젝트에서 파생되었습니다.

**언어 층:** [L1nefeed](https://github.com/L1nefeed)의
[`asd-ste100` 출력 스타일](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2).
그 자체가 [ASD-STE100](https://www.asd-ste100.org/) Simplified Technical English 9판을
압축한 것입니다.

이 프로젝트는 ASD 규격의 문장을 전혀 복제하지 않으며, 인증받거나 보증받거나
제휴하지 않았습니다. 자세한 내용은 [NOTICE.md](../../NOTICE.md)에 있습니다.

## 라이선스

MIT. [LICENSE](../../LICENSE)를 참고하세요.
