using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Threading.Tasks;
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
        private readonly string _initialWorkspaceRoot;
        private readonly CoreWebView2Environment _sharedEnvironment;
        private readonly bool _deferInitialNavigation;
        private CoreWebView2Environment _environment;
        private Task _initializationTask;

        public NativeShellForm(
            string initialUri = null,
            string initialPage = null,
            string initialWorkspaceRoot = null,
            CoreWebView2Environment sharedEnvironment = null,
            bool deferInitialNavigation = false)
        {
            _initialUri = initialUri;
            _initialPage = initialPage;
            _initialWorkspaceRoot = initialWorkspaceRoot;
            _sharedEnvironment = sharedEnvironment;
            _deferInitialNavigation = deferInitialNavigation;
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

            Shown += async (_, __) => await EnsureInitializedAsync();
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
                _dispatcher = new NativeCommandDispatcher(_config, _workspace);

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
                var responseJson = await _dispatcher.DispatchAsync(e.WebMessageAsJson);
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
