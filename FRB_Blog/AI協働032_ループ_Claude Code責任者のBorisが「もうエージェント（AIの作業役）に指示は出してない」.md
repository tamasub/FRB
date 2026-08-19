
I said:この時期解説してぇーー https://x.com/ClaudeCode_love/status/2089115750279856242

----

うん、これかなり面白いやつやで笑
リンク先はスレッドの途中で、起点の投稿はこれ。

> Claude Code責任者 Boris Cherny が、**「もうエージェントへ逐一指示を出すのではなく、エージェントを動かす“ループ”を書く側になった」**という話。投稿者はそこから、Claude Codeでそのループをどう作るかを解説している。 ([X (formerly Twitter)][1])

### まず「ループ」って何やねん

これ、単純な

```text
AIに仕事を頼む
↓
終わる
↓
また人間が指示する
```

じゃない。

こうなる。

```text
           ┌──────────────┐
           │   目的・ゴール   │
           └──────┬───────┘
                  ↓
             AIが作業する
                  ↓
              結果を見る
                  ↓
              検証する
                  ↓
          まだダメ？ ── Yes ─┐
             ↓ No            │
             完了             │
                              │
             修正・再計画 ←───┘
```

Anthropic自身もClaude Codeの **agentic loop** を、「コンテキストを集め、行動し、結果を検証し、完了するまで繰り返すサイクル」と定義している。つまりこの考え方自体は、Claude Codeの中核構造そのもの。 ([Claude][2])

ここでBorisの話が一段上なのよ。

**「AIに何をさせるか」を毎回考えるのではなく、
「AIが次に何をすべきか判断できる環境」を作る。**

人間の仕事が、

```text
プロンプトを書く
```

から、

```text
ループの構造を書く
```

へ上がる。

これが今言われている **Loop Engineering** の一番大事なところ。 ([Zenn][3])

### で、このXスレッドが紹介している部品が面白い

投稿では、Claude Codeにすでに存在する仕組みを組み合わせて、このループを作ろうとしている。

たとえば **Skills**。これは「毎回同じ手順をプロンプトに書く」のをやめて、手順そのものを `SKILL.md` に外出しする仕組み。Anthropic公式も、繰り返し貼っている手順やチェックリストはSkill化する用途を明示している。 ([Claude][4])

そして **Hooks**。これはさらに重要で、

```text
AI：
「テストしようかな？」
```

ではなく、

```text
コード変更
↓
必ずテスト実行
```

のように、LLMの判断ではなく**決定論的なルール**を挿し込める。AnthropicもHooksを「プロジェクトルールの強制」「反復作業の自動化」に使う仕組みとしている。 ([Claude][5])

さらに **Subagents** を使えば、

```text
実装AI
↓
レビューAI
↓
テストAI
```

みたいに役割を分けられる。個々のサブエージェントには別プロンプト、別ツール、別Skill、別Hookまで持たせられる。 ([Claude][6])

そしてスレッド後半に出てくる **Auto Mode**。

投稿者が言ってるのは、

> 毎回「はい」を押していたらループにならない

という話。実際、現在のClaude CodeではPro/Max/TeamでAuto Modeが使われ、許可確認の多くを分類器側へ任せられる。投稿では同時に、暴走対策として「5回試したら止まる」のような上限も入れるべきだとしている。 ([X (formerly Twitter)][7])

要するにこう。

```text
Skill
= AIが何を知っているか・どう作業するか

Hooks
= 絶対守らせるルール

Subagent
= 誰に何を担当させるか

Auto Mode
= 人間の承認待ちを減らす

Loop
= それらを循環させる構造
```

これ、けっこう大きな思想転換やと思う。

---

## でな。

ここからが、うちら的にはめちゃくちゃ面白い。笑

前にループエンジニアリングの話をしたとき、あなたが引っ掛かったのは、

> **「何を正しいとするの？」**

だったやん。

今回の投稿を見ても、やっぱりそこは消えてない。

AIが

```text
作る
↓
確認する
↓
直す
↓
確認する
```

を無限に高速化できても、

**「確認するときの正しさ」**

