using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
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
        // Frame-owned content: launcher theme gets an outer charcoal rim and
        // an inner light line without replacing the standard WinForms title bar.
        private readonly Panel _clientSurface = new Panel();
        private NativeShellConfig _config;
        private WorkspacePolicy _workspace;
        private NativeCommandDispatcher _dispatcher;
        private string _appRoot;
        private string _allowedOrigin;
        private readonly string _initialUri;
        private readonly string _initialPage;
        private readonly string _initialJsonPath;
        private readonly string _initialMarkdownPath;
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
                    // Windows 11 non-client border: dark-gray ring around the full window.
                    var border = ColorTranslator.ToWin32(launchPalette
                        ? Color.FromArgb(52, 60, 56)
                        : Color.FromArgb(32, 43, 41));
                    DwmSetWindowAttribute(Handle, 34, ref border, sizeof(int));
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
            // FRB Launch has a noticeably wider rim than a DWM 1px border.
            // Preserve the native caption/buttons, but inset the whole client area
            // with a charcoal 5px border and a thin gray-green inner hairline.
            // The content surface has zero padding for normal Studio themes.
            if (_launcherPresentation && _nativeTitleBarLaunchPalette)
            {
                Padding = new Padding(5);
                BackColor = Color.FromArgb(51, 62, 56);
                _clientSurface.Padding = new Padding(1);
                _clientSurface.BackColor = Color.FromArgb(180, 191, 180);
            }
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

        // Borderless splash is styled explicitly: WinForms default Font/Frame
        // otherwise looks unrelated to the WebView2 Studio + Qt launcher.
        private sealed class StartupSplashForm : Form
        {
            private const int Radius = 12;
            private readonly Font _headlineFont = new Font("Segoe UI", 10.5f, FontStyle.Regular);
            private readonly Font _subtitleFont = new Font("Segoe UI", 9f, FontStyle.Regular);

            internal StartupSplashForm()
            {
                Text = "FRB Studio  起動中...";
                FormBorderStyle = FormBorderStyle.None;
                StartPosition = FormStartPosition.CenterScreen;
                ClientSize = new Size(340, 112);
                MaximizeBox = false;
                MinimizeBox = false;
                ControlBox = false;
                ShowInTaskbar = true;
                BackColor = Color.FromArgb(32, 43, 41);
                DoubleBuffered = true;
            }

            // Add the standard Windows window shadow while keeping the rounded
            // borderless shape (no custom activation or focus management).
            protected override CreateParams CreateParams
            {
                get
                {
                    var parameters = base.CreateParams;
                    parameters.ClassStyle |= 0x00020000; // CS_DROPSHADOW
                    return parameters;
                }
            }

            private static GraphicsPath RoundedRectangle(Rectangle rect, int radius)
            {
                var path = new GraphicsPath();
                var diameter = radius * 2;
                path.AddArc(rect.Left, rect.Top, diameter, diameter, 180, 90);
                path.AddArc(rect.Right - diameter, rect.Top, diameter, diameter, 270, 90);
                path.AddArc(rect.Right - diameter, rect.Bottom - diameter, diameter, diameter, 0, 90);
                path.AddArc(rect.Left, rect.Bottom - diameter, diameter, diameter, 90, 90);
                path.CloseFigure();
                return path;
            }

            protected override void OnResize(EventArgs e)
            {
                base.OnResize(e);
                if (ClientSize.Width < Radius * 2 || ClientSize.Height < Radius * 2) return;
                using (var path = RoundedRectangle(new Rectangle(0, 0, ClientSize.Width, ClientSize.Height), Radius))
                {
                    var previous = Region;
                    Region = new Region(path);
                    previous?.Dispose();
                }
            }

            protected override void OnPaint(PaintEventArgs e)
            {
                base.OnPaint(e);
                var g = e.Graphics;
                g.SmoothingMode = SmoothingMode.AntiAlias;
                var outer = new Rectangle(0, 0, ClientSize.Width - 1, ClientSize.Height - 1);
                using (var path = RoundedRectangle(outer, Radius))
                using (var header = new LinearGradientBrush(outer,
                    Color.FromArgb(104, 116, 107), Color.FromArgb(55, 71, 62), 90f))
                using (var border = new Pen(Color.FromArgb(193, 203, 192)))
                {
                    g.FillPath(header, path);
                    g.DrawPath(border, path);
                }
                var inner = Rectangle.Inflate(outer, -5, -5);
                using (var path = RoundedRectangle(inner, Radius - 4))
                using (var fill = new SolidBrush(Color.FromArgb(32, 43, 41)))
                using (var outline = new Pen(Color.FromArgb(101, 122, 112)))
                {
                    g.FillPath(fill, path);
                    g.DrawPath(outline, path);
                }
                // Align BOTH lines centrally, using Studio's Segoe UI stack;
                // Windows supplies its normal Japanese glyph fallback.
                var headline = new Rectangle(16, 28, ClientSize.Width - 32, 28);
                var subtitle = new Rectangle(16, 59, ClientSize.Width - 32, 25);
                const TextFormatFlags centered = TextFormatFlags.HorizontalCenter
                    | TextFormatFlags.VerticalCenter | TextFormatFlags.NoPrefix | TextFormatFlags.SingleLine;
                TextRenderer.DrawText(g, "FRB Studio  起動中...", _headlineFont, headline,
                    Color.FromArgb(235, 241, 238), centered);
                TextRenderer.DrawText(g, "画面を準備しています", _subtitleFont, subtitle,
                    Color.FromArgb(170, 188, 180), centered);
            }

            protected override void Dispose(bool disposing)
            {
                if (disposing) { _headlineFont.Dispose(); _subtitleFont.Dispose(); }
                base.Dispose(disposing);
            }
        }

        private void ShowStartupSplash()
        {
            if (!_useStartupSplash || _startupRevealed || _startupSplash != null) return;
            _startupSplash = new StartupSplashForm();
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
            // Mouse activation from the Qt launcher can leave the WebView2
            // unfocused even though its outer WinForms window is foreground.
            // Always pass keyboard focus to the content after splash removal.
            if (_webView.CanFocus) _webView.Focus();
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
            bool deferInitialNavigation = false,
            string initialMarkdownPath = null)
        {
            _initialUri = initialUri;
            _initialPage = initialPage;
            _initialJsonPath = initialJsonPath;
            _initialMarkdownPath = initialMarkdownPath;
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
            _clientSurface.Dock = DockStyle.Fill;
            _clientSurface.Padding = new Padding(0);
            _clientSurface.Controls.Add(_webView);
            _clientSurface.Controls.Add(_status);
            Controls.Add(_clientSurface);

            ResizeEnd += (_, __) => {
                if (_launcherPresentation && WindowState == FormWindowState.Normal)
                    NativeShellWindowBounds.TrySave(Bounds);
            };
            Shown += async (_, __) => {
                ShowStartupSplash();
                await EnsureInitializedAsync();
            };
        }

        // WebView2 JS handles Ctrl+Q when the page has focus.  WinForms must
        // also route it when mouse launching left focus on the native chrome.
        // Both routes invoke the same JS unsaved-guard before Form.Close().
        protected override bool ProcessCmdKey(ref Message msg, Keys keyData)
        {
            if (keyData == (Keys.Control | Keys.Q)
                && _webView.CoreWebView2 != null
                && _webView.Source != null
                && string.Equals(_webView.Source.AbsolutePath, "/index.html", StringComparison.OrdinalIgnoreCase))
            {
                _ = RequestCloseFromNativeShortcutAsync();
                return true;
            }
            return base.ProcessCmdKey(ref msg, keyData);
        }

        private async Task RequestCloseFromNativeShortcutAsync()
        {
            try
            {
                await _webView.CoreWebView2.ExecuteScriptAsync(
                    "window.__frbStudioRequestClose?.();");
            }
            catch (Exception ex)
            {
                _status.Text = "Studio 終了ショートカット: " + ex.Message;
            }
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
                _dispatcher = new NativeCommandDispatcher(_config, _workspace, _initialJsonPath, _initialMarkdownPath);

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
                // Ctrl+Q from the trusted Studio main page closes this WinForms form
                // through the same Close() / OnFormClosing path as the title-bar X.
                // The page checks the unsaved guard before sending this request.
                if (message != null && message.TryGetValue("studio_close_request", out var closeValue)
                    && closeValue is bool closeRequested && closeRequested
                    && Uri.TryCreate(e.Source, UriKind.Absolute, out var closeSource)
                    && string.Equals(closeSource.AbsolutePath, "/index.html", StringComparison.OrdinalIgnoreCase))
                {
                    if (!IsDisposed && IsHandleCreated)
                        BeginInvoke(new Action(Close));
                    return;
                }
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
