using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;

namespace FRBStudio.NativeShell
{
    /// <summary>
    /// Windows taskbar Jump List registration for Native Shell launch shortcuts.
    /// Keep this layer Windows-shell-only; Studio page routing stays in NativeLaunchOptions.
    /// </summary>
    internal static class JumpListManager
    {
        private static readonly Guid IidObjectArray = new Guid("92CA9DCD-5622-4BBA-A805-5E9F541BD8C9");
        private static readonly PropertyKey PkeyTitle = new PropertyKey(
            new Guid("F29F85E0-4FF9-1068-AB91-08002B27B3D9"), 2);

        public static void TryInstall()
        {
            if (Environment.OSVersion.Platform != PlatformID.Win32NT) return;

            ICustomDestinationList destinationList = null;
            IObjectCollection tasks = null;
            IShellLinkW markdownTask = null;
            object removedDestinations = null;

            try
            {
                destinationList = (ICustomDestinationList)new CustomDestinationListComObject();
                uint maxSlots;
                var iid = IidObjectArray;
                ThrowIfFailed(destinationList.BeginList(out maxSlots, ref iid, out removedDestinations));

                tasks = (IObjectCollection)new EnumerableObjectCollectionComObject();
                markdownTask = CreateTaskLink(
                    Application.ExecutablePath,
                    "--launch=markdown",
                    "Markdown Studioを開く");
                ThrowIfFailed(tasks.AddObject(markdownTask));

                ThrowIfFailed(destinationList.AddUserTasks((IObjectArray)tasks));
                ThrowIfFailed(destinationList.CommitList());
            }
            catch
            {
                // Jump List is a convenience entry point. It must never block FRB Studio startup.
                try { destinationList?.AbortList(); } catch { }
            }
            finally
            {
                ReleaseCom(markdownTask);
                ReleaseCom(tasks);
                ReleaseCom(removedDestinations);
                ReleaseCom(destinationList);
            }
        }

        private static IShellLinkW CreateTaskLink(string executablePath, string arguments, string title)
        {
            var link = (IShellLinkW)new ShellLinkComObject();
            ThrowIfFailed(link.SetPath(executablePath));
            ThrowIfFailed(link.SetArguments(arguments));
            ThrowIfFailed(link.SetDescription(title));
            ThrowIfFailed(link.SetIconLocation(executablePath, 0));

            var propertyStore = (IPropertyStore)link;
            using (var value = PropVariant.FromString(title))
            {
                var key = PkeyTitle;
                var propertyValue = value;
                ThrowIfFailed(propertyStore.SetValue(ref key, ref propertyValue));
                ThrowIfFailed(propertyStore.Commit());
            }

            return link;
        }

        private static void ThrowIfFailed(int hresult)
        {
            if (hresult < 0) Marshal.ThrowExceptionForHR(hresult);
        }

        private static void ReleaseCom(object value)
        {
            if (value != null && Marshal.IsComObject(value))
            {
                try { Marshal.FinalReleaseComObject(value); } catch { }
            }
        }

        [StructLayout(LayoutKind.Sequential, Pack = 4)]
        private struct PropertyKey
        {
            public Guid FormatId;
            public uint PropertyId;

            public PropertyKey(Guid formatId, uint propertyId)
            {
                FormatId = formatId;
                PropertyId = propertyId;
            }
        }

        [StructLayout(LayoutKind.Explicit)]
        private struct PropVariant : IDisposable
        {
            [FieldOffset(0)] private ushort _variantType;
            [FieldOffset(8)] private IntPtr _pointerValue;

            public static PropVariant FromString(string value)
            {
                return new PropVariant
                {
                    _variantType = 31, // VT_LPWSTR
                    _pointerValue = Marshal.StringToCoTaskMemUni(value ?? string.Empty)
                };
            }

            public void Dispose()
            {
                if (_pointerValue != IntPtr.Zero)
                {
                    Marshal.FreeCoTaskMem(_pointerValue);
                    _pointerValue = IntPtr.Zero;
                }
                _variantType = 0;
            }
        }

        [ComImport]
        [Guid("77F10CF0-3DB5-4966-B520-B7C54FD35ED6")]
        [ClassInterface(ClassInterfaceType.None)]
        private class CustomDestinationListComObject { }

        [ComImport]
        [Guid("2D3468C1-36A7-43B6-AC24-D3F02FD9607A")]
        [ClassInterface(ClassInterfaceType.None)]
        private class EnumerableObjectCollectionComObject { }

