<p align="center">
  <strong>Attention Control</strong><br>
  <em>用空中交通管制的纪律来约束 AI 的输出。</em><br>
  <em>为 ADHD 读者而写。</em>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/aaddrick/attention-control?style=flat" alt="License"></a>
  <a href="../workflows/plugin-load-check.yml"><img src="https://img.shields.io/github/actions/workflow/status/aaddrick/attention-control/plugin-load-check.yml?label=plugin%20loads&style=flat" alt="Plugin load check"></a>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/aaddrick/">在 LinkedIn 上联系我！</a>
</p>

<p align="center">
  <a href="../../README.md">English</a> ·
  <strong>简体中文</strong> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt-BR.md">Português (BR)</a>
</p>

## 安装

<details open>
<summary><strong>Claude Code</strong></summary>

只有 Claude Code 带原生输出风格位。在终端里运行这两条命令：

```bash
claude plugin marketplace add aaddrick/attention-control
```

```bash
claude plugin install attention-control@attention-control
```

然后运行 `/config`，选择 **Output style**，再选 **Attention Control**。执行
`/clear` 或开启新会话后生效。

想跳过选择菜单，就把 `outputStyle` 加入 `~/.claude/settings.json`。它是顶层键，
不要放进 `env`、`permissions` 或其他块里：

```json
{
  "model": "opus",
  "env": { "EXAMPLE_VAR": "1" },
  "outputStyle": "Attention Control"
}
```

`model` 和 `env` 代表你可能已经有的键。保留它们，把 `outputStyle` 这一行加在
旁边。

只想用一个会话，就调用插件同时提供的技能：

```
/attention-control:attention-control
```

说 “stop attention control” 即可关闭。

</details>

<details>
<summary><strong>Codex</strong></summary>

Codex 没有输出风格位，所以这套规则以技能形式发布。

```bash
codex plugin marketplace add aaddrick/attention-control --ref main
```

```bash
codex plugin add attention-control@attention-control
```

在 Codex 内部，`/plugins` 打开插件浏览器。

新开一个线程，然后输入技能：

```
$attention-control:attention-control
```

