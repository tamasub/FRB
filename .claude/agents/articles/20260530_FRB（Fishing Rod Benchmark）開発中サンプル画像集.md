# FRB（Fishing Rod Benchmark）開発中サンプル画像集

- URL: https://qiita.com/tamasub/items/44aa1c32cc006fe093be
- 公開日: 2026-05-30T08:09:26+09:00
- タグ: モニター, FFT, FRB, サンプル画像

---


**※本規格は現在、実験・検証段階にある構想である。**

## FRBとは

:::note info
感度は分かち合って初めて本物になる
:::



感度とは、人間が認識可能な構造として現れる振動の和音構造である。
感度とは、単純な振動の強さではない。

FRBは、ロッドの「優劣」を決めるためではない。
「基準振動」を用いて、ロッドごとの振動構造差分を比較・可視化し、選択と体験共有のための共通言語を目指している。

FRBにおける知覚トレーニングとは、
室内で基準振動を体験し、海で感じる砂・岩・藻・糸擦れ・ぷるぷるなどの振動を、比較・言語化・共有するための練習である。

ロッドだけでなく、人間側の知覚も少しずつ海に合わせていく。
それがFRBの目指す「感じるための共通言語」である。



---

本記事は、以下ブログサイトで公開している 各種開発中サンプル画像を集めたページです。
[釣り竿の「感度」を数値化する話 - FRB（Fishing Rod Benchmark）宣言](https://qiita.com/tamasub/items/2b6649748e1772b7eec1)


---

## FRB物語：主人公紹介 

■ 『ルアーニスト改』(2026/3/11現在)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/6dde4bf0-973f-4508-a6d8-463f5a9e5fec.png)

## 開発中サンプル
■計測１号機くん(2026/3/11現在）
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/e7094599-297e-46f8-93f2-0e983b6d1497.png)

■計測２号機くん（2026/5/28現在）・・・ミニマム構成版（普及に向けて）
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/04e48cd1-3cef-453b-b6bc-f7bc62dfbe9e.png)


<details>
<summary>開発環境(2026/3/11現在）</summary>

■ 開発環境(2026/3/11現在）
  * 機器：ESP32-DevKitC-VE開発ボード、加速度センサー(MPU-6050)、マイク(INMP441)
  * 開発環境：Arduino IDE 2.3.7　及び 1.8.19

　本宣言に伴い、スマホのみで稼働できるスマホアプリ化(Flutter環境)に徐々に移行を検討する予定。
 
</details>

 
<details>
<summary>FFTモニターサンプル(2026/3/11現在）</summary>

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/3a7af3cd-e4b3-4e5c-8792-70fbc246c3eb.png)

  ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/57ba4ecf-feba-40bc-8e61-efc7bbc5d5f2.png)

  ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/272ea963-de06-48c6-a7f0-6627c4976ff8.png)

 ![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/5c814bde-c577-4033-ab24-3de8d99f05cb.png)

</details>


▶ FFTモニターサンプル(2026/5/30現在）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/b92f213c-5130-4da9-8f4c-957405c1f5f5.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/8cc53f8d-ba15-49dd-8857-b9f62c6961b1.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/f50d4a4b-e38e-4c4f-add1-9e6bfc8c8f6c.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/18deab3f-82b5-4522-8455-49b49dd4e19d.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/e077d14a-bb2c-446c-9422-face6a8fcac2.png)

▶ FRB Tools サンプル
□ FRB Compare
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/694a532c-cad7-4840-a136-7b7c674c6616.png)


□ [Artificial PuruPuru Designer](https://tamasub.github.io/FRB/tools/frb_purupuru_designer/)
（特上ぷるぷる振動発生装置・スピーカー再生→トップガイド接触→グリップ計測）
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/5bb6bbce-e28a-44ec-806f-87931f7f1469.png)

□ [FRB Sensor Check Mobile](https://tamasub.github.io/FRB/tools/frb_sensor_check_mobile/)　（スマホ計測体験 簡易Web版）

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/25f060c0-497f-4c39-9f87-6ef85b503fb4.png)


□ MetaDiff Hypothesis Viewer -AI差分物語・メタ認知外部化ツール-
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/22a39181-d8ea-4b1e-9dab-816c76ba1578.png)

□ DiffJson Viewer
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/383597a5-8bac-49b2-9159-19a55a64b82b.png)

□ [FRB Markdown Viewer](https://tamasub.github.io/FRB/tools/mdViewer.html?md=https%3A%2F%2Fraw.githubusercontent.com%2Ftamasub%2FFRB%2Fmain%2FFRB_Blog%2FFRB_Lab_Notes_Qiita.md) 

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/de4cc44b-1430-45da-8a03-9f170b4251fc.png)

□ 振動エフェクター
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/05dde216-19a7-4dbb-9f26-8833497f124a.png)

□ 木材骨伝導

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/3069714/76aa55ea-7d8e-4e24-a8d5-9ace387b5851.png)

---



[ロッド感度ベンチマーク（Fishing Rod Benchmark［FRB］） Home](https://qiita.com/tamasub/items/2b6649748e1772b7eec1)


---

