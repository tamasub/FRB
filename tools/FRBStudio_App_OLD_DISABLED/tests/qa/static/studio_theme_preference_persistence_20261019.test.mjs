import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = path => fs.readFileSync(path, 'utf8');
test('Studio theme is loaded before splash; user settings outrank default and CLI outranks settings',()=>{
  const options=read('NativeShell/NativeLaunchOptions.cs');
  const preference=read('NativeShell/NativeStudioThemePreference.cs');
  const form=read('NativeShell/NativeShellForm.cs');
  assert.match(options,/StudioTheme = NativeStudioThemePreference.TryLoad\(\)/);
  assert.ok(options.indexOf('StudioTheme = NativeStudioThemePreference.TryLoad()') < options.indexOf('foreach (var raw in args)'));
  assert.match(options,/options.StudioTheme = theme.ToLowerInvariant\(\)/);
  assert.match(options,/"studioTheme=" \+ options.StudioTheme/);
  assert.match(options,/string.IsNullOrWhiteSpace\(options.InitialPage\) && explicitThemeArgument/);
  assert.match(options,/options.InitialPage != null &&/);
  assert.match(preference,/SpecialFolder.LocalApplicationData/);
  assert.match(preference,/studio_theme_preference\.json/);
  assert.match(preference,/Deserialize<Dictionary<string, string>>/);
  assert.match(form,/new StartupSplashForm\(_startupSplashLight\)/);
  assert.match(form,/NativeStudioThemePreference.TrySave\(theme\)/);
  assert.match(form,/preferenceSource.AbsolutePath, "\/index.html"/);
});
test('browser menu persists explicit selection instead of mutating ViewDef',()=>{
  const js=read('wwwroot/js/ui/studio_presentation_profile.js');
  assert.match(js,/saveThemePreference\(sessionTheme\)/);
  assert.match(js,/studio_theme_preference/);
  assert.match(js,/localStorage\?\.setItem/);
  assert.match(js,/if \(config.savePlacement === 'heading' && isLauncher\(config\)\)/);
  assert.doesNotMatch(js,/def\.app\.presentation\.theme\s*=/);
});
