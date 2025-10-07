#!/usr/bin/env python3
"""
Safe consolidation script for 'agent templates' folder.
Run with --dry-run to see actions. Use --apply to perform moves/deletions.

This script will:
 - Identify common "project scaffold" files (.github, LICENSE, CONTRIBUTING.md, etc.) and optionally remove them
 - Propose moving prompt/chatmode/instructions folders from small repos into centralized 'prompt_kits/'
 - Propose centralizing common categories (rag_apps, starter_ai_agents, memory_agents, etc.) into 'collections/'

It is intentionally conservative: default is dry-run and it will never overwrite existing files unless --overwrite is specified.
"""

import argparse
import os
import shutil
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_TEMPLATES = ROOT / 'agent templates'

EXTRANEOUS_FILES = [
    '.github', '.gitignore', 'LICENSE', 'CONTRIBUTING.md',
    'CODE_OF_CONDUCT.md', 'README_TEMPLATE.md',
    'PULL_REQUEST_TEMPLATE.md', 'ISSUE_TEMPLATE',
]

CATEGORY_DIR = AGENT_TEMPLATES / 'collections'
PROMPT_KITS_DIR = AGENT_TEMPLATES / 'prompt_kits'


def is_project_dir(path_: Path):
    return (
        path_.is_dir()
        and path_.name
        not in ('.DS_Store', 'collections', 'prompt_kits', 'catalog')
    )


