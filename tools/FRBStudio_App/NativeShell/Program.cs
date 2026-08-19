using System;
using System.Windows.Forms;

namespace FRBStudio.NativeShell
{
    internal static class Program
    {
        [STAThread]
        private static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            var launchOptions = NativeLaunchOptions.Parse(args);
            JumpListManager.TryInstall();

            Application.Run(new NativeShellForm(initialPage: launchOptions.InitialPage));
        }
    }
}
