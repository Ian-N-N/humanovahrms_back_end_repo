from decimal import Decimal


def calculate_nssf(gross_salary):
    gross = Decimal(str(gross_salary))
    tier1_limit = Decimal("7000")
    tier2_limit = Decimal("36000")
    tier1 = min(gross, tier1_limit) * Decimal("0.06")
    tier2 = Decimal("0")
    if gross > tier1_limit:
        tier2 = (min(gross, tier2_limit) - tier1_limit) * Decimal("0.06")
    return tier1 + tier2


def calculate_shif(gross_salary):
    return Decimal(str(gross_salary)) * Decimal("0.0275")


def calculate_housing_levy(gross_salary):
    return Decimal(str(gross_salary)) * Decimal("0.015")


def calculate_paye(gross_salary, nssf_contribution):
    gross = Decimal(str(gross_salary))
    taxable_pay = gross - nssf_contribution
    tax = Decimal("0")
    remaining_pay = taxable_pay

    for band_amount, rate in (
        (Decimal("24000"), Decimal("0.10")),
        (Decimal("8333"), Decimal("0.25")),
        (Decimal("467667"), Decimal("0.30")),
        (Decimal("300000"), Decimal("0.325")),
    ):
        if remaining_pay <= 0:
            break
        amount = min(remaining_pay, band_amount)
        tax += amount * rate
        remaining_pay -= amount

    if remaining_pay > 0:
        tax += remaining_pay * Decimal("0.35")

    personal_relief = Decimal("2400")
    insurance_relief = calculate_shif(gross_salary) * Decimal("0.15")
    return round(max(Decimal("0"), tax - personal_relief - insurance_relief), 2)


def calculate_payroll_item(basic_salary):
    gross = Decimal(str(basic_salary or 0))
    nssf = calculate_nssf(gross)
    shif = calculate_shif(gross)
    housing_levy = calculate_housing_levy(gross)
    paye = calculate_paye(gross, nssf)
    net_pay = gross - nssf - shif - housing_levy - paye
    return {
        "gross_salary": gross,
        "nssf": nssf,
        "shif": shif,
        "housing_levy": housing_levy,
        "tax_paid": paye,
        "net_salary": round(net_pay, 2),
    }
