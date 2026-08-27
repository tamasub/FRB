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

string ReadControlValue(IWebElement control)
{
    return
        control.GetDomProperty("value") ??
        control.GetAttribute("value") ??
        control.Text;
}

bool WaitUntil(Func<bool> condition, int timeoutMs = 5000, int intervalMs = 100)
{
    var started = Environment.TickCount64;
    while (Environment.TickCount64 - started < timeoutMs)
    {
        try
        {
            if (condition()) return true;
        }
        catch (StaleElementReferenceException)
        {
            // 再描画中は次のpollでDOMを取り直す。
        }
        catch (NoSuchElementException)
        {
            // 再描画中は次のpollでDOMを取り直す。
        }

        Thread.Sleep(intervalMs);
    }

    return false;
}

void AssertPass(bool passed, string label, string? detail = null)
{
    Console.WriteLine($"{label}: {(passed ? "PASS" : "FAIL")}");
    if (!passed)
    {
        throw new InvalidOperationException(
            string.IsNullOrWhiteSpace(detail)
                ? $"{label} failed"
                : $"{label} failed: {detail}"
        );
    }
}

bool IsDetailDialogOpen()
{
    var raw = driver.FindElement(By.Id("detailDialog")).GetDomProperty("open");
    return bool.TryParse(raw, out var opened) && opened;
}

void CloseDetailDialog()
{
    var detailDialog = driver.FindElement(By.Id("detailDialog"));
    if (IsDetailDialogOpen())
    {
        var closeButton = detailDialog.FindElement(
            By.CssSelector("button[value='cancel']")
        );
        closeButton.Click();
        WaitUntil(() => !IsDetailDialogOpen());
    }
}

IWebElement OpenSecondRowAndVerifyWorkItem()
{
    var rows = driver.FindElements(By.CssSelector("#dataGrid tbody tr"));
    Console.WriteLine("Grid行数: " + rows.Count);

    if (rows.Count < 2)
    {
        throw new InvalidOperationException("Gridが2行以上ありません");
    }

    new Actions(driver)
        .DoubleClick(rows[1])
        .Perform();

    Console.WriteLine("2行目をダブルクリックしました");

    var opened = WaitUntil(IsDetailDialogOpen);
    AssertPass(opened, "エディター表示");

    var detailDialog = driver.FindElement(By.Id("detailDialog"));
    var workItemIdControl = detailDialog.FindElement(
        By.CssSelector("#detailForm [data-field='work_item_id']")
    );

    var workItemId = ReadControlValue(workItemIdControl);
    Console.WriteLine("work_item_id: " + workItemId);

    AssertPass(
        workItemId == "studio_work_0002",
        "work_item_id 読取",
        $"Expected=studio_work_0002, Actual={workItemId}"
    );

    return detailDialog;
}

string ReadTitleFromOpenDetail()
{
    var detailDialog = driver.FindElement(By.Id("detailDialog"));
    var titleControl = detailDialog.FindElement(
        By.CssSelector("#detailForm [data-field='title']")
    );
    return ReadControlValue(titleControl);
}

void SetTitleAndApply(string value)
{
    var detailDialog = driver.FindElement(By.Id("detailDialog"));
    var titleControl = detailDialog.FindElement(
        By.CssSelector("#detailForm [data-field='title']")
    );

    titleControl.Clear();
    titleControl.SendKeys(value);

    var draft = ReadControlValue(titleControl);
    Console.WriteLine("title UI入力後: " + draft);
    AssertPass(draft == value, "title UI入力");

    titleControl.SendKeys(Keys.F12);
    Console.WriteLine("F12を送信しました");

    var reflected = WaitUntil(() =>
    {
        var refreshedDialog = driver.FindElement(By.Id("detailDialog"));
        var refreshedTitle = refreshedDialog.FindElement(
            By.CssSelector("#detailForm [data-field='title']")
        );
        return ReadControlValue(refreshedTitle) == value;
    });

    var titleAfter = ReadTitleFromOpenDetail();
    Console.WriteLine("title F12反映後: " + titleAfter);
    AssertPass(reflected && titleAfter == value, "title F12反映");
}

