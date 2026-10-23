"""Import CSV / Google Sheets, dédoublonnage et classement conservateur."""
import csv, hashlib, io, json, os, unicodedata
from django.utils import timezone
from .models import Student, StudyLevel, Program, SyncLog

def norm(value):
    s = unicodedata.normalize("NFKD", str(value or "").strip().casefold())
    return "".join(c for c in s if not unicodedata.combining(c))

ALIASES = {
 "nom": ["nom", "nom de famille", "last name"],
 "prenom": ["prenom", "prenoms", "prenom(s)", "prénom(s)", "first name"],
 "commune": ["commune", "commune de residence", "lieu de residence", "residence"],
 "niveau": ["niveau", "niveau d'etudes", "licence", "annee d'etude", "classe"],
 "filiere": ["filiere", "parcours", "specialite"],
 "groupe": ["groupe", "classe ou groupe", "classe"],
 "car": ["souhaite prendre le car", "prendre le car", "transport", "car"],
 "date": ["horodatage", "timestamp", "date de soumission", "date d'inscription"],
 "telephone": ["telephone", "numero de telephone", "phone"],
}

def map_headers(headers):
    mapping = {}
    for idx, header in enumerate(headers):
        h = norm(header)
        for target, aliases in ALIASES.items():
            if (h in [norm(a) for a in aliases] or any(norm(a) in h for a in aliases if len(norm(a)) >= 7)) and target not in mapping:
                mapping[target] = idx
    return mapping

def normalize_row(row, mapping):
    return {key: (str(row[idx]).strip() if idx < len(row) and row[idx] is not None else "") for key, idx in mapping.items()}

def parse_choice(text):
    v = norm(text)
    if v in ("oui", "yes", "true", "1", "je souhaite", "oui je souhaite") or v.startswith("oui"):
        return Student.BusChoice.YES
    if v in ("non", "no", "false", "0") or v.startswith("non"):
        return Student.BusChoice.NO
    return Student.BusChoice.REVIEW

def classify(raw):
    lv = norm(raw.get("niveau")); prog = norm(raw.get("filiere"))
    level = None
    if lv in ("l1", "licence 1", "licence1", "premiere annee", "1", "premiere annee de licence") or "licence 1" in lv:
        level = StudyLevel.objects.filter(slug="licence-1").first()
    elif lv in ("l2", "licence 2", "licence2", "deuxieme annee", "2") or "licence 2" in lv:
        level = StudyLevel.objects.filter(slug="licence-2").first()
    program = Program.objects.filter(level=level, slug=prog.replace(" ", "-")).first() if level else None
    if not program and level:
        program = Program.objects.filter(level=level, name__iexact=raw.get("filiere", "").strip()).first()
    return level, program

def import_rows(headers, rows, source="csv"):
    mapping = map_headers(headers)
    log = SyncLog.objects.create(source=source)
    counts = {"created": 0, "updated": 0, "ignored": 0, "errors": 0}
    messages = []
    if "nom" not in mapping or "prenom" not in mapping:
        log.errors = 1
        log.details = "Colonnes requises introuvables : Nom et Prénom(s)."
        log.save()
        return log
    for line_no, row in enumerate(rows, start=2):
        try:
            raw = normalize_row(row, mapping)
            if not raw.get("nom") and not raw.get("prenom"):
                counts["ignored"] += 1
                continue
            level, program = classify(raw)
            identity = "|".join(norm(raw.get(k, "")) for k in ("nom", "prenom", "commune", "niveau", "filiere"))
            if not identity.strip("|"):
                counts["ignored"] += 1
                continue
            key = hashlib.sha256(identity.encode("utf-8")).hexdigest()
            student, created = Student.objects.get_or_create(source_key=key, defaults={"last_name": raw.get("nom", "")[:120], "first_names": raw.get("prenom", "")[:160]})
            if not created and student.local_override:
                counts["ignored"] += 1
                continue
            student.last_name = raw.get("nom", "")[:120]
            student.first_names = raw.get("prenom", "")[:160]
            student.commune = raw.get("commune", "")[:120]
            student.level = level
            student.program = program
            student.class_group = raw.get("groupe", "")[:120]
            student.bus_choice = parse_choice(raw.get("car", ""))
            student.phone = raw.get("telephone", "")[:40]
            student.source_row = line_no
            student.notes = "" if level and program else "Licence ou filière absente/inconnue; vérifier le classement."
            date_text = raw.get("date", "")
            if date_text:
                from datetime import datetime
                parsed = None
                for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        parsed = timezone.make_aware(datetime.strptime(date_text, fmt))
                        break
                    except ValueError:
                        pass
                student.submitted_at = parsed
            student.save()
            counts["created" if created else "updated"] += 1
        except Exception as exc:
            counts["errors"] += 1
            messages.append(f"Ligne {line_no}: {exc}")
    for key, value in counts.items():
        setattr(log, key, value)
    log.details = "\n".join(messages[:100])
    log.save()
    return log

def import_csv(upload):
    content = upload.read().decode("utf-8-sig", errors="replace")
    try:
        dialect = csv.Sniffer().sniff(content[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.reader(io.StringIO(content), dialect)
    headers = next(reader, [])
    return import_rows(headers, reader, "csv")

def import_google_sheet():
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "")
    credentials = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if not sheet_id or not (credentials_json or credentials):
        raise ValueError("Configurez GOOGLE_SHEET_ID et un identifiant de compte de service.")
    import gspread
    if credentials_json:
        from google.oauth2.service_account import Credentials
        info = json.loads(credentials_json)
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        gc = gspread.authorize(Credentials.from_service_account_info(info, scopes=scopes))
    else:
        gc = gspread.service_account(filename=credentials, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    ws = gc.open_by_key(sheet_id).worksheet(os.getenv("GOOGLE_WORKSHEET_NAME", "Form Responses 1"))
    values = ws.get_all_values()
    if not values:
        raise ValueError("La feuille ne contient aucune ligne.")
    return import_rows(values[0], values[1:], "google")
