<p align="center">
  <strong>Attention Control</strong><br>
  <em>航空管制の規律を、AI の出力に。</em>
</p>

<p align="center">
  <a href="../../README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <strong>日本語</strong> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <a href="README.pt-BR.md">Português (BR)</a>
</p>

## インストール

<details open>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add aaddrick/attention-control
claude plugin install attention-control@attention-control
```

次に `/config` を実行し、**Output style** から **Attention Control** を選びます。
`/clear` または次のセッションから有効になります。

メニューを使わずに設定するなら、`~/.claude/settings.json` に次を追加します。

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

そのあと `$attention-control` と入力してスタイルを適用します。

</details>

<details>
<summary><strong>Cursor、Gemini CLI、手動インストール</strong></summary>

[INSTALL.md](../../INSTALL.md) を参照してください。

</details>

## 何をするのか

航空管制の定型用語が存在する理由はひとつです。負荷の高い人間は指示を聞き違えます。
航空業界はこれを 2 つの規律で解決しました。統制された語彙が、1 つの語に 1 つの
意味だけを持たせます。固定された文型が、指示を先頭に、背景を末尾に置きます。

このスタイルは同じ 2 つの規律をコーディングエージェントに適用します。エージェントは
実行できるアクションを先に示し、1 語 1 義で各文を書きます。

## 何が変わるか

<table>
<tr>
<td width="50%">

### 変更前

> いい質問ですね！確認してみましょう。認証フローにはいくつかの要素が絡んでいる
> ようです。`src/auth.ts` を見ると、トークン検証のロジックが非推奨の API を使って
> いる可能性があります。42〜58 行目あたりの `verifyToken` 関数が、古い
> `jsonwebtoken` のシグネチャに対して実装されているようです。考えられる方法の
> ひとつは、パッケージを更新してその関数をリファクタリングすることでしょう。
> ちなみに、依存関係のバージョン全体もいずれ見直したほうがよいかもしれません。
> お役に立てば幸いです！さらに掘り下げたい点があればお知らせください。

</td>
<td width="50%">

### 変更後

> `npm install jsonwebtoken@latest` を実行し、`src/auth.ts:42` を編集します。
>
> 1. `src/auth.ts` を開く
> 2. `verifyToken`（42〜58 行目）を下のコードに置き換える
> 3. `npm test -- auth.spec.ts` を実行する
>
> 古いシグネチャが失敗の原因です。`jsonwebtoken` v9 は 47 行目が使うコールバック
> 形式を削除しました。
>
> 次: テストが失敗したら、最初のエラー行を貼ってください。

</td>
</tr>
</table>

## 2 つのレイヤー

**シェイプ**は、何をどの順で言うかを決めます。10 のルール。

1. 次のアクションから始める。
2. 複数ステップの作業に番号を振る。
3. 具体的な次の一手で終える。
4. 脱線を抑える。
5. 毎ターン状態を言い直す。
6. 所要時間は具体的な単位で示す。
7. 今、何が動くようになったかを示す。
8. エラーは淡々と述べる。
9. リストは 5 項目まで。
10. 前置きなし、要約なし、締めの挨拶なし。

**言語**は、各文の書き方を決めます。

- 1 語 1 義。1 つの動作に 1 つの動詞。類義語を使い回さない。
- 標準動詞: check、make sure、start、stop、use、show、find、change、remove、need。
- 能動態を使い、動作主を明示する。
- 単純時制のみ。完了時制も助動詞の積み重ねも使わない。
- 指示は 1 文 20 語まで、説明は 25 語まで。名詞の連結は 3 語まで。

全文は [`output-styles/attention-control.md`](../../output-styles/attention-control.md) にあります。

## 決して触れないもの

コード、コマンド、ファイルパス、識別子、エラーメッセージ、引用したテキストは
1 文字も変えずにそのまま再現します。このスタイルが管理するのは、エージェント自身が
書く文章だけです。

正確さは簡潔さに優先します。文を短くするために事実、数値、条件、適用範囲を削る
ことはありません。実際の不確実性を表す表現はそのまま残します。

## 評価

評価ハーネスは、スタイルを適用しないベースラインと回答の品質を比較します。長さは
測りません。

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3
```

20 ケース、6 つの採点軸、そして正確性や安全性の後退を止めるリリースゲート。
[evals/README.md](../../evals/README.md) を参照してください。

## クレジット

このスタイルは既存の 2 つの作品を組み合わせたものです。どちらの作者も本プロジェクトに
関与していません。

**シェイプ層:** Ayoub G. の [`i-have-adhd`](https://github.com/ayghri/i-have-adhd)（MIT）。
評価ハーネスも同じプロジェクトに由来します。

**言語層:** [L1nefeed](https://github.com/L1nefeed) の
[`asd-ste100` 出力スタイル](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2)。
これ自体が [ASD-STE100](https://www.asd-ste100.org/) Simplified Technical English 第 9 版を
凝縮したものです。

本プロジェクトは ASD 規格の文章を一切複製しておらず、認証、承認、提携のいずれも
受けていません。詳細は [NOTICE.md](../../NOTICE.md) にあります。

## ライセンス

MIT。[LICENSE](../../LICENSE) を参照してください。