Codex 会在插件技能名前加上插件名。说 “stop attention control” 即可关闭。想每一轮
都生效，就把 [INSTALL.md](../../INSTALL.md#the-always-on-snippet) 里的常驻片段写入
`~/.codex/AGENTS.md`。

</details>

<details>
<summary><strong>Cursor、Gemini CLI、Copilot、Zed 和手动安装</strong></summary>

见 [INSTALL.md](../../INSTALL.md)。它们都没有输出风格位，所以这套规则以技能、
规则文件或 `AGENTS.md` 段落的形式发布。走技能这条路时，输入
`/attention-control`，说 “stop attention control” 即可关闭。

</details>

## 它做什么

空中交通管制的标准用语只为一个目的存在：注意力被占满的人会听错指令。航空业用
两条纪律解决了这个问题。受控词汇让每个词只有一个含义。固定的信息结构把指令放在
最前面，把背景放在最后面。

这个风格把这两条纪律用在你的编程助手上。助手先给出你能直接运行的动作，再让每个
句子做到一词一义。

这个风格只针对一类读者：有 ADHD 的读者。结构层的规则正是从这类读者来的。见
[结构规则从何而来](#结构规则从何而来)。

## 变化在哪里

<table>
<tr>
<td width="50%">

### 之前

> 好问题！让我看一下。你的认证流程涉及好几个部分。看 `src/auth.ts`，令牌验证
> 逻辑可能用了已废弃的 API —— 第 42 到 58 行的 `verifyToken` 函数似乎是按旧版
> `jsonwebtoken` 的签名实现的。一种可以考虑的方式是升级这个包并重构该函数。
> 顺便说一句，你的依赖版本整体上或许也该抽时间检查一下。希望这些有帮助！如果你
> 想深入了解其中任何一部分，随时告诉我。

</td>
<td width="50%">

### 之后

> 运行 `npm install jsonwebtoken@latest`。
>
> 我改了 `src/auth.ts:47`。`verifyToken` 现在写明算法：
>
> `jwt.verify(token, secret, { algorithms: ["HS256"] }, callback);`
>
> 运行 `npm test -- auth.spec.ts`。大约 10 秒。
>
> 旧的调用没有写明算法。`jsonwebtoken` v9 拒绝未签名的令牌，除非你传入
> `algorithms: ["none"]`。
>
> 下一步：如果测试失败，把第一行报错贴过来。

</td>
</tr>
</table>

## 两个层次

**结构层**决定说什么、按什么顺序说。共 11 条：

1. 以下一个动作开头。
2. 属于自己的活自己干完。
3. 多步骤工作要编号。
4. 以一个具体的下一步结束。
5. 抑制离题内容。
6. 每一轮都重述当前状态。
7. 时间估计用具体单位。
8. 说明现在什么能用了。
9. 平铺直叙地报告错误。
10. 列表最多 5 项。
11. 不要开场白、不要复述、不要客套结尾。

**语言层**决定每个句子怎么写：

- 一词一义，一个动作一个动词。不要轮换同义词。
- 标准动词：check、make sure、start、stop、use、show、find、change、remove、need。
- 使用主动语态，点明动作的执行者。
- 只用简单时态。不用完成时，不叠加助动词。
- 指令每句最多 20 词，说明每句最多 25 词。名词串最多 3 个词。

完整文本见 [`output-styles/attention-control.md`](../../output-styles/attention-control.md)。

## 结构规则从何而来

关于 ADHD 阅读的五个事实，推导出全部 11 条结构规则。下表中每个事实都标注了它
产生的规则。

| 事实 | 助手怎么做 |
|---|---|
| **工作记忆很小。** 不在屏幕上的内容等于不存在。 | 它从不写"请记住 X"。它每一轮都重述状态："第 3 步（共 5 步）完成：我改了 schema。下一步：运行 `scripts/backfill.py`。"（规则 6、10） |
| **知道答案不等于做完答案。** 工作就死在这两者之间的缝隙里。 | 它把属于自己的活干完，而不是甩回给读者。它给命令，不给标签。"补上缺失的请求头"是标签。`Authorization: Bearer ${token}` 才是修复。（规则 1、2、3） |
| **开始是最难的一步。** | 第一行必须小、明确、现在就能做。最后一行只给一个两分钟内能做完的动作。"打开文件"就算数。（规则 1、4） |
| **时间估计听起来都一样。** "一点工作量"和"几个小时"在感受上没有区别。 | 它写"如果测试覆盖到了，大概 15 分钟；如果没有，要一个下午"。它从不写"一些工作"。（规则 7） |
| **多巴胺很稀缺。** 被埋起来的成果不会被感知到。 | 改完之后，它用具体的话说明结果："魔法链接登录已经能用了。运行 `npm run dev` 并打开 `/login`。"（规则 8） |

还有两条规则保护注意力本身。规则 5 抑制离题，让一条待办线索始终只是一条。规则
11 去掉开场白和客套结尾，让答案从第一行开始。

所以这个风格不等于"说得短"。为了短而丢掉命令、数字或条件，会让读者多跑一个
来回，而一个来回就可能弄丢整条思路。规则 9 出自同样的逻辑：报错要给位置、原因
和修复，前面不加"哎呀"。惊慌不是信息，它还要和信息抢同一份注意力。

不需要 ADHD 诊断也能从中受益。疲惫的读者、用手机看的读者、开着 40 个标签页的
读者，读法都一样。

## 它从不改动什么

代码、命令、文件路径、标识符、报错信息和引用文本一律逐字保留，一个字符都不改。
这个风格只约束助手自己写的散文，别的都不碰。

准确性优先于简洁。规则不会为了缩短句子而删掉事实、数字、条件或适用范围。带有
真实不确定性的措辞会保留。

## 评测

评测工具把回答质量和未加风格的基线作对比，而不是比较长度。

```bash
python3 scripts/run_evals.py validate
```

```bash
python3 scripts/run_evals.py plan --trials 3
```

24 个用例、6 个评分维度，以及一道会拦截正确性或安全性退步的发布闸门。

判分器是最薄弱的一环，所以评测工具专门针对它。`blind` 隐藏条件并平衡位置。
判分器把每一组打两遍分，第二遍把顺序颠倒，然后报告两遍结果的分歧率。运行器
在空目录里跑，不读你的任何配置。设计说明和支撑它的实测数据见
[evals/README.md](../../evals/README.md)。

## 自己调

Fork 之后编辑 `output-styles/attention-control.md`，然后重新生成每个面向具体
助手的副本：

```bash
python3 scripts/sync_style.py
```

换成你自己的版本，一条一条运行：

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

## 致谢

这个风格由两个已有作品组合而成。两位作者都没有参与本项目。

**结构层：** Ayoub G. 的 [`i-have-adhd`](https://github.com/ayghri/i-have-adhd)（MIT）。
评测工具同样源自该项目。

**语言层：** [L1nefeed](https://github.com/L1nefeed) 的
[`asd-ste100` 输出风格](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2)，
它本身是对 [ASD-STE100](https://www.asd-ste100.org/) 简化技术英语第 9 版的浓缩。

本项目不复制 ASD 规范的任何文本，也未获得其认证、背书或关联。详见
[NOTICE.md](../../NOTICE.md)。

## 许可

MIT。见 [LICENSE](../../LICENSE)。
