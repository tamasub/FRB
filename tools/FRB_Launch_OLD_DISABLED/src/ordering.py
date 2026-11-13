"""Persist the visual order of registered siblings without changing their parents."""
import copy
import json
import os
from pathlib import Path
import tempfile
from core import validate


def reordered(data, page, parent, ids):
    result=copy.deepcopy(data)
    siblings=sorted([r for r in result['items'] if r['page_id']==page and r.get('parent_item_id','')==parent],key=lambda r:r.get('sort_order',0))
    visible={r['item_id']:r for r in siblings if r.get('enabled',True)}
    if len(ids)!=len(visible) or set(ids)!=set(visible):
        raise ValueError('並べ替え対象が変わっています。再読込してから操作してください')
    ordered=iter(visible[i] for i in ids)
    # Hidden siblings keep their slots; only registered visible siblings move.
    siblings=[next(ordered) if r.get('enabled',True) else r for r in siblings]
    for index,row in enumerate(siblings,1):row['sort_order']=index*10
    return validate(result)


def save_order(path, expected_mtime, page, parent, ids):
    path=Path(path)
    if path.stat().st_mtime_ns!=expected_mtime:
        raise ValueError('設定JSONが更新されています。再読込してから並べ替えてください')
    original=path.read_bytes()
    data=reordered(json.loads(original.decode('utf-8-sig')),page,parent,ids)
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix=path.name+'.',suffix='.tmp',delete=False) as f:
            temporary=Path(f.name)
            f.write((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
            f.flush();os.fsync(f.fileno())
        if path.stat().st_mtime_ns!=expected_mtime or path.read_bytes()!=original:
            raise ValueError('設定JSONが更新されています。再読込してから並べ替えてください')
        os.replace(temporary,path)
        return data,path.stat().st_mtime_ns
    finally:
        if temporary:temporary.unlink(missing_ok=True)
