using OpenQA.Selenium;
using OpenQA.Selenium.Interactions;


using OpenQA.Selenium.Edge;

var options = new EdgeOptions();
options.UseWebView = true;
options.BinaryLocation =
    @"F:\FRB\tools\FRBStudio_App\NativeShell\_publish\FRBStudio.NativeShell.exe";

var service = EdgeDriverService.CreateDefaultService(
    @"F:\FRB\tools\FRBStudio_App\SeleniumTaste\driver\edgedriver_win64"
);

using var driver = new EdgeDriver(service, options);
Thread.Sleep(3000);

// DATA JSON コンボをクリック
var dataCombo = driver.FindElement(By.Id("dataNameInput"));
dataCombo.Click();


// インシデントファイル名で検索
dataCombo.Clear();



dataCombo.SendKeys("_studio_work_incident_data_v2.json");

Thread.Sleep(500);

dataCombo.SendKeys(Keys.Enter);

Thread.Sleep(300);

Console.WriteLine(
    "選択値: " + dataCombo.GetAttribute("value")
);

// 読み込みボタンを明示的にクリック
var loadBtn = driver.FindElement(By.Id("loadBtn"));

Console.WriteLine("読込ボタン Enabled: " + loadBtn.Enabled);

loadBtn.Click();

Console.WriteLine("読込ボタンをクリックしました");

// グリッド描画待ち
Thread.Sleep(3000);

// グリッド行を取得
var rows = driver.FindElements(
    By.CssSelector("#dataGrid tbody tr")
);

Console.WriteLine("Grid行数: " + rows.Count);

if (rows.Count >= 2)
{
    // 上から2行目をダブルクリック
    new Actions(driver)
        .DoubleClick(rows[1])
        .Perform();

    Console.WriteLine("2行目をダブルクリックしました");

    Thread.Sleep(1000);

    var detailDialog = driver.FindElement(By.Id("detailDialog"));

    Console.WriteLine(
        "エディター表示: " +
        detailDialog.GetDomProperty("open")
    );
}
else
{
    Console.WriteLine("Gridが2行以上ありません");
}

Console.WriteLine("画面確認中。Enterで終了します");
Console.ReadLine();




Console.WriteLine("画面確認中。Enterで終了します");
Console.ReadLine();

