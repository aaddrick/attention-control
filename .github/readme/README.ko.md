<p align="center">
  <strong>Attention Control</strong><br>
  <em>항공 교통 관제의 규율을 AI 출력에.</em><br>
  <em>ADHD 독자를 위해 썼습니다.</em>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/aaddrick/attention-control?style=flat" alt="License"></a>
  <a href="../workflows/plugin-load-check.yml"><img src="https://img.shields.io/github/actions/workflow/status/aaddrick/attention-control/plugin-load-check.yml?label=plugin%20loads&style=flat" alt="Plugin load check"></a>
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

네이티브 출력 스타일 자리를 가진 에이전트는 Claude Code뿐입니다. 터미널에서 다음
두 명령을 실행하세요.

```bash
claude plugin marketplace add aaddrick/attention-control
```

```bash
claude plugin install attention-control@attention-control
```

Claude Code 안에서는 같은 두 단계가 슬래시 명령입니다.

```
/plugin marketplace add aaddrick/attention-control
```

```
/plugin install attention-control@attention-control
```

```
/reload-plugins
```

그다음 `/config`를 실행하고 **Output style**에서 **Attention Control**을 선택하세요.
`/clear` 또는 다음 세션부터 적용됩니다.

메뉴를 건너뛰려면 `~/.claude/settings.json`에 `outputStyle`을 추가하세요. 최상위
키입니다. `env`나 `permissions` 안에 넣지 않습니다.

```json
{
  "model": "opus",
  "env": { "EXAMPLE_VAR": "1" },
  "outputStyle": "Attention Control"
}
```

`model`과 `env`는 이미 가지고 있을 만한 키의 예입니다. 그대로 두고
`outputStyle` 줄을 그 옆에 추가하세요.

모든 세션이 아니라 한 세션만 적용하려면 플러그인이 함께 제공하는 스킬을
사용하세요.

```
/attention-control:attention-control
```

끄려면 "stop attention control"이라고 말하세요.

</details>

<details>
<summary><strong>Codex</strong></summary>

Codex에는 출력 스타일 자리가 없습니다. 그래서 이 규칙은 스킬로 제공됩니다.

```bash
codex plugin marketplace add aaddrick/attention-control --ref main
```

```bash
codex plugin add attention-control@attention-control
```

Codex 안에서는 `/plugins`가 플러그인 브라우저를 엽니다.

새 스레드를 시작한 뒤 스킬을 입력하세요.

```
$attention-control:attention-control
```

