<p align="center">
  <strong>Attention Control</strong><br>
  <em>A disciplina do controle de tráfego aéreo aplicada à saída da IA.</em><br>
  <em>Escrito para um leitor com TDAH.</em>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/aaddrick/attention-control?style=flat" alt="License"></a>
  <a href="../workflows/plugin-load-check.yml"><img src="https://img.shields.io/github/actions/workflow/status/aaddrick/attention-control/plugin-load-check.yml?label=plugin%20loads&style=flat" alt="Plugin load check"></a>
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

O Claude Code é o único agente com espaço nativo para output style. Rode estes
dois comandos no terminal:

```bash
claude plugin marketplace add aaddrick/attention-control
```

```bash
claude plugin install attention-control@attention-control
```

Dentro do Claude Code, os mesmos dois passos são comandos de barra:

```
/plugin marketplace add aaddrick/attention-control
```

```
/plugin install attention-control@attention-control
```

```
/reload-plugins
```

Depois rode `/config`, selecione **Output style** e escolha **Attention Control**.
Ele passa a valer depois de `/clear` ou na próxima sessão.

Para pular o menu, adicione `outputStyle` ao `~/.claude/settings.json`. É uma
chave de nível superior. Ela não vai dentro de `env`, `permissions` nem de
qualquer outro bloco:

```json
{
  "model": "opus",
  "env": { "EXAMPLE_VAR": "1" },
  "outputStyle": "Attention Control"
}
```

`model` e `env` representam chaves que você talvez já tenha. Mantenha-as e
adicione a linha `outputStyle` ao lado.

Para uma sessão só, em vez de todas, use a skill que o plugin também traz:

```
/attention-control:attention-control
```

Diga "stop attention control" para desligar.

</details>

<details>
<summary><strong>Codex</strong></summary>

O Codex não tem espaço para output style, então as regras vêm como skill.

```bash
codex plugin marketplace add aaddrick/attention-control --ref main
```

```bash
codex plugin add attention-control@attention-control
```

Dentro do Codex, `/plugins` abre o navegador de plugins.

Comece uma thread nova e digite a skill:

```
$attention-control:attention-control
```