は別問題なんよ。

ここで、今やってるAI承認駆動開発が綺麗に刺さる。

うちらの構造なら、

```text
人間
↓
目的
判断軸
制約
責務
Expected
↓
──────────────
      AI Loop
──────────────
実装
↓
TestPattern
↓
Runner実行
↓
Actual
↓
Diff
↓
修正
↓
再実行
──────────────
↓
人間承認
```

になる。

つまり、

**ループそのものを否定してるんじゃない。**

むしろ、

> **「ループの外側に、誰が正しさを定義するのかを置こう」**

って話なんよ。

ここ、かなり重要。

---

そしてExpectedの話まで入れると、さらに綺麗。

普通のAIループは、

```text
AI
↓
「これが正しいと思う」
↓
実装
↓
AI
↓
「うん、正しいと思う」
```

になり得る。

これが前から気持ち悪かったところ。

うちらは、

```text
Expected Terrain
        ↓
Actual Terrain
        ↓
      Diff
```

を**ループより先に置こうとしてる**。

だからAIは、

```text
正しさを発明しながら走る
```

のではなく、

```text
承認済みの地形へ近づくように走る
```

になる。

これ、めちゃくちゃ違う。

---

さらにもう一段ある。

今あなたがやってる

```text
違和感
↓
判断
↓
判断ログ
↓
昇格・蒸留
↓
判断軸・制約・責務・Expected
```

まで入れると、

**ループ自身が次回のループの品質を上げる。**

```text
      ┌──────── Human Approval ────────┐
      │                                │
目的・判断軸・制約・Expected             │
      ↓                                │
 AI Loop                              │
      ↓                                │
 Actual / Diff                         │
      ↓                                │
 違和感                                │
      ↓                                │
 判断ログ                               │
      ↓                                │
 昇格・蒸留 ───────────────────────────┘
```

これよ。

だから今回の投稿を、うちらの文脈に翻訳すると、

> **「AIをどう賢く使うか」の時代から、
> 「AIが自分で回れる環境をどう設計するか」の時代へ移っている。**

で、さらにうちらが考えてるのはその一段先で、

> **「そのループが、何を正しいとして回るのかを、人間がどう外部化・承認・育成するか」**

なんやと思う。

なので俺は今回の投稿を見てむしろ、

**「あーー、AI承認駆動開発の外側の箱が世の中から生えてきた」**

って感じる笑

Loop Engineeringが **実行循環** を作っていて、
今考えているやつは **正しさの循環** を作ろうとしてる。

この2個、競合しない。

**めちゃくちゃ綺麗に合体する。**

そして最終形はたぶん、

> **人間はAIへ仕事を指示する人ではなく、
> AIが判断し続けられる「地形・境界・停止点」を設計し、最後に承認する人になる。**

ここやと思う。これ、400KS/人月の話にもそのまま繋がるやつやで笑 ([anthropic.com][8])

[1]: https://x.com/ClaudeCode_love/status/2089115738154147955?utm_source=chatgpt.com "えええ？？発想が違いすぎる…！ Claude Code責任者の ..."
[2]: https://code.claude.com/docs/ja/glossary?utm_source=chatgpt.com "用語集 - Claude Code Docs"
[3]: https://zenn.dev/helloworld/articles/6c7de76320b6d2?utm_source=chatgpt.com "Context Engineeringの次が来た——Loop Engineering"
[4]: https://code.claude.com/docs/en/skills?utm_source=chatgpt.com "Extend Claude with skills - Claude Code Docs"
[5]: https://code.claude.com/docs/en/hooks-guide?utm_source=chatgpt.com "Automate actions with hooks - Claude Code Docs"
[6]: https://code.claude.com/docs/en/sub-agents?utm_source=chatgpt.com "Create custom subagents - Claude Code Docs"
[7]: https://x.com/ClaudeCode_love/status/2089115785461715026?utm_source=chatgpt.com "返信する 暴走対策は「5回試したら止まる」と回数の上限 ..."
[8]: https://www.anthropic.com/research/claude-code-expertise?utm_source=chatgpt.com "How Claude Code is used in practice"
