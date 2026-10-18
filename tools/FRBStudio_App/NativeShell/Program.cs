using System;
using System.Windows.Forms;
using System.Diagnostics;
using System.IO;

namespace FRBStudio.NativeShell
{
    internal static class Program
    {
        [STAThread]
        private static void Main(string[] args)
        {
            NativeLaunchOptions launchOptions;
            try { launchOptions = NativeLaunchOptions.Parse(args); }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "FRB Studio 起動引数", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }
            NativeAppIdentity.Ensure();
            var jumpListTimer = Stopwatch.StartNew();
            JumpListManager.TryRegisterTasks();
            jumpListTimer.Stop();
            // Opt-in timing for real Windows comparison (no noisy default log).
            if (Environment.GetEnvironmentVariable("FRB_STUDIO_STARTUP_PROFILING") == "1")
            {
                try
                {
                    var folder = Path.Combine(Environment.GetFolderPath(
                        Environment.SpecialFolder.LocalApplicationData), "FRBStudio");
                    Directory.CreateDirectory(folder);
                    File.AppendAllText(Path.Combine(folder, "startup_profile.log"),
                        DateTime.Now.ToString("s") + " JumpList_ms=" + jumpListTimer.ElapsedMilliseconds + Environment.NewLine);
                }
                catch { /* Diagnostics must not block startup. */ }
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new NativeShellForm(initialPage: launchOptions.InitialPage, initialJsonPath: launchOptions.InitialJsonPath, initialMarkdownPath: launchOptions.InitialMarkdownPath, startupTheme: launchOptions.StudioTheme));
        }
    }
}
