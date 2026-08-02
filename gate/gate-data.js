// ============================================
// gate-data.js
// 忍者ブログ(または他の静的ホスティング)に、そのまま置くファイル。
// <script src="https://あなたの忍者URL/gate-data.js"></script>
// の形で、各作品のアーティファクト側から読み込んで使う。
//
// 生パスワードではなく「SHA-256ハッシュ」を保存する。
// ハッシュの作り方は、このファイルの末尾のコメントを参照。
// ============================================

window.GATE_DATA = {
  "work-a": {
    title: "限定公開: context diff #1",
    hash: "c49a71ac58c7d7b0d77b3f6336abd706368926a849f0fd4426a7e68783ef29ca",
    url: "https://claude.ai/public/artifacts/76fd7a2b-1d5d-4ce8-ba26-1c87e4e61b09"
    
        
  },
  "work-b": {
    title: "作品B 限定公開",
    hash: "9038bc7953396be1f57d15fb22a350a2eddc0c90abe0eda1362bd9367182daa2",
    url: "https://claude.ai/public/artifacts/ac90227b-aaec-43d0-90ef-0635d0ebea96"
  },
  // 新しい作品はここに追加していくだけ
  // "work-c": { title: "作品C 限定公開", hash: "...", url: "https://..." },
};
