using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace FRBStudio.NativeShell
{
    internal sealed class NativeShellForm : Form
    {
        private readonly WebView2 _webView = new WebView2();
        private readonly Label _status = new Label();
        private NativeShellConfig _config;
        private WorkspacePolicy _workspace;
        private NativeCommandDispatcher _dispatcher;
        private string _appRoot;
        private string _allowedOrigin;
        private readonly string _initialUri;
        private readonly string _initialPage;
        private readonly string _initialJsonPath;
        private readonly string _initialWorkspaceRoot;
        private readonly CoreWebView2Environment _sharedEnvironment;
        private readonly bool _deferInitialNavigation;
        private CoreWebView2Environment _environment;
        private Task _initializationTask;
        private bool _presentationReceived;
        private bool _launcherPresentation;
        private bool _nativeTitleBarDark;
        private bool _nativeTitleBarLaunchPalette;
        // The main WinForms host must never flash its default (1500x950) bounds.
        // Keep it transparent until the ViewDef applies its final presentation.
        private readonly bool _useStartupSplash;
        private Form _startupSplash;
        private Timer _startupDeadline;
        private bool _startupRevealed;

        [DllImport("dwmapi.dll", PreserveSig = true)]
        private static extern int DwmSetWindowAttribute(IntPtr hwnd, int attribute, ref int value, int size);

        private void SetNativeTitleBarDark(bool dark, bool launchPalette)
        {
            if (!IsHandleCreated) return;
            var enabled = dark ? 1 : 0;
            try
            {
                // Win10 20H1 / Win11; fallback for older Win10.
                if (DwmSetWindowAttribute(Handle, 20, ref enabled, sizeof(int)) != 0)
                    DwmSetWindowAttribute(Handle, 19, ref enabled, sizeof(int));
                if (dark)
                {
                    // Windows 11: match the FRB Launch palette where supported.
                    // DWM caption color is a single COLORREF, not a gradient.
                    // FRB Launch's gray-green gradient is approximately (85,97,90)
                    // in the middle of its title bar; use that as the solid-color match.
                    // Keep the original dark caption for other Studio dark themes.
                    var caption = ColorTranslator.ToWin32(launchPalette
                        ? Color.FromArgb(85, 97, 90)
                        : Color.FromArgb(32, 43, 41));
                    var titleText = ColorTranslator.ToWin32(Color.FromArgb(229, 235, 243));
                    DwmSetWindowAttribute(Handle, 35, ref caption, sizeof(int));
                    DwmSetWindowAttribute(Handle, 36, ref titleText, sizeof(int));
                }
            }
            catch (DllNotFoundException) { /* Windows without DWM */ }
            catch (EntryPointNotFoundException) { /* older Windows */ }
        }

        private void ApplyNativePresentation(string preset, string theme, string shell)
        {
            // ViewDef loading fixes the mode; do not expose a runtime switch.
            if (_presentationReceived) return;
            // A startup/default ViewDef may be loaded before the requested one.
            // It must not lock out the later launcher presentation.
            if (!string.Equals(preset, "launcher", StringComparison.OrdinalIgnoreCase)
                && !string.Equals(theme, "dark", StringComparison.OrdinalIgnoreCase)
                && !string.Equals(theme, "launch-dark", StringComparison.OrdinalIgnoreCase)) return;
            _presentationReceived = true;
            _launcherPresentation = string.Equals(preset, "launcher", StringComparison.OrdinalIgnoreCase)
                && string.Equals(shell, "minimal", StringComparison.OrdinalIgnoreCase);
            var dark = string.Equals(theme, "dark", StringComparison.OrdinalIgnoreCase)
                || string.Equals(theme, "launch-dark", StringComparison.OrdinalIgnoreCase);
            _nativeTitleBarDark = dark;
            _nativeTitleBarLaunchPalette = dark && string.Equals(theme, "launch-dark", StringComparison.OrdinalIgnoreCase);
            SetNativeTitleBarDark(dark, _nativeTitleBarLaunchPalette);
            if (dark)
            {
                _status.BackColor = Color.FromArgb(23, 35, 33);
                _status.ForeColor = Color.FromArgb(172, 188, 185);
            }
            if (!_launcherPresentation) return;
            Text = "FRB Launch — 設定";
            _status.Height = 20;
            // First launch: compact. Subsequent launches: restore manually resized bounds.
            if (NativeShellWindowBounds.TryLoad(out var bounds))
            {
                StartPosition = FormStartPosition.Manual;
                Bounds = bounds;
            }
            else
            {
                Size = new Size(990, 690);
                CenterToScreen();
            }
        }

        private void ShowStartupSplash()
        {
            if (!_useStartupSplash || _startupRevealed || _startupSplash != null) return;
            _startupSplash = new Form
            {
                Text = "FRB Studio",
                FormBorderStyle = FormBorderStyle.None,
                StartPosition = FormStartPosition.CenterScreen,
                ClientSize = new Size(330, 96),
                MaximizeBox = false,
                MinimizeBox = false,
                ControlBox = false,
                ShowInTaskbar = true,
                Padding = new Padding(1),
                BackColor = Color.FromArgb(82, 105, 101),
                ForeColor = Color.FromArgb(229, 235, 243)
            };
            var splashContent = new Panel { Dock = DockStyle.Fill, BackColor = Color.FromArgb(32, 43, 41) };
            splashContent.Controls.Add(new Label
            {
                Dock = DockStyle.Fill,
                Padding = new Padding(18, 13, 10, 8),
                Font = new Font(SystemFonts.MessageBoxFont.FontFamily, 11f),
                TextAlign = ContentAlignment.MiddleLeft,
                ForeColor = Color.FromArgb(229, 235, 243),
                Text = "FRB Studio  起動中...\n画面を準備しています"
            });
            _startupSplash.Controls.Add(splashContent);
            _startupSplash.Show();
            _startupSplash.Activate();

            // If the web app does not send its ready event (e.g. a script error),
            // show the host rather than leaving the user with a permanent splash.
            _startupDeadline = new Timer { Interval = 20000 };
            _startupDeadline.Tick += (_, __) => RevealMainWindow();
            _startupDeadline.Start();
        }

        private void RevealMainWindow()
        {
            if (!_useStartupSplash || _startupRevealed || IsDisposed) return;
            _startupRevealed = true;
            _startupDeadline?.Stop();
            _startupDeadline?.Dispose();
            _startupDeadline = null;

            // Presentation dimensions have already been applied by
            // ApplyNativePresentation; lay out the WebView before making it visible.
            PerformLayout();
            _webView.PerformLayout();
            Opacity = 1;
            ShowInTaskbar = true;
            // Changing ShowInTaskbar may recreate the HWND and clear DWM attrs.
            SetNativeTitleBarDark(_nativeTitleBarDark, _nativeTitleBarLaunchPalette);
            _startupSplash?.Close();
            _startupSplash?.Dispose();
            _startupSplash = null;
            Activate();
        }

        private void RevealAfterLayout()
        {
            if (!_useStartupSplash || _startupRevealed || !IsHandleCreated) return;
            // Defer one UI message turn so WinForms can finish Bounds/Layout updates.
            BeginInvoke(new Action(RevealMainWindow));
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            _startupDeadline?.Stop();
            _startupDeadline?.Dispose();
            _startupDeadline = null;
            _startupSplash?.Close();
            _startupSplash?.Dispose();
            _startupSplash = null;
            if (_launcherPresentation)
                NativeShellWindowBounds.TrySave(WindowState == FormWindowState.Normal ? Bounds : RestoreBounds);
            base.OnFormClosing(e);
        }


        public NativeShellForm(
            string initialUri = null,
            string initialPage = null,
            string initialJsonPath = null,
            string initialWorkspaceRoot = null,
            CoreWebView2Environment sharedEnvironment = null,
            bool deferInitialNavigation = false)
        {
            _initialUri = initialUri;
            _initialPage = initialPage;
            _initialJsonPath = initialJsonPath;
            _initialWorkspaceRoot = initialWorkspaceRoot;
            _sharedEnvironment = sharedEnvironment;
            _deferInitialNavigation = deferInitialNavigation;
            // Child/popup windows continue to use the normal visible startup path.
            _useStartupSplash = sharedEnvironment == null && !deferInitialNavigation;
            if (_useStartupSplash)
            {
                Opacity = 0;
                ShowInTaskbar = false;
            }
            Text = "FRB Studio / Native Shell";
            Width = 1500;
            Height = 950;
            StartPosition = FormStartPosition.CenterScreen;
		    var iconPath = Path.Combine(AppContext.BaseDirectory, "FRB_Studio.ico");
		    if (File.Exists(iconPath))
		    {
		        this.Icon = new Icon(iconPath);
		    }

            _status.Dock = DockStyle.Bottom;
            _status.Height = 24;
            _status.TextAlign = ContentAlignment.MiddleLeft;
            _status.Padding = new Padding(8, 0, 0, 0);
            _status.Text = "Native Shell 初期化中...";

            _webView.Dock = DockStyle.Fill;
            Controls.Add(_webView);
            Controls.Add(_status);

            ResizeEnd += (_, __) => {
                if (_launcherPresentation && WindowState == FormWindowState.Normal)
                    NativeShellWindowBounds.TrySave(Bounds);
            };
            Shown += async (_, __) => {
                ShowStartupSplash();
                await EnsureInitializedAsync();
            };
        }

        private Task EnsureInitializedAsync()
        {
            if (_initializationTask == null)
                _initializationTask = InitializeAsync();
            return _initializationTask;
        }

        private async Task<CoreWebView2> EnsureCoreWebViewReadyAsync()
        {
            await EnsureInitializedAsync();
            if (_webView.CoreWebView2 == null)
                throw new InvalidOperationException("Child WebView2 initialization failed.");
            return _webView.CoreWebView2;
        }

        private async Task InitializeAsync()
        {
            try
            {
                _appRoot = ResolveStudioAppRoot();
                var configPath = ResolveConfigPath();
                _config = NativeShellConfig.Load(configPath);
                _workspace = new WorkspacePolicy(
                    !string.IsNullOrWhiteSpace(_initialWorkspaceRoot) && Directory.Exists(_initialWorkspaceRoot)
                        ? _initialWorkspaceRoot
                        : _appRoot);
                _dispatcher = new NativeCommandDispatcher(_config, _workspace, _initialJsonPath);

                var webRoot = Path.Combine(_appRoot, "wwwroot");
                if (!File.Exists(Path.Combine(webRoot, _config.StartPage)))
                    throw new FileNotFoundException("Native Shell start page が見つかりません。", Path.Combine(webRoot, _config.StartPage));

                _allowedOrigin = "https://" + _config.VirtualHostName;
                var userDataFolder = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "FRBStudio",
                    "WebView2");
                Directory.CreateDirectory(userDataFolder);

                var runtimeVersion = CoreWebView2Environment.GetAvailableBrowserVersionString();
                _environment = _sharedEnvironment ?? await CoreWebView2Environment.CreateAsync(null, userDataFolder);
                await _webView.EnsureCoreWebView2Async(_environment);

                _webView.CoreWebView2.Settings.AreDevToolsEnabled = _config.DevToolsEnabled;
                _webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = true;
                _webView.CoreWebView2.Settings.IsStatusBarEnabled = false;
                _webView.CoreWebView2.SetVirtualHostNameToFolderMapping(
                    _config.VirtualHostName,
                    webRoot,
                    CoreWebView2HostResourceAccessKind.DenyCors);

                _webView.CoreWebView2.WebMessageReceived += OnWebMessageReceived;
                _webView.CoreWebView2.NavigationStarting += OnNavigationStarting;
                _webView.CoreWebView2.NewWindowRequested += OnNewWindowRequested;
                _webView.CoreWebView2.NavigationCompleted += (_, e) => {
                    if (!_useStartupSplash || _startupRevealed) return;
                    // index.html reports readiness AFTER auto-loading its Data/ViewDef.
                    // Other HTML tools have no such message, so show after navigation.
                    var page = _webView.Source?.AbsolutePath ?? "";
                    if (!e.IsSuccess || !page.EndsWith("/index.html", StringComparison.OrdinalIgnoreCase))
                        RevealAfterLayout();
                };

                _status.Text = "Native Shell / WebView2 Runtime " + runtimeVersion + " / App Root: " + _workspace.RootPath;
                if (!_deferInitialNavigation)
                {
                    var requestedPageUri = !string.IsNullOrWhiteSpace(_initialPage)
                        ? _allowedOrigin + "/" + _initialPage.TrimStart('/')
                        : null;
                    var startUri = !string.IsNullOrWhiteSpace(_initialUri) && IsAllowedNavigation(_initialUri)
                        ? _initialUri
                        : (!string.IsNullOrWhiteSpace(requestedPageUri) && IsAllowedNavigation(requestedPageUri)
                            ? requestedPageUri
                            : _allowedOrigin + "/" + _config.StartPage.TrimStart('/'));
                    _webView.Source = new Uri(startUri);
                }
            }
            catch (Exception ex)
            {
                // Close the splash before opening a modal error dialog.
                RevealMainWindow();
                _status.Text = "起動失敗: " + ex.Message;
                MessageBox.Show(
                    "FRB Studio Native Shell の起動に失敗しました。\n\n" +
                    ex.Message +
                    "\n\n追加インストールは自動実行しません。配布条件に合う環境か確認してください。",
                    "FRB Studio Native Shell",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        private async void OnWebMessageReceived(object sender, CoreWebView2WebMessageReceivedEventArgs e)
        {
            try
            {
                if (!IsAllowedSource(e.Source)) return;
                // UI-only profile message from the trusted Studio origin; never forward
                // to the file/command dispatcher or synthesize a bridge response.
                var message = new JavaScriptSerializer().DeserializeObject(e.WebMessageAsJson)
                    as Dictionary<string, object>;
                if (message != null && message.TryGetValue("studio_startup_ready", out var readyValue)
                    && readyValue is bool ready && ready)
                {
                    RevealAfterLayout();
                    return;
                }
                if (message != null && message.TryGetValue("studio_presentation", out var profileValue)
                    && profileValue is Dictionary<string, object> profile)
                {
                    string get(string key) => profile.TryGetValue(key, out var value) ? value as string : null;
                    ApplyNativePresentation(get("preset"), get("theme"), get("shell"));
                    return;
                }
                var responseJson = await _dispatcher.DispatchAsync(e.WebMessageAsJson, e.AdditionalObjects);
                _webView.CoreWebView2.PostWebMessageAsJson(responseJson);
                _status.Text = "Native Bridge: message processed / App Root: " + _workspace.RootPath;
            }
            catch (Exception ex)
            {
                _status.Text = "Native Bridge error: " + ex.Message;
            }
        }

        private void OnNavigationStarting(object sender, CoreWebView2NavigationStartingEventArgs e)
        {
            if (IsAllowedNavigation(e.Uri)) return;
            e.Cancel = true;
            if (_config.OpenExternalLinksInDefaultBrowser && Uri.TryCreate(e.Uri, UriKind.Absolute, out var uri))
                OpenExternal(uri.AbsoluteUri);
        }

        private async void OnNewWindowRequested(object sender, CoreWebView2NewWindowRequestedEventArgs e)
        {
            var deferral = e.GetDeferral();
            NativeShellForm child = null;
            try
            {
                if (IsAllowedNavigation(e.Uri))
                {
                    // Bind the JavaScript window.open() WindowProxy to the actual child WebView2.
                    // WebView2 requires the popup target to share the opener environment/profile and
                    // to remain un-navigated until assigned to NewWindow.
                    child = new NativeShellForm(
                        initialUri: null,
                        initialWorkspaceRoot: _workspace?.RootPath ?? _appRoot,
                        sharedEnvironment: _environment,
                        deferInitialNavigation: true);
                    child.Show(this);
                    e.NewWindow = await child.EnsureCoreWebViewReadyAsync();
                    return;
                }

                e.Handled = true;
                if (_config.OpenExternalLinksInDefaultBrowser && Uri.TryCreate(e.Uri, UriKind.Absolute, out var uri))
                    OpenExternal(uri.AbsoluteUri);
            }
            catch (Exception ex)
            {
                e.Handled = true;
                if (child != null && !child.IsDisposed)
                    child.Close();
                _status.Text = "Native Shell new-window error: " + ex.Message;
            }
            finally
            {
                deferral.Complete();
            }
        }

        private bool IsAllowedSource(string source)
        {
            if (!Uri.TryCreate(source, UriKind.Absolute, out var uri)) return false;
            return string.Equals(uri.Scheme, "https", StringComparison.OrdinalIgnoreCase)
                && string.Equals(uri.Host, _config.VirtualHostName, StringComparison.OrdinalIgnoreCase);
        }

        private bool IsAllowedNavigation(string uriText)
        {
            if (string.Equals(uriText, "about:blank", StringComparison.OrdinalIgnoreCase)) return true;
            if (!Uri.TryCreate(uriText, UriKind.Absolute, out var uri)) return false;
            return string.Equals(uri.Scheme, "https", StringComparison.OrdinalIgnoreCase)
                && string.Equals(uri.Host, _config.VirtualHostName, StringComparison.OrdinalIgnoreCase);
        }

        private static void OpenExternal(string uri)
        {
            try
            {
                Process.Start(new ProcessStartInfo(uri) { UseShellExecute = true });
            }
            catch { }
        }

        private string ResolveConfigPath()
        {
            var nextToExe = Path.Combine(AppContext.BaseDirectory, "native_shell.config.json");
            if (File.Exists(nextToExe)) return nextToExe;

            var sourceConfig = Path.Combine(_appRoot, "NativeShell", "native_shell.config.json");
            if (File.Exists(sourceConfig)) return sourceConfig;

            throw new FileNotFoundException("native_shell.config.json が見つかりません。");
        }

        private static string ResolveStudioAppRoot()
        {
            var starts = new[] { AppContext.BaseDirectory, Environment.CurrentDirectory };
            foreach (var start in starts)
            {
                var dir = new DirectoryInfo(Path.GetFullPath(start));
                while (dir != null)
                {
                    if (File.Exists(Path.Combine(dir.FullName, "wwwroot", "index.html"))
                        && Directory.Exists(Path.Combine(dir.FullName, "data", "json"))
                        && Directory.Exists(Path.Combine(dir.FullName, "defs")))
                        return dir.FullName;
                    dir = dir.Parent;
                }
            }

            throw new DirectoryNotFoundException("FRBStudio_App root を特定できません。");
        }
    }
}
