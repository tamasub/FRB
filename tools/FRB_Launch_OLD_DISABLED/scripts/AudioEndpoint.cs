using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
namespace FrbAudio {
 [ComImport,Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class Enumerator {}
 [ComImport,Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IEnum {
  [PreserveSig] int EnumAudioEndpoints(int flow,uint mask,out ICollection devices);
  [PreserveSig] int GetDefaultAudioEndpoint(int flow,int role,out IDevice device);
  [PreserveSig] int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string id,out IDevice device);
  [PreserveSig] int RegisterEndpointNotificationCallback(IntPtr callback);
  [PreserveSig] int UnregisterEndpointNotificationCallback(IntPtr callback);
 }
 [ComImport,Guid("0BD7A1BE-7A1A-44DB-8397-CC5392387B5E"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface ICollection {
  [PreserveSig] int GetCount(out uint count);
  [PreserveSig] int Item(uint index,out IDevice device);
 }
 [ComImport,Guid("D666063F-1587-4E43-81F1-B948E807363F"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IDevice {
  [PreserveSig] int Activate(ref Guid iid,uint context,IntPtr parameters,out IntPtr result);
  [PreserveSig] int OpenPropertyStore(uint access,out IProperties store);
  [PreserveSig] int GetId([MarshalAs(UnmanagedType.LPWStr)] out string id);
  [PreserveSig] int GetState(out uint state);
 }
 [StructLayout(LayoutKind.Sequential)] struct Key { public Guid Format;public uint Id; }
 [StructLayout(LayoutKind.Explicit,Size=24)] struct Value { [FieldOffset(0)] public ushort Type;[FieldOffset(8)] public IntPtr Pointer; }
 [ComImport,Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IProperties {
  [PreserveSig] int GetCount(out uint count);
  [PreserveSig] int GetAt(uint index,out Key key);
  [PreserveSig] int GetValue(ref Key key,out Value value);
  [PreserveSig] int SetValue(ref Key key,ref Value value);
  [PreserveSig] int Commit();
 }
 // PolicyConfig is the Windows desktop COM interface used for changing defaults.
 [ComImport,Guid("F8679F50-850A-41CF-9C72-430F290290C8"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IPolicy {
  [PreserveSig] int GetMixFormat([MarshalAs(UnmanagedType.LPWStr)] string id,out IntPtr format);
  [PreserveSig] int GetDeviceFormat([MarshalAs(UnmanagedType.LPWStr)] string id,int mode,out IntPtr format);
  [PreserveSig] int ResetDeviceFormat([MarshalAs(UnmanagedType.LPWStr)] string id);
  [PreserveSig] int SetDeviceFormat([MarshalAs(UnmanagedType.LPWStr)] string id,IntPtr endpoint,IntPtr mix);
  [PreserveSig] int GetProcessingPeriod([MarshalAs(UnmanagedType.LPWStr)] string id,int mode,out long normal,out long minimum);
  [PreserveSig] int SetProcessingPeriod([MarshalAs(UnmanagedType.LPWStr)] string id,ref long period);
  [PreserveSig] int GetShareMode([MarshalAs(UnmanagedType.LPWStr)] string id,IntPtr mode);
  [PreserveSig] int SetShareMode([MarshalAs(UnmanagedType.LPWStr)] string id,IntPtr mode);
  [PreserveSig] int GetPropertyValue([MarshalAs(UnmanagedType.LPWStr)] string id,ref Key key,out Value value);
  [PreserveSig] int SetPropertyValue([MarshalAs(UnmanagedType.LPWStr)] string id,ref Key key,ref Value value);
  [PreserveSig] int SetDefaultEndpoint([MarshalAs(UnmanagedType.LPWStr)] string id,int role);
  [PreserveSig] int SetEndpointVisibility([MarshalAs(UnmanagedType.LPWStr)] string id,int visible);
 }
 public class Endpoint { public string Id;public string Name;public bool Default;public bool Communications; }
 public static class Audio {
  [DllImport("ole32.dll")] static extern int PropVariantClear(ref Value value);
  static void Check(int hr) { Marshal.ThrowExceptionForHR(hr); }
  static void Release(object value) { if(value!=null && Marshal.IsComObject(value)) Marshal.ReleaseComObject(value); }
  static string DefaultId(IEnum e,int role) {
   IDevice d=null;try { if(e.GetDefaultAudioEndpoint(0,role,out d)<0)return "";string id;Check(d.GetId(out id));return id; } finally {Release(d);}
  }
  public static Endpoint[] List() {
   IEnum e=(IEnum)new Enumerator();ICollection collection=null;
   try {
    Check(e.EnumAudioEndpoints(0,1,out collection));uint count;Check(collection.GetCount(out count));
    string normal=DefaultId(e,1),comm=DefaultId(e,2);var result=new List<Endpoint>();
    for(uint i=0;i<count;i++) {
     IDevice d=null;IProperties store=null;Value value=new Value();
     try {
      Check(collection.Item(i,out d));string id;Check(d.GetId(out id));Check(d.OpenPropertyStore(0,out store));
      Key key=new Key {Format=new Guid("A45C254E-DF1C-4EFD-8020-67D146A850E0"),Id=14};
      Check(store.GetValue(ref key,out value));string name=value.Type==31?Marshal.PtrToStringUni(value.Pointer):id;
      result.Add(new Endpoint {Id=id,Name=name,Default=id==normal,Communications=id==comm});
     } finally {PropVariantClear(ref value);Release(store);Release(d);}
    }
    return result.ToArray();
   } finally {Release(collection);Release(e);}
  }
  public static void Set(string id) {
   bool active=false;foreach(Endpoint d in List())if(d.Id==id)active=true;
   if(!active)throw new InvalidOperationException("Output device is disconnected, disabled, or missing. Reconnect it or register again.");
   object client=Activator.CreateInstance(Type.GetTypeFromCLSID(new Guid("870AF99C-171D-4F9E-AF0D-E63DF40C2BC9")));
   try {IPolicy p=(IPolicy)client;for(int role=0;role<3;role++)Check(p.SetDefaultEndpoint(id,role));} finally {Release(client);}
   IEnum e=(IEnum)new Enumerator();try {for(int role=0;role<3;role++)if(DefaultId(e,role)!=id)throw new InvalidOperationException("Default output verification failed.");} finally {Release(e);}
  }
 }
}