Codex는 플러그인 스킬 이름 앞에 플러그인 이름을 붙입니다. 끄려면 "stop attention
control"이라고 말하세요. 매 턴 적용하려면
[INSTALL.md](../../INSTALL.md#the-always-on-snippet)의 상시 적용 스니펫을
`~/.codex/AGENTS.md`에 넣으세요.

</details>

<details>
<summary><strong>Cursor, Gemini CLI, Copilot, Zed, 수동 설치</strong></summary>

[INSTALL.md](../../INSTALL.md)를 참고하세요. 모두 출력 스타일 자리가 없어서 이
규칙은 스킬, 규칙 파일, 또는 `AGENTS.md` 블록으로 제공됩니다. 스킬 경로에서는
`/attention-control`을 입력하고, 끄려면 "stop attention control"이라고 말하세요.

</details>

## 무엇을 하는가

항공 교통 관제 용어가 존재하는 이유는 하나입니다. 부하가 걸린 사람은 지시를 잘못
듣습니다. 항공 업계는 두 가지 규율로 이 문제를 해결했습니다. 통제된 어휘는 한 단어에
한 가지 뜻만 부여합니다. 고정된 문장 구조는 지시를 앞에, 배경을 뒤에 둡니다.

이 스타일은 같은 두 규율을 코딩 에이전트에 적용합니다. 에이전트는 바로 실행할 수 있는
동작을 먼저 제시하고, 한 단어가 한 가지 뜻만 갖도록 각 문장을 씁니다.

이 스타일이 겨냥하는 독자는 한 종류입니다. ADHD가 있는 독자입니다. 형태 규칙은 그
독자에서 나왔습니다. [형태 규칙이 나온 이유](#형태-규칙이-나온-이유)를 참고하세요.

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

**형태**는 무엇을 어떤 순서로 말할지 정합니다. 규칙 11개.

1. 다음 동작으로 시작한다.
2. 자기 몫의 일은 자기가 끝낸다.
3. 여러 단계 작업에 번호를 매긴다.
4. 구체적인 다음 동작 하나로 끝낸다.
5. 곁가지를 억제한다.
6. 매 턴마다 상태를 다시 말한다.
7. 소요 시간은 구체적인 단위로 제시한다.
8. 지금 무엇이 동작하는지 보여 준다.
9. 오류는 담담하게 서술한다.
10. 목록은 5개까지만 쓴다.
11. 서두도, 요약도, 마무리 인사도 없다.

**언어**는 각 문장을 어떻게 쓸지 정합니다.

- 한 단어에 한 가지 뜻. 한 동작에 한 동사. 동의어를 돌려쓰지 않는다.
- 표준 동사: check, make sure, start, stop, use, show, find, change, remove, need.
- 능동태를 쓰고 행위자를 밝힌다.
- 단순 시제만 쓴다. 완료 시제도, 조동사 중첩도 쓰지 않는다.
- 지시문은 문장당 20단어, 설명은 25단어까지. 명사 나열은 3단어까지.

전문은 [`output-styles/attention-control.md`](../../output-styles/attention-control.md)에 있습니다.

## 형태 규칙이 나온 이유

ADHD 독서에 관한 다섯 가지 사실이 형태 규칙 11개를 모두 만듭니다. 아래 표는 각
사실이 어떤 규칙을 낳는지 보여 줍니다.

| 사실 | 에이전트가 하는 일 |
|---|---|
| **작업 기억이 작다.** 화면에 없는 것은 없는 것과 같다. | "X를 기억해 두세요"라고 쓰지 않습니다. 매 턴 상태를 다시 말합니다. "5단계 중 3단계 완료: 스키마를 바꿨습니다. 다음: `scripts/backfill.py`를 실행하세요." (규칙 6, 10) |
| **답을 아는 것과 답을 실행하는 것은 다르다.** 일은 그 사이 틈에서 멈춘다. | 자기 몫의 일을 독자에게 넘기지 않고 직접 끝냅니다. 이름표가 아니라 명령을 줍니다. "빠진 헤더를 추가하세요"는 이름표입니다. `Authorization: Bearer ${token}`이 수정입니다. (규칙 1, 2, 3) |
| **시작이 가장 어려운 단계다.** | 첫 줄은 작고, 분명하고, 지금 바로 할 수 있습니다. 마지막 줄은 2분 안에 끝나는 동작 하나를 짚습니다. "파일을 여세요"도 해당합니다. (규칙 1, 4) |
| **시간 추정이 다 비슷하게 들린다.** "조금 걸려요"와 "몇 시간"이 똑같이 들린다. | "테스트가 덮고 있으면 15분쯤, 아니면 반나절"이라고 씁니다. "작업이 좀 있습니다"라고 쓰지 않습니다. (규칙 7) |
| **도파민이 부족하다.** 묻힌 성과는 와닿지 않는다. | 바꾼 뒤에는 결과를 구체적으로 말합니다. "매직 링크 로그인이 됩니다. `npm run dev`를 실행하고 `/login`을 여세요." (규칙 8) |

두 규칙이 주의력 자체를 지킵니다. 규칙 5는 곁가지를 눌러서 열린 작업 줄기를 하나로
유지합니다. 규칙 11은 서두와 마무리 인사를 없애서 답이 첫 줄에서 시작하게 합니다.

그래서 이 스타일은 "짧게 쓰기"가 아닙니다. 명령, 숫자, 조건을 버리는 간결함은
독자에게 왕복 한 번을 떠넘기고, 그 왕복이 작업 줄기를 끊습니다. 규칙 9도 같은
논리입니다. 오류에는 위치, 원인, 수정을 적고 앞에 "이런"을 붙이지 않습니다. 놀람은
정보가 아니며, 정보와 같은 주의력을 두고 다툽니다.

ADHD 진단이 있어야 도움이 되는 것은 아닙니다. 지친 독자, 휴대폰으로 읽는 독자,
탭 40개를 열어 둔 독자 모두 같은 방식으로 읽습니다.

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
```

```bash
python3 scripts/run_evals.py plan --trials 3
```

20개 사례, 6개 채점 항목, 그리고 정확성이나 안전성 퇴보를 막는 릴리스 게이트.

가장 약한 고리는 심사자라서 하니스가 그 지점을 겨냥합니다. `blind`는 조건을 감추고
제시 위치를 고르게 맞춥니다. 심사자는 각 묶음을 두 번 채점하고, 두 번째는 순서를
뒤집은 뒤, 두 결과가 얼마나 어긋나는지 보고합니다. 러너는 빈 디렉터리에서 돌고
여러분의 설정을 전혀 읽지 않습니다. 설계 근거와 측정값은
[evals/README.md](../../evals/README.md)에 있습니다.

## 직접 손보기

포크한 뒤 `output-styles/attention-control.md`를 편집하고, 에이전트별 사본을 다시
생성하세요.

```bash
python3 scripts/sync_style.py
```

자신의 사본으로 교체하세요. 한 번에 한 명령씩 실행합니다.

```bash
claude plugin uninstall attention-control
```

```bash
claude plugin marketplace remove attention-control
```

```bash
claude plugin marketplace add <your-username>/attention-control
```

```bash
claude plugin install attention-control@attention-control
```

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