void SaveAndVerifyStatus(string label)
{
    CloseDetailDialog();

    var saveBtn = driver.FindElement(By.Id("saveBtn"));
    Console.WriteLine("保存ボタン Enabled: " + saveBtn.Enabled);
    AssertPass(saveBtn.Enabled, label + " 保存ボタン");

    saveBtn.Click();
    Console.WriteLine("保存ボタンをクリックしました");

    var saved = WaitUntil(() =>
    {
        var status = driver.FindElement(By.Id("status")).Text;
        return status.Contains("上書き保存しました", StringComparison.Ordinal);
    }, timeoutMs: 8000);

    var statusText = driver.FindElement(By.Id("status")).Text;
    Console.WriteLine("保存Status: " + statusText);
    AssertPass(saved, label + " 上書き保存", statusText);
}

void ReloadCurrentData()
{
    var loadBtn = driver.FindElement(By.Id("loadBtn"));
    loadBtn.Click();
    Console.WriteLine("再読込ボタンをクリックしました");

    var reloaded = WaitUntil(() =>
    {
        var status = driver.FindElement(By.Id("status")).Text;
        return !status.Contains("上書き保存しました", StringComparison.Ordinal)
            && driver.FindElements(By.CssSelector("#dataGrid tbody tr")).Count >= 2;
    }, timeoutMs: 8000);

    AssertPass(reloaded, "再読込");
}

// STEP 0: 対象JSONを選択してロード。
var dataCombo = driver.FindElement(By.Id("dataNameInput"));
dataCombo.Click();
dataCombo.Clear();
dataCombo.SendKeys("_studio_work_incident_data_v2.json");
Thread.Sleep(500);
dataCombo.SendKeys(Keys.Enter);
Thread.Sleep(300);

Console.WriteLine("選択値: " + dataCombo.GetAttribute("value"));

var loadBtn = driver.FindElement(By.Id("loadBtn"));
Console.WriteLine("読込ボタン Enabled: " + loadBtn.Enabled);
loadBtn.Click();
Console.WriteLine("読込ボタンをクリックしました");

Thread.Sleep(2000);

// STEP 1: Row Detail Editor の状態を読む。
OpenSecondRowAndVerifyWorkItem();
var titleBefore = ReadTitleFromOpenDetail();
var marker = " [SeleniumTaste]";
var titleExpected = titleBefore + marker;
Console.WriteLine("title 変更前: " + titleBefore);

// STEP 2: UI入力 -> F12でcanonical Dataへ反映。
SetTitleAndApply(titleExpected);

// STEP 3: 実際の「保存」ボタンでファイルへ上書き保存。
SaveAndVerifyStatus("変更値");

// STEP 4: 同じJSONを再読込し、保存値が残っていることを確認。
ReloadCurrentData();
OpenSecondRowAndVerifyWorkItem();
var titleReloaded = ReadTitleFromOpenDetail();
Console.WriteLine("title 再読込後: " + titleReloaded);
AssertPass(
    titleReloaded == titleExpected,
    "title 保存・再読込",
    $"Expected={titleExpected}, Actual={titleReloaded}"
);

// STEP 5: テスト痕跡を残さないよう元タイトルへ戻して再保存。
Console.WriteLine("後始末: 元タイトルへ戻します");
SetTitleAndApply(titleBefore);
SaveAndVerifyStatus("後始末");

// STEP 6: 最後に再読込し、元の状態へ戻ったことまで確認。
ReloadCurrentData();
OpenSecondRowAndVerifyWorkItem();
var titleRestored = ReadTitleFromOpenDetail();
Console.WriteLine("title 後始末再読込後: " + titleRestored);
AssertPass(
    titleRestored == titleBefore,
    "後始末",
    $"Expected={titleBefore}, Actual={titleRestored}"
);

Console.WriteLine("保存E2E: ALL PASS");
Console.WriteLine("画面確認中。Enterで終了します");
Console.ReadLine();
