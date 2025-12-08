# patch_speechbrain_symlinks.py
import os, shutil
import speechbrain.utils.fetching as fetching

def _safe_copy(src, dst, local_strategy="copy", *args, **kwargs):
    """
    Force SpeechBrain to always copy (never symlink),
    and safely handle dst=None (which happens during local audio loading).
    """
    # 1️⃣ Handle None or empty destination (SpeechBrain load_audio calls)
    if not dst:
        # Just return the source unchanged — don't copy anything
        return src

    # 2️⃣ Ensure destination directory exists
    os.makedirs(os.path.dirname(dst), exist_ok=True)

    # 3️⃣ Verify source exists
    if not os.path.exists(src):
        print(f"⚠️ SpeechBrain copy skipped — missing source: {src}")
        return src

    try:
        # 4️⃣ Copy files/folders
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
    except Exception as e:
        print(f"⚠️ SpeechBrain copy failed ({src} → {dst}): {e}")
    return dst

# Apply patch globally
fetching.link_with_strategy = _safe_copy
print("✅ Patched SpeechBrain to always use safe copy (no symlinks, handles dst=None).")
