from __future__ import annotations

from sentence_transformers import SentenceTransformer


# 検索対象の簡易ナレッジ
DOCUMENTS = [
    "在宅勤務を行う場合は、事前に上司の承認を得てください。",
    "出張費は、出張終了後5営業日以内に精算してください。",
    "有給休暇は、原則として前日までに申請してください。",
    "社外から接続する場合は、会社指定のVPNを使用してください。",
    "機密情報を個人所有の端末へ保存してはいけません。",
    "勤務開始時と終了時には、勤怠システムへ時刻を入力してください。",
    "FRBは、釣り竿の硬さ・曲がり方・パワー・アクションを比較するための規格ではありません。",
    "FRBは、静荷重によるベンディングカーブや曲がり量を測定するものではありません。",
    "FRBは「基準振動」を用いて、ロッドごとの振動構造差分を比較・可視化することを目指している。",
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
    "釣り竿は使用後に水洗いし、十分に乾燥させて保管する。",
]

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5


def main() -> None:
    print("モデルを読み込んでいます。初回だけ少し待ってください……")
    model = SentenceTransformer(MODEL_NAME)

    print("文書をベクトル化しています……")
    # 文書側は起動時に一度だけ計算し、その後の質問では使い回す。
    document_vectors = model.encode(
        DOCUMENTS,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    print("\n準備完了！")
    print("質問を何度でも入力できます。終了するときは「終了」「exit」「quit」のどれかを入力してください。")

    while True:
        try:
            query = input("\n質問> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n終了します。")
            break

        if query.lower() in {"終了", "exit", "quit"}:
            print("終了します。")
            break

        if not query:
            continue

        # 質問だけをベクトル化する。重たいモデルと文書ベクトルは再利用する。
        query_vector = model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        scores = model.similarity(query_vector, document_vectors)[0].tolist()

        results = sorted(
            zip(scores, DOCUMENTS),
            key=lambda item: item[0],
            reverse=True,
        )

        print(f"\n質問: {query}")
        print(f"上位{min(TOP_K, len(results))}件:")

        for rank, (score, document) in enumerate(results[:TOP_K], start=1):
            print(f"{rank}. {score:.3f}  {document}")


if __name__ == "__main__":
    main()
