from studio_theme_launch import studio_launch_arguments


def test_studio_preserves_its_own_saved_theme_and_open_target():
    program = r'F:\FRB\tools\FRBStudio_App\NativeShell\_publish\FRBStudio.NativeShell.exe'
    assert studio_launch_arguments(program, ['--open-json=F:/file.json']) == [
        '--open-json=F:/file.json'
    ]
    assert studio_launch_arguments(program, ['--studio-theme=dark']) == ['--studio-theme=dark']
    assert studio_launch_arguments(program, ['--studio-theme=light']) == ['--studio-theme=light']
    assert studio_launch_arguments('notepad.exe', ['some.txt']) == ['some.txt']
    assert studio_launch_arguments(program, []) == []
