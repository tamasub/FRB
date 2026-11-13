import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
OPT=(ROOT/'NativeShell/NativeLaunchOptions.cs').read_text(encoding='utf-8-sig')
JL=(ROOT/'NativeShell/JumpListManager.cs').read_text(encoding='utf-8-sig')
RUNTIME=(ROOT/'wwwroot/js/runtime/load_runtime.js').read_text(encoding='utf-8')

class NativeCliContractTests(unittest.TestCase):
    def test_properties_target_encoded_as_url_query(self):
        self.assertIn('options.InitialJsonPath == null',OPT)
        self.assertIn('&focusField=item_id&focusValue=',OPT)
        self.assertIn('Uri.EscapeDataString(options.LaunchItemId)',OPT)

    def test_new_category_only_with_explicit_data_json(self):
        self.assertIn('--launch-new-category=',OPT)
        self.assertIn('&launchNewCategory=1&newCategoryPage=',OPT)
        self.assertIn('if (launchTargets > 1)',OPT)

    def test_startup_load_and_focus(self):
        self.assertIn('!applyLaunchNewCategoryFromQuery(params) && !applyLaunchPageFromQuery(params)',RUNTIME)

    def test_page_group_target_does_not_invoke_details(self):
        self.assertIn('--launch-page-id=', OPT)
        self.assertIn('&launchPageId=', OPT)
        self.assertIn("state.selectedGroup = pageId", RUNTIME)
        self.assertIn("viewport.scrollTop = Math.max(0", RUNTIME)
        self.assertIn("selectedIndex = -1", RUNTIME)
        self.assertIn("row.focus({ preventScroll: true })", RUNTIME)

    def test_jumplist_cache_invalidation(self):
        self.assertIn('CurrentFingerprint()',JL)
        self.assertIn('File.ReadAllBytes(path)',JL)
        self.assertIn('File.GetLastWriteTimeUtc(exe)',JL)
        self.assertIn('destinationList.CommitList();',JL)
        self.assertIn('File.WriteAllText(marker, fingerprint)',JL)

if __name__=='__main__':unittest.main()
