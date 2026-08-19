using System;
using System.Windows.Forms;

namespace FRBStudio.NativeShell
{
    internal static class Program
    {
        [STAThread]
        private static void Main(string[] args)
        {
            var launchOptions = NativeLaunchOptions.Parse(args);
            NativeAppIdentity.Ensure();
            JumpListManager.TryRegisterTasks();

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new NativeShellForm(initialPage: launchOptions.InitialPage));
        }
    }
}
