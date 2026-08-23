using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

namespace FRBStudio.NativeShell
{
    internal static class JumpListManager
    {
        public static void TryRegisterTasks()
        {
            try
            {
                NativeAppIdentity.Ensure();
                var removed = IntPtr.Zero;
                uint slots;
                var destinationList = (ICustomDestinationList)new CCustomDestinationList();
                destinationList.SetAppID(NativeAppIdentity.AppId);
                var objectArrayGuid = typeof(IObjectArray).GUID;
                destinationList.BeginList(out slots, ref objectArrayGuid, out removed);

                var tasks = (IObjectCollection)new CEnumerableObjectCollection();
                tasks.AddObject(CreateShellLink(
                    title: "Markdown Studioを開く",
                    arguments: "--launch=markdown",
                    description: "Markdown Studioを直接開きます。",
                    iconPath: ResolveMarkdownTaskIconPath(),
                    iconIndex: 0));

                foreach (var shortcut in NativeLaunchShortcutCatalog.Load())
                {
                    tasks.AddObject(CreateShellLink(
                        title: shortcut.Caption,
                        arguments: "--launch-shortcut=" + Uri.EscapeDataString(shortcut.Id),
                        description: "Studio設定の起動ショートカット: " + shortcut.DataPath,
                        iconPath: ResolveStudioTaskIconPath(),
                        iconIndex: 0));
                }

                destinationList.AddUserTasks((IObjectArray)tasks);
                destinationList.CommitList();
            }
            catch
            {
            }
        }

        private static IShellLinkW CreateShellLink(string title, string arguments, string description, string iconPath, int iconIndex)
        {
            var exePath = System.Diagnostics.Process.GetCurrentProcess().MainModule.FileName;
            var shellLink = (IShellLinkW)new CShellLink();
            shellLink.SetPath(exePath);
            shellLink.SetArguments(arguments);
            shellLink.SetDescription(description);
            if (!string.IsNullOrWhiteSpace(iconPath) && File.Exists(iconPath))
            {
                shellLink.SetIconLocation(iconPath, iconIndex);
            }

            var propertyStore = (IPropertyStore)shellLink;
            using (var pv = new PropVariant(title))
            {
                var titleKey = PropertyKey.Title;
                propertyStore.SetValue(ref titleKey, pv);
                propertyStore.Commit();
            }

            return shellLink;
        }

        private static string ResolveMarkdownTaskIconPath()
        {
            var nextToExe = Path.Combine(AppContext.BaseDirectory, "MarkdownStudio.ico");
            if (File.Exists(nextToExe)) return nextToExe;
            var source = Path.Combine(AppContext.BaseDirectory, "NativeShell", "MarkdownStudio.ico");
            if (File.Exists(source)) return source;
            return ResolveStudioTaskIconPath();
        }

        private static string ResolveStudioTaskIconPath()
        {
            var nextToExe = Path.Combine(AppContext.BaseDirectory, "FRB_Studio.ico");
            if (File.Exists(nextToExe)) return nextToExe;
            return Path.Combine(AppContext.BaseDirectory, "NativeShell", "FRB_Studio.ico");
        }

        [ComImport, Guid("77F10CF0-3DB5-4966-B520-B7C54FD35ED6")]
        private class CCustomDestinationList { }

        [ComImport, Guid("2D3468C1-36A7-43B6-AC24-D3F02FD9607A")]
        private class CEnumerableObjectCollection { }

        [ComImport, Guid("00021401-0000-0000-C000-000000000046")]
        private class CShellLink { }

