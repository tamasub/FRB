using System;
using System.Runtime.InteropServices;

namespace FRBStudio.NativeShell
{
    internal static class NativeAppIdentity
    {
        public const string AppId = "FRBStudio.NativeShell";

        [DllImport("shell32.dll", CharSet = CharSet.Unicode)]
        private static extern int SetCurrentProcessExplicitAppUserModelID(string appID);

        public static void Ensure()
        {
            try
            {
                SetCurrentProcessExplicitAppUserModelID(AppId);
            }
            catch
            {
            }
        }
    }
}
