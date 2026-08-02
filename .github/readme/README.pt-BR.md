<p align="center">
  <strong>Attention Control</strong><br>
  <em>A disciplina do controle de tráfego aéreo aplicada à saída da IA.</em>
</p>

<p align="center">
  <a href="../../README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <a href="README.vi.md">Tiếng Việt</a> ·
  <strong>Português (BR)</strong>
</p>

## Instalação

<details open>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add aaddrick/attention-control
claude plugin install attention-control@attention-control
```

Depois rode `/config`, selecione **Output style** e escolha **Attention Control**.
Ele passa a valer depois de `/clear` ou na próxima sessão.

Para pular o menu, adicione isto ao `~/.claude/settings.json`:

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

Depois digite `$attention-control` para aplicar o estilo.

</details>

<details>
<summary><strong>Cursor, Gemini CLI e instalação manual</strong></summary>

Veja [INSTALL.md](../../INSTALL.md).

</details>

## O que ele faz

A fraseologia do controle de tráfego aéreo existe por um motivo: uma pessoa sob
carga ouve a instrução errada. A aviação resolveu isso com duas disciplinas. O
vocabulário controlado faz cada palavra ter um único sentido. A estrutura fixa da
mensagem põe a instrução na frente e o contexto no fim.

Este estilo aplica as duas disciplinas ao seu agente de código. O agente começa
pela ação que você pode executar e escreve cada frase com uma palavra, um sentido.

## O que muda

<table>
<tr>
<td width="50%">

### Antes

> Ótima pergunta! Deixe-me dar uma olhada. Parece que seu fluxo de autenticação
> tem algumas partes envolvidas. Olhando `src/auth.ts`, a lógica de verificação do
> token possivelmente esteja utilizando uma API descontinuada — a função
> `verifyToken`, por volta das linhas 42-58, parece ter sido implementada contra
> uma assinatura antiga do `jsonwebtoken`. Uma abordagem que poderia ser
> considerada seria atualizar o pacote e refatorar essa função. A propósito, as
> versões das suas dependências em geral talvez também mereçam uma revisão em
> algum momento. Espero que ajude! Me avise se quiser aprofundar qualquer ponto.

</td>
<td width="50%">

### Depois

> Rode `npm install jsonwebtoken@latest` e depois edite `src/auth.ts:42`.
>
> 1. Abra `src/auth.ts`
> 2. Substitua `verifyToken` (linhas 42–58) pelo trecho abaixo
> 3. Rode `npm test -- auth.spec.ts`
>
> A assinatura antiga causa a falha. O `jsonwebtoken` v9 removeu a forma de
> callback que a linha 47 usa.
>
> Próximo passo: cole a primeira linha de erro se algum teste falhar.

</td>
</tr>
</table>

## As duas camadas

**Forma** decide o que você diz e em que ordem. 10 regras:

1. Comece pela próxima ação.
2. Numere o trabalho de várias etapas.
3. Termine com uma próxima ação concreta.
4. Suprima tangentes.
5. Repita o estado a cada turno.
6. Dê estimativas de tempo em unidades concretas.
7. Mostre o que agora funciona.
8. Relate erros de forma seca.
9. Limite listas a 5 itens.
10. Sem preâmbulo, sem recapitulação, sem fecho.

**Linguagem** decide como cada frase é escrita:

- Uma palavra, um sentido. Uma ação, um verbo. Não alterne sinônimos.
- Verbos padrão: check, make sure, start, stop, use, show, find, change, remove, need.
- Use a voz ativa e nomeie quem age.
- Use apenas tempos simples. Sem tempos compostos e sem pilhas de auxiliares.
- No máximo 20 palavras por frase em instruções e 25 em explicações. Cadeias de
  substantivos até 3 palavras.

Texto completo: [`output-styles/attention-control.md`](../../output-styles/attention-control.md).

## O que ele nunca toca

Código, comandos, caminhos de arquivo, identificadores, mensagens de erro e texto
citado permanecem literais, caractere por caractere. O estilo governa apenas a
prosa que o próprio agente escreve.

Precisão vence brevidade. Nenhuma regra remove um fato, um número, uma condição ou
um qualificador de escopo para encurtar uma frase. Uma ressalva que carrega
incerteza real permanece.

## Avaliações

O harness compara a qualidade da resposta com uma linha de base sem estilo. Ele não
mede tamanho.

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3
```

20 casos, 6 dimensões de pontuação e um portão de release que barra um candidato
que regride em correção ou segurança. Veja [evals/README.md](../../evals/README.md).

## Créditos

Este estilo combina dois trabalhos já existentes. Nenhum dos dois autores participa
deste projeto.

**Camada de forma:** [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) de
Ayoub G. (MIT). O harness de avaliação deriva do mesmo projeto.

**Camada de linguagem:** o
[estilo de saída `asd-ste100`](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2)
de [L1nefeed](https://github.com/L1nefeed), que por sua vez condensa o
[ASD-STE100](https://www.asd-ste100.org/) Simplified Technical English, edição 9.

Este projeto não reproduz nenhum texto da especificação da ASD e não é certificado,
endossado nem afiliado. Detalhes em [NOTICE.md](../../NOTICE.md).

## Licença

MIT. Veja [LICENSE](../../LICENSE).