def compute_file_hash(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def compute_dir_signature(dir_path: Path):
    """Return a stable signature for a directory.

    The signature is the SHA256 of a sorted list of "relative-path:filehash"
    entries joined with a separator. This gives a stable fingerprint.
    """
    entries = []
    for root, _, files in os.walk(dir_path):
        rootp = Path(root)
        for fn in sorted(files):
            fp = rootp / fn
            try:
                h = compute_file_hash(fp)
            except OSError:
                # fallback: mark error so signature still builds
                h = 'ERR'
            rel = str(fp.relative_to(dir_path))
            entries.append(f"{rel}:{h}")
    joined = "|".join(entries)
    return hashlib.sha256(joined.encode('utf-8')).hexdigest()


def plan_consolidation():
    plan_map = {
        'deletions': [],
        'moves': [],
        'conflicts': [],
        'duplicates': [],
    }

    # Scan recursively for extraneous files/folders and for known categories.
    category_names = (
        'rag_apps', 'starter_ai_agents', 'memory_agents',
        'advance_ai_agents', 'mcp_ai_agents', 'simple_ai_agents',
    )
    prompt_subtrees = ('chatmodes', 'instructions', 'prompts')

    candidate_dirs = []

    for root, dirs, _ in os.walk(AGENT_TEMPLATES):
        rootp = Path(root)

        # deletable files/dirs
        for item in EXTRANEOUS_FILES:
            target = rootp / item
            if target.exists():
                try:
                    proj_name = target.relative_to(
                        AGENT_TEMPLATES
                    ).parts[0]
                except ValueError:
                    proj_name = target.name

                plan_map['deletions'].append(
                    {'project': proj_name, 'path': str(target)}
                )

        # categories: when we see a category folder, move each child project
        # directory into AGENT_TEMPLATES/collections/<category>/<project>
        for d in list(dirs):
            if d in category_names:
                src_cat = rootp / d
                # iterate child directories (projects) inside this category
                if src_cat.exists():
                    children = sorted(src_cat.iterdir())
                else:
                    children = []
                for child in children:
                    if not child.is_dir():
                        continue
                    # name of the project directory we will move
                    proj_name = child.name
                    dst = CATEGORY_DIR / d / proj_name
                    # safety: don't plan a move that would place src inside
                    # itself
                    try:
                        if dst.exists() and dst.samefile(child):
                            # nothing to do
                            continue
                    except OSError:
                        # ignore stat errors
                        pass

                    if dst.exists():
                        plan_map['conflicts'].append({
                            'from': str(child),
                            'to': str(dst),
                            'reason': 'destination exists',
                        })
                    else:
                        plan_map['moves'].append(
                            {'from': str(child), 'to': str(dst)}
                        )
                        candidate_dirs.append(child)

            # prompt subtrees: move chatmodes/instructions/prompts under
            # prompt_kits/<repo>/<subtree>
            if d in prompt_subtrees:
                if rootp == PROMPT_KITS_DIR:
                    continue
                src = rootp / d
                # determine repo name: first component after AGENT_TEMPLATES
                try:
                    parts = src.relative_to(AGENT_TEMPLATES).parts
                    # parts like ('prompt_kits', '<repo>', 'chatmodes')
                    if len(parts) > 1:
                        repo_name = parts[1]
                    elif len(parts) == 1:
                        repo_name = parts[0]
                    else:
                        repo_name = src.name
                except ValueError:
                    repo_name = src.name

                dst = PROMPT_KITS_DIR / repo_name / d
                # safety: avoid planning move into a path that is inside src
                try:
                    if dst.exists() and dst.samefile(src):
                        continue
                except OSError:
                    pass

                if dst.exists():
                    plan_map['conflicts'].append(
                        {
                            'from': str(src),
                            'to': str(dst),
                            'reason': 'destination exists',
                        }
                    )
                else:
                    plan_map['moves'].append(
                        {'from': str(src), 'to': str(dst)}
                    )
                    candidate_dirs.append(src)

    # Basic duplicate detection among candidate_dirs (and already existing
    # collections/prompt_kits)
    sig_map = {}
    for d in candidate_dirs:
        try:
            sig = compute_dir_signature(d)
        except OSError:
            sig = None
        if sig:
            sig_map.setdefault(sig, []).append(str(d))

    for sig, group in sig_map.items():
        if len(group) > 1:
            plan_map['duplicates'].append({'signature': sig, 'paths': group})

    return plan_map


def apply_plans(plan_map, apply=False, overwrite=False):
    result = {'deleted': [], 'moved': [], 'skipped': []}

    # deletions
    for d in plan_map['deletions']:
        path_obj = Path(d['path'])
        if apply:
            try:
                if path_obj.is_dir():
                    shutil.rmtree(path_obj)
                else:
                    path_obj.unlink()
                result['deleted'].append(d)
            except OSError as exc:
                result['skipped'].append(
                    {
                        'action': 'delete',
                        'path': str(path_obj),
                        'error': str(exc),
                    }
                )
        else:
            result['deleted'].append(d)

    # moves
    for m in plan_map['moves']:
        src = Path(m['from'])
        dst = Path(m['to'])
        if not src.exists():
            result['skipped'].append(
                {
                    'action': 'move',
                    'from': str(src),
                    'to': str(dst),
                    'reason': 'source missing',
                }
            )
            continue
        if dst.exists() and not overwrite:
            result['skipped'].append(
                {
                    'action': 'move',
                    'from': str(src),
                    'to': str(dst),
                    'reason': 'destination exists',
                }
            )
            continue
        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dst))
                result['moved'].append(m)
            except OSError as exc:
                result['skipped'].append(
                    {
                        'action': 'move',
                        'from': str(src),
                        'to': str(dst),
                        'error': str(exc),
                    }
                )
        else:
            result['moved'].append(m)

    # conflicts
    for c in plan_map.get('conflicts', []):
        result['skipped'].append({'action': 'conflict', **c})

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--apply', action='store_true',
        help='Actually perform moves and deletions',
    )
    parser.add_argument(
        '--overwrite', action='store_true',
        help='Overwrite existing destinations when moving',
    )
    parser.add_argument(
        '--report', type=str,
        help='Write JSON report to given path',
    )
    args = parser.parse_args()

    if not AGENT_TEMPLATES.exists():
        print(
            f"Error: expected agent templates directory at {AGENT_TEMPLATES}"
        )
        raise SystemExit(1)

    plans = plan_consolidation()
    report = apply_plans(plans, apply=args.apply, overwrite=args.overwrite)

    out = {'plans': plans, 'report': report}
    print(json.dumps(out, indent=2))

    if args.report:
        p = Path(args.report)
        p.write_text(json.dumps(out, indent=2), encoding='utf-8')

    if args.apply:
        print('\nApplied changes.')
    else:
        print('\nDry-run complete. No changes were made.')