        [ComImport]
        [Guid("00021401-0000-0000-C000-000000000046")]
        [ClassInterface(ClassInterfaceType.None)]
        private class ShellLinkComObject { }

        [ComImport]
        [Guid("6332DEBF-87B5-4670-90C0-5E57B408A49E")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface ICustomDestinationList
        {
            [PreserveSig] int SetAppID([MarshalAs(UnmanagedType.LPWStr)] string appId);
            [PreserveSig] int BeginList(out uint minSlots, ref Guid interfaceId, [MarshalAs(UnmanagedType.Interface)] out object removedDestinations);
            [PreserveSig] int AppendCategory([MarshalAs(UnmanagedType.LPWStr)] string category, [MarshalAs(UnmanagedType.Interface)] IObjectArray objects);
            [PreserveSig] int AppendKnownCategory(uint category);
            [PreserveSig] int AddUserTasks([MarshalAs(UnmanagedType.Interface)] IObjectArray objects);
            [PreserveSig] int CommitList();
            [PreserveSig] int GetRemovedDestinations(ref Guid interfaceId, [MarshalAs(UnmanagedType.Interface)] out object removedDestinations);
            [PreserveSig] int DeleteList([MarshalAs(UnmanagedType.LPWStr)] string appId);
            [PreserveSig] int AbortList();
        }

        [ComImport]
        [Guid("92CA9DCD-5622-4BBA-A805-5E9F541BD8C9")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface IObjectArray
        {
            [PreserveSig] int GetCount(out uint count);
            [PreserveSig] int GetAt(uint index, ref Guid interfaceId, [MarshalAs(UnmanagedType.Interface)] out object value);
        }

        [ComImport]
        [Guid("5632B1A4-E38A-400A-928A-D4CD63230295")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface IObjectCollection : IObjectArray
        {
            [PreserveSig] new int GetCount(out uint count);
            [PreserveSig] new int GetAt(uint index, ref Guid interfaceId, [MarshalAs(UnmanagedType.Interface)] out object value);
            [PreserveSig] int AddObject([MarshalAs(UnmanagedType.Interface)] object value);
            [PreserveSig] int AddFromArray([MarshalAs(UnmanagedType.Interface)] IObjectArray source);
            [PreserveSig] int RemoveObjectAt(uint index);
            [PreserveSig] int Clear();
        }

        [ComImport]
        [Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface IPropertyStore
        {
            [PreserveSig] int GetCount(out uint propertyCount);
            [PreserveSig] int GetAt(uint index, out PropertyKey key);
            [PreserveSig] int GetValue(ref PropertyKey key, out PropVariant value);
            [PreserveSig] int SetValue(ref PropertyKey key, ref PropVariant value);
            [PreserveSig] int Commit();
        }

        [ComImport]
        [Guid("000214F9-0000-0000-C000-000000000046")]
        [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
        private interface IShellLinkW
        {
            [PreserveSig] int GetPath([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder file, int maxPath, IntPtr findData, uint flags);
            [PreserveSig] int GetIDList(out IntPtr itemIdList);
            [PreserveSig] int SetIDList(IntPtr itemIdList);
            [PreserveSig] int GetDescription([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder description, int maxName);
            [PreserveSig] int SetDescription([MarshalAs(UnmanagedType.LPWStr)] string description);
            [PreserveSig] int GetWorkingDirectory([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder directory, int maxPath);
            [PreserveSig] int SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string directory);
            [PreserveSig] int GetArguments([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder arguments, int maxPath);
            [PreserveSig] int SetArguments([MarshalAs(UnmanagedType.LPWStr)] string arguments);
            [PreserveSig] int GetHotkey(out short hotkey);
            [PreserveSig] int SetHotkey(short hotkey);
            [PreserveSig] int GetShowCmd(out int showCommand);
            [PreserveSig] int SetShowCmd(int showCommand);
            [PreserveSig] int GetIconLocation([Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder iconPath, int iconPathLength, out int iconIndex);
            [PreserveSig] int SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string iconPath, int iconIndex);
            [PreserveSig] int SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string path, uint reserved);
            [PreserveSig] int Resolve(IntPtr windowHandle, uint flags);
            [PreserveSig] int SetPath([MarshalAs(UnmanagedType.LPWStr)] string file);
        }
    }
}
