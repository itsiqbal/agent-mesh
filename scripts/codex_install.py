#!/usr/bin/env python3
"""Install rendered adapters; Codex uses conservative manifest ownership."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

KIT = Path(__file__).resolve().parents[1]
BEGIN = b'<!-- BEGIN ai-agent-kit -->'
END = b'<!-- END ai-agent-kit -->'
TOOLS = {'claude', 'antigravity', 'opencode', 'codex'}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe(path: Path) -> None:
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'Refusing symlink path: {part}')
    if path.exists() and not path.is_file():
        raise ValueError(f'Expected file: {path}')


def split_block(data: bytes) -> tuple[bytes, bytes, bytes]:
    if data.count(BEGIN) != data.count(END) or data.count(BEGIN) > 1:
        raise ValueError('Malformed or duplicate rules markers')
    if BEGIN not in data:
        return data, b'', b''
    start, finish = data.index(BEGIN), data.index(END) + len(END)
    if finish <= start or data[start+len(BEGIN):start+len(BEGIN)+1] != b'\n' or (data.index(END) and data[data.index(END)-1:data.index(END)] != b'\n') or (start and data[start-1:start] != b'\n') or (finish < len(data) and data[finish:finish+1] != b'\n'):
        raise ValueError('Rules markers must be ordered and occupy complete lines')
    if finish < len(data):
        finish += 1
    return data[:start], data[start:finish], data[finish:]


def locations(tool: str, home: Path, codex: Path) -> tuple[Path, Path, list[Path]]:
    if tool == 'codex':
        return codex, codex/'AGENTS.md', [codex/'agents', home/'.agents/skills']
    if tool == 'claude':
        root = home/'.claude'
        return root, root/'CLAUDE.md', [root/'agents', root/'skills', root/'commands']
    if tool == 'antigravity':
        root = home/'.gemini'
        return root, root/'GEMINI.md', [root/'config/agents', root/'antigravity/skills', root/'config/skills', root/'antigravity/global_workflows']
    root = home/'.config/opencode'
    return root, root/'AGENTS.md', [root/'agents', root/'skills', root/'command']


def files(tool: str, stage: Path, roots: list[Path]) -> dict[Path, bytes]:
    result: dict[Path, bytes] = {}
    adapter = {'claude':'claude-code.md','antigravity':'antigravity.md','opencode':'opencode.md','codex':'codex.toml'}[tool]
    for role in sorted((stage/'agents').iterdir()):
        if role.is_dir():
            result[roots[0]/(role.name + ('.toml' if tool == 'codex' else '.md'))] = (role/adapter).read_bytes()
    for directory in sorted((KIT/'skills').iterdir()):
        if directory.is_dir():
            for source in sorted(directory.rglob('*')):
                if (source.is_file() and source.name != '.DS_Store'
                        and '__pycache__' not in source.relative_to(directory).parts
                        and source.suffix not in {'.pyc', '.pyo'}):
                    for destination in (roots[1:3] if tool == 'antigravity' else roots[1:2]):
                        result[destination/directory.name/source.relative_to(directory)] = source.read_bytes()
    for workflow in sorted((stage/'workflows').iterdir()):
        if not workflow.is_dir():
            continue
        if tool == 'codex':
            for source in sorted((workflow/'codex').rglob('*')):
                if source.is_file():
                    result[roots[1]/workflow.name/source.relative_to(workflow/'codex')] = source.read_bytes()
        else:
            result[roots[-1]/(workflow.name+'.md')] = (workflow/adapter).read_bytes()
    return result


def load_manifest(path: Path, roots: list[Path]) -> dict:
    safe(path)
    if not path.exists():
        return {'version':1, 'files':{}, 'rules_hash':None}
    value = json.loads(path.read_text())
    if not isinstance(value, dict) or value.get('version') != 1 or not isinstance(value.get('files'), dict):
        raise ValueError(f'Invalid manifest: {path}')
    for name, checksum in value['files'].items():
        target = Path(name)
        if not target.is_absolute() or '..' in target.parts or not any(target != root and target.is_relative_to(root) for root in roots):
            raise ValueError(f'Unsafe manifest path: {name}')
        if not isinstance(checksum, str) or len(checksum) != 64:
            raise ValueError(f'Invalid checksum: {name}')
        safe(target)
    checksum = value.get('rules_hash')
    if checksum is not None and (not isinstance(checksum, str) or len(checksum) != 64):
        raise ValueError(f'Invalid rules ownership: {path}')
    return value


def plan(tool: str, operation: str, stage: Path | None, home: Path, codex: Path) -> tuple[dict[Path, bytes | None], list[str]]:
    root, rules, roots = locations(tool, home, codex)
    manifest = root/'.ai-agent-kit-manifest.json'
    old = load_manifest(manifest, roots)
    safe(rules)
    desired = files(tool, stage, roots) if stage is not None else {}
    changes: dict[Path, bytes | None] = {}
    notices: list[str] = []
    retained: dict[str, str] = {}
    for target in sorted(set(desired) | {Path(name) for name in old['files']}):
        safe(target)
        owned = old['files'].get(str(target))
        current = target.read_bytes() if target.exists() else None
        if current is not None and owned is None:
            raise ValueError(f'Unmanaged file collision: {target}')
        if current is not None and digest(current) != owned:
            if operation == 'install':
                raise ValueError(f'Managed file was edited: {target}')
            notices.append(f'Preserved edited file: {target}')
            retained[str(target)] = owned
            continue
        replacement = desired.get(target)
        if current != replacement:
            changes[target] = replacement
        if replacement is not None:
            retained[str(target)] = digest(replacement)
    existing = rules.read_bytes() if rules.exists() else b''
    prefix, block, suffix = split_block(existing)
    owned = old.get('rules_hash')
    if block and (owned is None or digest(block) != owned):
        if operation == 'install':
            raise ValueError(f'Unmanaged or edited rules block: {rules}')
        notices.append(f'Preserved edited rules block: {rules}')
        rules_hash = owned
    else:
        replacement = b''
        if stage is not None:
            replacement = BEGIN+b'\n'+(KIT/'AGENTS.md').read_bytes().rstrip(b'\n')+b'\n'+END+b'\n'
            if not block:
                suffix, prefix = prefix, b''
        updated = prefix+replacement+suffix
        if updated != existing:
            changes[rules] = updated
        rules_hash = digest(replacement) if replacement else None
    if retained or rules_hash is not None:
        content = json.dumps({'version':1, 'files':retained, 'rules_hash':rules_hash}, indent=2, sort_keys=True).encode()+b'\n'
        if not manifest.exists() or manifest.read_bytes() != content:
            changes[manifest] = content
    elif manifest.exists():
        changes[manifest] = None
    return changes, notices


def legacy_plan(tool: str, operation: str, stage: Path | None, home: Path, codex: Path) -> tuple[dict[Path, bytes | None], list[str]]:
    """Retain historical overwrite/removal semantics for existing client installs."""
    _, rules, roots = locations(tool, home, codex)
    desired = files(tool, stage, roots) if stage is not None else {}
    changes: dict[Path, bytes | None] = dict(desired)
    if stage is None:
        adapter_suffix = '.md'
        for role in (KIT/'agents').iterdir():
            if role.is_dir():
                changes[roots[0]/(role.name+adapter_suffix)] = None
        for directory in (KIT/'skills').iterdir():
            if directory.is_dir():
                for destination in (roots[1:3] if tool == 'antigravity' else roots[1:2]):
                    skill = destination/directory.name
                    if skill.exists():
                        for source in skill.rglob('*'):
                            if source.is_file():
                                changes[source] = None
        for workflow in (KIT/'workflows').iterdir():
            if workflow.is_dir():
                changes[roots[-1]/(workflow.name+'.md')] = None
    safe(rules)
    existing = rules.read_bytes() if rules.exists() else b''
    prefix, block, suffix = split_block(existing)
    if stage is not None:
        if existing and not block:
            backup = Path(str(rules)+'.pre-ai-agent-kit.bak')
            if not backup.exists():
                changes[backup] = existing
        replacement = BEGIN+b'\n'+(KIT/'AGENTS.md').read_bytes().rstrip(b'\n')+b'\n'+END+b'\n'
        if prefix and not prefix.endswith(b'\n'):
            prefix += b'\n'
        changes[rules] = prefix+replacement+suffix
    elif block:
        changes[rules] = prefix+suffix
    for target in changes:
        safe(target)
    return changes, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('install','uninstall'))
    parser.add_argument('--only', default='claude,antigravity,opencode')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    selected = args.only.split(',')
    if any(tool not in TOOLS for tool in selected):
        parser.error('--only requires comma-separated claude,antigravity,opencode,codex')
    home = Path(os.environ['HOME']).absolute()
    codex = Path(os.environ.get('CODEX_HOME', str(home/'.codex'))).absolute()
    try:
        with tempfile.TemporaryDirectory(prefix='agent-kit-stage-') as temporary:
            stage = Path(temporary) if args.operation == 'install' else None
            if stage is not None:
                subprocess.run([sys.executable,str(KIT/'scripts/build_kit.py'),'--output-dir',str(stage)], check=True)
            changes: dict[Path, bytes | None] = {}
            notices: list[str] = []
            destinations: list[Path] = []
            for tool in dict.fromkeys(selected):
                root, _, _ = locations(tool, home, codex)
                if any(root.is_relative_to(other) or other.is_relative_to(root) for other in destinations):
                    raise ValueError('Selected tool roots overlap; use separate destinations')
                destinations.append(root)
                planner = plan if tool == 'codex' else legacy_plan
                updates, messages = planner(tool,args.operation,stage,home,codex)
                if set(updates) & set(changes):
                    raise ValueError('Selected tool destination files overlap')
                changes.update(updates)
                notices.extend(messages)
            for message in notices:
                print(message)
            for target, content in changes.items():
                print(f"{'[dry-run] ' if args.dry_run else ''}{'remove' if content is None else 'write'} {target}")
                if args.dry_run:
                    continue
                if content is None:
                    target.unlink(missing_ok=True)
                else:
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as output:
                        output.write(content)
                        temporary_file = Path(output.name)
                    temporary_file.replace(target)
            print(f'{args.operation.capitalize()} complete ({len(changes)} changes).')
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'Error: {error}',file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