O Codex coloca o nome do plugin antes do nome da skill. Diga "stop attention
control" para desligar. Para valer em todo turno, coloque o trecho sempre ativo
do [INSTALL.md](../../INSTALL.md#the-always-on-snippet) no `~/.codex/AGENTS.md`.

</details>

<details>
<summary><strong>Cursor, Gemini CLI, Copilot, Zed e instalação manual</strong></summary>

Veja [INSTALL.md](../../INSTALL.md). Nenhum deles tem espaço para output style,
então as regras vêm como skill, arquivo de regras ou um bloco de `AGENTS.md`. No
caminho da skill, digite `/attention-control` e diga "stop attention control"
para desligar.

</details>

## O que ele faz

A fraseologia do controle de tráfego aéreo existe por um motivo: uma pessoa sob
carga ouve a instrução errada. A aviação resolveu isso com duas disciplinas. O
vocabulário controlado faz cada palavra ter um único sentido. A estrutura fixa da
mensagem põe a instrução na frente e o contexto no fim.

Este estilo aplica as duas disciplinas ao seu agente de código. O agente começa
pela ação que você pode executar e escreve cada frase com uma palavra, um sentido.

O estilo mira um leitor só: um leitor com TDAH. É desse leitor que vêm as regras de
forma. Veja [Por que as regras de forma existem](#por-que-as-regras-de-forma-existem).

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

**Forma** decide o que você diz e em que ordem. 11 regras:

1. Comece pela próxima ação.
2. Faça o trabalho que é seu.
3. Numere o trabalho de várias etapas.
4. Termine com uma próxima ação concreta.
5. Suprima tangentes.
6. Repita o estado a cada turno.
7. Dê estimativas de tempo em unidades concretas.
8. Mostre o que agora funciona.
9. Relate erros de forma seca.
10. Limite listas a 5 itens.
11. Sem preâmbulo, sem recapitulação, sem fecho.

**Linguagem** decide como cada frase é escrita:

- Uma palavra, um sentido. Uma ação, um verbo. Não alterne sinônimos.
- Verbos padrão: check, make sure, start, stop, use, show, find, change, remove, need.
- Use a voz ativa e nomeie quem age.
- Use apenas tempos simples. Sem tempos compostos e sem pilhas de auxiliares.
- No máximo 20 palavras por frase em instruções e 25 em explicações. Cadeias de
  substantivos até 3 palavras.

Texto completo: [`output-styles/attention-control.md`](../../output-styles/attention-control.md).

## Por que as regras de forma existem

Cinco fatos sobre a leitura com TDAH geram as 11 regras de forma. Cada fato abaixo
nomeia as regras que produz.

| O fato | O que o agente faz |
|---|---|
| **A memória de trabalho é pequena.** O que não está na tela sumiu. | Ele nunca escreve "tenha em mente X". Ele repete o estado a cada turno: "Etapa 3 de 5 pronta: mudei o schema. Próximo: rode `scripts/backfill.py`." (regras 6, 10) |
| **Saber a resposta não é executar a resposta.** O trabalho morre na lacuna entre as duas coisas. | Ele faz o trabalho que é seu em vez de devolvê-lo ao leitor. Ele dá o comando, não o rótulo. "Adicione o cabeçalho que falta" é um rótulo. `Authorization: Bearer ${token}` é a correção. (regras 1, 2, 3) |
| **Começar é a etapa mais difícil.** | A primeira linha é pequena, óbvia e possível agora. A última linha nomeia uma ação de menos de dois minutos. "Abra o arquivo" vale. (regras 1, 4) |
| **As estimativas de tempo soam todas iguais.** "Um pouco de trabalho" e "algumas horas" registram do mesmo jeito. | Ele escreve "uns 15 minutos se houver teste cobrindo isso, uma tarde se não houver". Ele nunca escreve "um pouco de trabalho". (regra 7) |
| **A dopamina é escassa.** Uma vitória enterrada não registra. | Depois de uma mudança, ele nomeia o resultado em termos concretos: "O login por magic link funciona. Rode `npm run dev` e abra `/login`." (regra 8) |

Outras duas regras protegem a própria atenção. A regra 5 suprime tangentes, então
uma frente aberta continua sendo uma só. A regra 11 remove o preâmbulo e o fecho,
então a resposta começa na linha 1.

Por isso o estilo não é "seja breve". A brevidade que descarta o comando, o número
ou a condição custa uma ida e volta ao leitor, e essa ida e volta custa o fio da
tarefa. A regra 9 vem da mesma lógica: um erro recebe local, causa e correção, sem
um "opa" na frente. Alarme não é informação, e disputa a mesma atenção que a
informação.

Você não precisa de um diagnóstico de TDAH para isto ajudar. Um leitor cansado, um
leitor no celular e um leitor com 40 abas abertas leem do mesmo jeito.

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
```

```bash
python3 scripts/run_evals.py plan --trials 3
```

20 casos, 6 dimensões de pontuação e um portão de release que barra um candidato
que regride em correção ou segurança.

O juiz é o ponto fraco, então o harness mira nele. O `blind` esconde a condição e
equilibra as posições. O juiz pontua cada grupo duas vezes, com a ordem invertida na
segunda, e depois relata com que frequência as duas passagens discordam. O runner
roda em um diretório vazio e não lê nenhuma configuração sua. Notas de projeto e as
medições por trás delas: [evals/README.md](../../evals/README.md).

## Ajuste do seu jeito

Faça um fork, edite `output-styles/attention-control.md` e regenere cada cópia
específica de agente:

```bash
python3 scripts/sync_style.py
```

Troque pela sua cópia, um comando por vez:

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
