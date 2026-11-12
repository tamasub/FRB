"""Session-only, Explorer-pane navigation history (not Launcher page history).

Only committed folder destinations are stored. A folder selected in Files'
first column is a destination just like a breadcrumb or a second-column folder.
Refresh/selection changes never create duplicate stops.
"""

import ntpath


class DirectoryNavigationHistory:
    def __init__(self, limit=100):
        self.limit = max(2, int(limit))
        self.entries = []
        self.index = -1

    @staticmethod
    def _key(path, rows):
        if path:
            return ('filesystem', ntpath.normcase(ntpath.normpath(str(path))))
        if rows:
            return ('virtual', tuple(str(row.get('item_id', '')) for row in rows))
        return None

    @property
    def can_back(self):
        return self.index > 0

    @property
    def can_forward(self):
        return 0 <= self.index < len(self.entries) - 1

    @property
    def current(self):
        return self.entries[self.index] if self.index >= 0 else None

    def record(self, path, rows, root_id=None, *, virtual_node=None,
               entry_origin=None, direct_root=None, registered_root=None):
        """Push a *new* destination, ignoring re-renders of the same folder."""
        if virtual_node is not None:
            key = ('launch_json', str(virtual_node.get('node_id', '')))
        elif entry_origin is not None and path:
            key = ('launch_mount', str(entry_origin['node']['node_id']),
                   self._key(path, rows)[1])
        elif direct_root and path:
            key = ('direct_path', self._key(direct_root, ())[1],
                   self._key(path, rows)[1])
        elif registered_root and path:
            key = ('registered_root', str(registered_root['root_id']),
                   self._key(path, rows)[1])
        else:
            key = self._key(path, rows)
        if key is None:
            return False
        entry = {'key': key, 'path': path, 'rows': list(rows),
                 'root_id': root_id, 'virtual_node': virtual_node,
                 'entry_origin': dict(entry_origin) if entry_origin else None,
                 'direct_root': direct_root,
                 'registered_root': dict(registered_root) if registered_root else None}
        if self.current is not None and self.current['key'] == key:
            self.entries[self.index] = entry
            return False
        del self.entries[self.index + 1:]
        self.entries.append(entry)
        overflow = len(self.entries) - self.limit
        if overflow > 0:
            del self.entries[:overflow]
        self.index = len(self.entries) - 1
        return True

    def back(self):
        if not self.can_back:
            return None
        self.index -= 1
        return self.current

    def forward(self):
        if not self.can_forward:
            return None
        self.index += 1
        return self.current
