import re
from decimal import Decimal

from django.conf import settings
from qrcodegen import *


class UPNQRException(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.key = kwargs.pop("key", None)
        super().__init__(msg, *args, **kwargs)

    def __str__(self):
        str_ = super().__str__()
        if self.key:
            str_ += f" (key={self.key})"
        return str_


def _to_bool(v, key=None):
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return bool(v)
    if isinstance(v, str):
        return v.strip().lower() in ("yes", "true", "on", "t", "1")
    raise UPNQRException(f"Cannot convert type '{type(v).__name__}' to 'bool'", key=key)


def _to_number(v, type_, key=None):
    if v is None:
        return type_()
    if isinstance(v, type_):
        return v
    if isinstance(v, (int, float)):
        return type_(v)
    if isinstance(v, str):
        try:
            return type_(v.strip())
        except ValueError as e:
            raise UPNQRException(
                f"Cannot convert string '{v.strip()}' to '{type_.__name__}'", key=key
            ) from e
    raise UPNQRException(
        f"Cannot convert type '{type(v).__name__}' to '{type_.__name__}'", key=key
    )


def _to_int(v, key=None):
    return _to_number(v, int, key=key)


def _to_float(v, key=None):
    return _to_number(v, float, key=key)


def _to_decimal(v, key=None):
    return _to_number(v, Decimal, key=key)


def _pop_kwarg(kwargs, expected_type, key, default=None):
    if key in kwargs:
        kwarg = kwargs.pop(key, default)
        if kwarg is not None:
            if expected_type == bool:
                return _to_bool(kwarg, key)
            if expected_type == int:
                return _to_int(kwarg, key)
            if expected_type == float:
                return _to_float(kwarg, key)
            if expected_type == Decimal:
                return _to_decimal(kwarg, key)
            if expected_type == str:
                return str(kwarg).strip()
            raise UPNQRException(
                f"Cannot convert type '{type(kwarg).__name__}' to '{expected_type.__name__}'",
                key=key,
            )

    if default is None:
        raise UPNQRException(f"Missing required kwarg '{key}'")

    if not isinstance(default, expected_type):
        raise UPNQRException(
            f"Default value '{default}' is not of type '{expected_type.__name__}'",
            key=key,
        )

    return default


def _encode_and_trim(string, max_length=None):
    string = re.sub(r"\s+", " ", string).strip()
    string = string.encode("iso-8859-2", errors="replace")
    if max_length is not None:
        string = string[:max_length]
    return string


def _encode_amount(amount):
    amount = str(int(amount * 100)).zfill(11)
    amount = amount.encode("iso-8859-2", errors="replace")
    if len(amount) > 11:
        raise UPNQRException(f"Amount '{amount}' is too long (max 11 digits)")
    return amount


def _encode_code(code):
    code = code.strip().upper()
    code = code.encode("iso-8859-2", errors="replace")
    if len(code) > 4:
        raise UPNQRException(f"Code '{code}' is too long (max 4 characters)")
    if not re.match(rb"^[A-Z]+$", code):
        raise UPNQRException(f"Code '{code}' contains invalid characters")
    return code


def _encode_date(date):
    date = date.strip()
    date = date.encode("iso-8859-2", errors="replace")
    if date != b"" and not re.match(rb"^\d{2}\.\d{2}\.\d{4}$", date):
        raise UPNQRException(f"Date '{date}' is not in the format 'DD.MM.YYYY'")
    return date


def _encode_iban(iban):
    iban = iban.replace(" ", "")
    iban = iban.encode("iso-8859-2", errors="replace")
    if len(iban) > 34:
        raise UPNQRException(f"IBAN '{iban}' is too long (max 34 characters)")
    if not re.match(rb"^[A-Z]{2}", iban):
        raise UPNQRException(f"IBAN '{iban}' must start with 2 letters")
    if not re.match(rb"^[A-Z0-9]+$", iban):
        raise UPNQRException(f"IBAN '{iban}' contains invalid characters")
    return iban


def _encode_reference(reference):
    reference = reference.replace(" ", "")
    reference = reference.encode("iso-8859-2", errors="replace")
    if len(reference) > 26:
        raise UPNQRException(f"Reference '{reference}' is too long (max 26 characters)")
    if not re.match(rb"^(SI|RF)", reference):
        raise UPNQRException(f"Reference '{reference}' must start with SI or RF")
    if reference.startswith(b"SI"):
        if not re.match(rb"^SI\d{2}", reference):
            raise UPNQRException(
                f"Reference '{reference}' must start with SI and 2 digits"
            )
        if not re.match(rb"^SI\d{2}[\d-]{0,22}$", reference):
            raise UPNQRException(
                f"Reference '{reference}' must contain only digits and dashes (-)"
            )
    if reference.startswith(b"RF"):
        if not re.match(rb"^RF\d{2}", reference):
            raise UPNQRException(
                f"Reference '{reference}' must start with RF and 2 digits"
            )
        if not re.match(rb"^RF\d{2}[\dA-Z]{0,21}$", reference):
            raise UPNQRException(
                f"Reference '{reference}' must contain only digits and uppercase letters (A-Z)"
            )
    return reference


def generate_upnqr_svg(**kwargs):
    include_xml_declaration = _pop_kwarg(kwargs, bool, "include_xml_declaration", False)

    """
    Zap. |                         | Največja |
    št.  | Ime polja               | dolžina  | Vsebina
    -----+-------------------------+----------+--------------------------------------------------------
      1. | Vodilni slog            |        5 | Konstanta »UPNQR«.
      2. | IBAN plačnika           |          | Prazno.
      3. | Polog                   |          | Prazno.
      4. | Dvig                    |          | Prazno.
      5. | Referenca plačnika      |          | Prazno.
      6. | Ime plačnika            |       33 | Obvezno (*). Brez vodilnih ali sledečih presledkov.
      7. | Ulica in št. plačnika   |       33 | Obvezno (*). Brez vodilnih ali sledečih presledkov.
      8. | Kraj plačnika           |       33 | Obvezno (*). Brez vodilnih ali sledečih presledkov.
      9. | Znesek                  |       11 | Obvezno (**). Enajst cifer.
     10. | Datum plačila           |          | Prazno.
     11. | Nujno                   |          | Prazno.
     12. | Koda namena             |        4 | Obvezno. Štiri velike črke (A-Z).
     13. | Namen plačila           |       42 | Obvezno. Brez vodilnih ali sledečih presledkov.
     14. | Rok plačila             |       10 | Poljubno. Format »DD.MM.LLLL« ali prazno.
     15. | IBAN prejemnika         |       34 | Obvezno. Brez formatiranja (brez vmesnih presledkov).
     16. | Referenca prejemnika    |       26 | Obvezno. (4+22) Model in sklic skupaj brez presledkov.
     17. | Ime prejemnika          |       33 | Obvezno. Brez vodilnih ali sledečih presledkov.
     18. | Ulica in št. prejemnika |       33 | Obvezno. Brez vodilnih ali sledečih presledkov.
     19. | Kraj prejemnika         |       33 | Obvezno. Brez vodilnih ali sledečih presledkov.
     20. | Kontrolna vsota         |        3 | Obvezno (***). Tri cifre.
         | Rezerva                 |          | Poljubno. Prazno ali presledki, brez ločila.

    (*) Če izpolnjujete nalog za humanitarne namene in plačnik ni znan, so polja lahko prazna.
    (**) Če izpolnjujete nalog za humanitarne namene in je znesek prazen, vpišete enajst ničel »00000000000«.
    (***) Kontrolna vsota = strlen(N1) + strlen(N2) + … + strlen(N19) + 19
    """

    name = _pop_kwarg(kwargs, str, "name", "")
    address1 = _pop_kwarg(kwargs, str, "address1", "")
    address2 = _pop_kwarg(kwargs, str, "address2", "")
    amount = _pop_kwarg(kwargs, Decimal, "amount", Decimal("0.00"))
    code = _pop_kwarg(kwargs, str, "code", "GDSV")
    purpose = _pop_kwarg(kwargs, str, "purpose", "")
    due_date = _pop_kwarg(kwargs, str, "due_date", "")
    iban = _pop_kwarg(kwargs, str, "iban", settings.IBAN)
    reference = _pop_kwarg(kwargs, str, "reference", "")
    to_name = _pop_kwarg(kwargs, str, "to_name", settings.TO_NAME)
    to_address1 = _pop_kwarg(kwargs, str, "to_address1", settings.TO_ADDRESS1)
    to_address2 = _pop_kwarg(kwargs, str, "to_address2", settings.TO_ADDRESS2)

    if kwargs:
        raise UPNQRException(f"Unknown kwargs: {kwargs}")

    qr_text_lines = [
        b"UPNQR",  # 1
        b"",  # 2
        b"",  # 3
        b"",  # 4
        b"",  # 5
        _encode_and_trim(name, 33),  # 6
        _encode_and_trim(address1, 33),  # 7
        _encode_and_trim(address2, 33),  # 8
        _encode_amount(amount),  # 9
        b"",  # 10
        b"",  # 11
        _encode_code(code),  # 12
        _encode_and_trim(purpose, 42),  # 13
        _encode_date(due_date),  # 14
        _encode_iban(iban),  # 15
        _encode_reference(reference),  # 16
        _encode_and_trim(to_name, 33),  # 17
        _encode_and_trim(to_address1, 33),  # 18
        _encode_and_trim(to_address2, 33),  # 19
    ]
    checksum = str(sum([len(line) for line in qr_text_lines]) + 19).zfill(3)  # 20
    checksum = checksum.encode("iso-8859-2", errors="replace")
    qr_text_lines.append(checksum)
    qr_text = b"\n".join(qr_text_lines) + b"\n"

    qr_segments = QrCode.encode_segments(
        segs=[QrSegment.make_eci(4), QrSegment.make_bytes(qr_text)],
        ecl=QrCode.Ecc.MEDIUM,
        minversion=15,
        maxversion=15,
        mask=2,
        boostecl=False,
    )
    qr_string = qr_segments.to_svg_str(2)

    if not include_xml_declaration:
        qr_string = "\n".join(qr_string.split("\n")[2:])

    return qr_string
