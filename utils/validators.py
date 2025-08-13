# utils/validators.py
import re

_email = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_valid_email(s: str) -> bool:
    return bool(_email.match(s or ""))

def clean_rut(rut: str) -> str:
    return (rut or "").replace(".", "").replace("-", "").strip().upper()

def rut_dv(num: int) -> str:
    # algoritmo: multiplicar por 2..7 cíclico, sumar, 11 - (suma % 11)
    seq = [2,3,4,5,6,7]
    s, i = 0, 0
    while num > 0:
        s += (num % 10) * seq[i % 6]
        num //= 10
        i += 1
    r = 11 - (s % 11)
    if r == 11: return "0"
    if r == 10: return "K"
    return str(r)

def is_valid_rut(rut: str) -> bool:
    r = clean_rut(rut)
    if len(r) < 2: return False
    num, dv = r[:-1], r[-1]
    if not num.isdigit(): return False
    return rut_dv(int(num)) == dv
