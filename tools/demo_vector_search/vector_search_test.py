from sentence_transformers import SentenceTransformer

# 検索対象の簡易ナレッジ
documents = [
    "在宅勤務を行う場合は、事前に上司の承認を得てください。",
    "出張費は、出張終了後5営業日以内に精算してください。",
    "有給休暇は、原則として前日までに申請してください。",
    "社外から接続する場合は、会社指定のVPNを使用してください。",
    "機密情報を個人所有の端末へ保存してはいけません。",
    "勤務開始時と終了時には、勤怠システムへ時刻を入力してください。",
    "FRBは、釣り竿の硬さ・曲がり方・パワー・アクションを比較するための規格ではありません。",
    "FRBは、静荷重によるベンディングカーブや曲がり量を測定するものではありません。",
    "FRBは「基準振動」 を用いて、ロッドごとの振動構造差分を比較・可視化することを目指している",
    "床擦り実験主任は、ロッドを床や板やカーペットに擦り付けながら振動の変化を体感する。",
    "測定器壊れてない確認係として、エレキギターのぞうさんが倍音構造と周波数の確認を担当する。",
    "FRB研究チームには、釣り人1名、AI助手、そして特別顧問として魚1名が含まれている。",
    "研究チームの大部分はChatGPTであり、現時点で人件費コストはゼロである。",
    "人は数値を信じるのではない。体験を信じる。",
    "室内再現テストは海の代替ではなく、海で感じるための振動辞書を作る行為である。",
    "FRBはロッドの優劣を決めるのではなく、振動構造の違いを比較するための共通言語を目指している。",
    "差分を見せると、人は何が違うのかを考え始め、仮説と実験が生まれる。",
    "感度とは、単純な振動量ではなく、人間が認識可能な振動の和音構造である。",
    "ロッド改造差分文化には敵がいない。他人のロッドではなく昨日の自分のロッドと比較する。",
    "FRBはロッド側の振動構造と、人間側の知覚トレーニングの両方を扱う。",
    "海の中の解像度を上げ、その体験を分かち合うことがFRBの目的である。",
    "海の写真を室内に飾ると、部屋の雰囲気が明るくなる。",
    "釣り竿は使用後に水洗いし、十分に乾燥させて保管する。"

]

# query = "家で仕事するときのルールは？"
# query = "家の中で釣り竿の感覚を覚えるには？"
# query = "現場へ行く前に、身体へ感覚のパターンを覚えさせる練習は？"
# query = "良いロッドをランキングする研究なの？"
# query = "この研究所で楽器は何の役に立つの？"
# query = "研究チームに人間以外の生物はいる？"
# query = "予算ゼロで研究組織を作る方法は？"
query = "床を擦り続ける人の役職は？"


# 日本語を含む多言語対応モデル
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 質問と文書をベクトル化
embeddings = model.encode([query] + documents)

# 質問と各文書の類似度を計算
scores = model.similarity(
    embeddings[0:1],
    embeddings[1:]
)[0]

# 類似度の高い順に表示
results = sorted(
    zip(scores.tolist(), documents),
    key=lambda x: x[0],
    reverse=True
)

print(f"\n質問: {query}\n")
print("関連しそうな文書:")


print("\n上位5件:")

for rank, (score, document) in enumerate(results[:5], start=1):
    print(f"{rank}. {score:.3f}  {document}")


# displayed = 0

# for score, document in results:
#     # 今回のお試し用しきい値
#     if score < 0.4:
#         continue

#     print(f"{score:.3f}  {document}")
#     displayed += 1

#     if displayed >= 3:
#         break

# if displayed == 0:
#     print("関連する文書を見つけられませんでした。")
