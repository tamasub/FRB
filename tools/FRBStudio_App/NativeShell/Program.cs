using System;
using System.Windows.Forms;

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
            JumpListManager.TryRegisterTasks();

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new NativeShellForm(initialPage: launchOptions.InitialPage, initialJsonPath: launchOptions.InitialJsonPath));
        }
    }
}
