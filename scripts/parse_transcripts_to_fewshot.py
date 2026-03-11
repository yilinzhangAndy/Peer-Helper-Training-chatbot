#!/usr/bin/env python3
"""
Parse WEBVTT transcripts and DOCX transcripts from real dialogue folder into Few-Shot format.
Extracts Advisor -> Student turn pairs (consecutive, correctly ordered).
Output: data/real_dialogue_transcripts.json
"""
import re
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Tuple, Set

TRANSCRIPTS_DIR = Path(__file__).parent.parent / "real dialogue" / "ALL"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "real_dialogue_transcripts.json"


def _is_advisor_webvtt(speaker: str) -> bool:
    return "peer advisor" in speaker.lower()


def _is_student_webvtt(speaker: str) -> bool:
    return not _is_advisor_webvtt(speaker)


def _student_names_from_filename(filename: str) -> Set[str]:
    """从文件名推断学生姓名（用于 DOCX）。支持 'Bauer alyssa' -> Alyssa Bauer，'Santiago Fernandez 2' -> Santiago Fernandez。"""
    stem = Path(filename).stem
    stem_clean = re.sub(r"\s*\d+\s*$", "", stem).strip()
    if stem.startswith("ID ") or not stem_clean.replace(" ", "").replace("-", "").isalpha():
        return set()
    parts = [p for p in stem_clean.split() if not p.isdigit()]
    names = {stem_clean, stem_clean.lower(), stem_clean.title()}
    if len(parts) == 2:
        names.add(f"{parts[1]} {parts[0]}")
        names.add(f"{parts[1].title()} {parts[0].title()}")
    elif len(parts) >= 3:
        names.add(f"{parts[-1]} {parts[0]}")
        names.add(" ".join(p.title() for p in parts))
    return names


def _normalize_speaker(speaker: str) -> str:
    """将 'Daniel Mata Daniel Mata' 规范为 'Daniel Mata'。"""
    s = speaker.strip()
    parts = s.split()
    if len(parts) >= 4 and parts[:2] == parts[2:4]:
        return " ".join(parts[:2])
    return s


def _infer_student_from_id_file(turns: List[Tuple[str, str]]) -> Set[str]:
    """
    ID 文件无学生姓名：取前两个不同说话人，假设先出现的为顾问、后出现的为学生。
    """
    seen = []
    for speaker, _ in turns[:15]:
        s = _normalize_speaker(speaker)
        if not s or len(s) < 4 or any(c.isdigit() for c in s):
            continue
        if s not in seen:
            seen.append(s)
        if len(seen) >= 2:
            return {seen[1], seen[1].lower(), seen[1].title()}
    return set()


def parse_webvtt(content: str) -> List[Tuple[str, str]]:
    """
    Parse WEBVTT content into list of (speaker, text) turns.
    Merges consecutive same-speaker utterances.
    """
    lines = content.split("\n")
    turns = []
    current_speaker = None
    current_text = []

    for line in lines:
        line = line.strip()
        if not line or line == "WEBVTT" or re.match(r"^\d+$", line) or " --> " in line:
            continue
        # Format: "Peer Advisor 2: Hello" or "Student 14: Yeah"
        match = re.match(r"^([^:]+):\s*(.*)$", line, re.IGNORECASE)
        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()
            if not text:
                continue
            if current_speaker == speaker:
                current_text.append(text)
            else:
                if current_speaker and current_text:
                    turns.append((current_speaker, " ".join(current_text)))
                current_speaker = speaker
                current_text = [text]

    if current_speaker and current_text:
        turns.append((current_speaker, " ".join(current_text)))

    return turns