        [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("6332DEBF-87B5-4670-90C0-5E57B408A49E")]
        private interface ICustomDestinationList
        {
            void SetAppID([MarshalAs(UnmanagedType.LPWStr)] string pszAppID);
            [PreserveSig] int BeginList(out uint cMinSlots, ref Guid riid, out IntPtr ppv);
            [PreserveSig] int AppendCategory([MarshalAs(UnmanagedType.LPWStr)] string pszCategory, IObjectArray poa);
            [PreserveSig] int AppendKnownCategory(KnownDestinationCategory category);
            [PreserveSig] int AddUserTasks(IObjectArray poa);
            [PreserveSig] int CommitList();
            [PreserveSig] int GetRemovedDestinations(ref Guid riid, out IntPtr ppv);
            [PreserveSig] int DeleteList([MarshalAs(UnmanagedType.LPWStr)] string pszAppID);
            [PreserveSig] int AbortList();
        }

        private enum KnownDestinationCategory
        {
            KDC_FREQUENT = 1,
            KDC_RECENT
        }

        [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("92CA9DCD-5622-4bba-A805-5E9F541BD8C9")]
        private interface IObjectArray
        {
            void GetCount(out uint pcObjects);
            void GetAt(uint uiIndex, ref Guid riid, [MarshalAs(UnmanagedType.Interface)] out object ppv);
        }

        [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("5632B1A4-E38A-400A-928A-D4CD63230295")]
        private interface IObjectCollection : IObjectArray
        {
            new void GetCount(out uint pcObjects);
            new void GetAt(uint uiIndex, ref Guid riid, [MarshalAs(UnmanagedType.Interface)] out object ppv);
            void AddObject([MarshalAs(UnmanagedType.Interface)] object pv);
            void AddFromArray(IObjectArray poaSource);
            void RemoveObjectAt(uint uiIndex);
            void Clear();
        }

        [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("000214F9-0000-0000-C000-000000000046")]
        private interface IShellLinkW
        {
            void GetPath([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszFile, int cch, IntPtr pfd, uint fFlags);
            void GetIDList(out IntPtr ppidl);
            void SetIDList(IntPtr pidl);
            void GetDescription([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszName, int cch);
            void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string pszName);
            void GetWorkingDirectory([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszDir, int cch);
            void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string pszDir);
            void GetArguments([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszArgs, int cch);
            void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string pszArgs);
            void GetHotkey(out short pwHotkey);
            void SetHotkey(short wHotkey);
            void GetShowCmd(out int piShowCmd);
            void SetShowCmd(int iShowCmd);
            void GetIconLocation([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pszIconPath, int cch, out int piIcon);
            void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string pszIconPath, int iIcon);
            void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string pszPathRel, uint dwReserved);
            void Resolve(IntPtr hwnd, uint fFlags);
            void SetPath([MarshalAs(UnmanagedType.LPWStr)] string pszFile);
        }

        [ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
        private interface IPropertyStore
        {
            uint GetCount([Out] out uint cProps);
            void GetAt([In] uint iProp, out PropertyKey pkey);
            void GetValue([In] ref PropertyKey key, [Out] PropVariant pv);
            void SetValue([In] ref PropertyKey key, [In] PropVariant pv);
            void Commit();
        }

        [StructLayout(LayoutKind.Sequential, Pack = 4)]
        private struct PropertyKey
        {
            public Guid fmtid;
            public uint pid;

            public PropertyKey(Guid formatId, uint propertyId)
            {
                fmtid = formatId;
                pid = propertyId;
            }

            public static readonly PropertyKey Title = new PropertyKey(new Guid("F29F85E0-4FF9-1068-AB91-08002B27B3D9"), 2);
        }

        [StructLayout(LayoutKind.Explicit)]
        private sealed class PropVariant : IDisposable
        {
            [FieldOffset(0)] private ushort valueType;
            [FieldOffset(8)] private IntPtr ptr;

            public PropVariant(string value)
            {
                valueType = 31;
                ptr = Marshal.StringToCoTaskMemUni(value);
            }

            public void Dispose()
            {
                PropVariantClear(this);
                GC.SuppressFinalize(this);
            }

            ~PropVariant()
            {
                Dispose();
            }

            [DllImport("ole32.dll")]
            private static extern int PropVariantClear([In, Out] PropVariant pvar);
        }
    }
}