def extract_pairs(
    turns: List[Tuple[str, str]],
    is_advisor=None,
    is_student=None,
) -> List[Dict[str, str]]:
    """
    Extract Advisor -> Student pairs from turns.
    When advisor speaks, the next student utterance(s) form the response.
    """
    is_adv = is_advisor or _is_advisor_webvtt
    is_stu = is_student or _is_student_webvtt
    pairs = []
    i = 0
    while i < len(turns):
        speaker, text = turns[i]
        if is_adv(speaker):
            advisor_text = text
            student_parts = []
            j = i + 1
            while j < len(turns) and is_stu(turns[j][0]):
                student_parts.append(turns[j][1])
                j += 1
            if student_parts and len(advisor_text) > 15 and len(" ".join(student_parts)) > 10:
                pairs.append({
                    "advisor": advisor_text,
                    "student": " ".join(student_parts),
                    "intent": None,
                    "persona": None,
                    "source": "real_transcript"
                })
            i = j
        else:
            i += 1
    return pairs


def _extract_text_from_docx(path: Path) -> str:
    """从 DOCX 提取纯文本（无需 python-docx）。"""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    return " ".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))


def parse_docx(content: str, student_names: Set[str]) -> List[Tuple[str, str]]:
    """
    Parse DOCX 格式：'Name HH:MM text'。首句可能无时间戳 'Name text'。
    返回 (speaker, text) 列表。
    """
    pat = re.compile(r"\s+([A-Za-z][A-Za-z\s\-]+?)\s+(\d{1,2}:\d{2}(?::\d{2})?)\s+")
    matches = list(pat.finditer(content))
    turns = []

    if matches:
        first_seg = content[: matches[0].start()].strip()
        parts = first_seg.split(None, 2)
        if len(parts) >= 3 and not parts[0].isdigit() and not parts[1].isdigit():
            name = _normalize_speaker(f"{parts[0]} {parts[1]}")
            text = parts[2]
            if name and text and len(name) > 2:
                turns.append((name, text))

    for i, m in enumerate(matches):
        speaker = _normalize_speaker(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        text = content[start:end].strip()
        if speaker and len(speaker) > 2 and text:
            turns.append((speaker, text))

    return turns


def _is_advisor_docx(speaker: str, student_names: Set[str]) -> bool:
    """DOCX 中：若 speaker 在 student_names 中则为学生，否则为顾问。"""
    if not student_names:
        return True
    s = speaker.strip().lower()
    for n in student_names:
        if n.lower() in s or s in n.lower():
            return False
    return True


def _is_student_docx(speaker: str, student_names: Set[str]) -> bool:
    return not _is_advisor_docx(speaker, student_names)


def main():
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_pairs = []
    for f in sorted(TRANSCRIPTS_DIR.glob("TRANSCRIPT_*.txt")):
        raw = f.read_bytes()
        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            content = raw.decode("utf-16", errors="replace")
        else:
            content = raw.decode("utf-8", errors="replace")
        turns = parse_webvtt(content)
        pairs = extract_pairs(turns)
        all_pairs.extend(pairs)
        print(f"  {f.name}: {len(pairs)} pairs")

    for f in sorted(TRANSCRIPTS_DIR.glob("*.docx")):
        if f.name.startswith("~$"):
            continue
        try:
            content = _extract_text_from_docx(f)
            student_names = _student_names_from_filename(f.name)
            turns = parse_docx(content, student_names)
            if not student_names and turns:
                student_names = _infer_student_from_id_file(turns)
            is_adv = lambda s, sn=student_names: _is_advisor_docx(s, sn)
            is_stu = lambda s, sn=student_names: _is_student_docx(s, sn)
            pairs = extract_pairs(turns, is_advisor=is_adv, is_student=is_stu)
            all_pairs.extend(pairs)
            print(f"  {f.name}: {len(pairs)} pairs")
        except Exception as e:
            print(f"  {f.name}: skip ({e})")

    out = [{"advisor": p["advisor"], "student": p["student"], "intent": p["intent"], "persona": p["persona"], "source": p["source"]} for p in all_pairs]
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(all_pairs)} pairs to {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    main()
