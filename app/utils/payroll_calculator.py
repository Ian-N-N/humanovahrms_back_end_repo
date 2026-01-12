from decimal import Decimal

def calculate_nssf(gross_salary):
    """
    Calculate NSSF based on Tier I and Tier II.
    Tier I: 6% of lower limit (7,000) = 420
    Tier II: 6% of upper limit (36,000 - 7,000) = 1,740
    Total max: 2,160
    """
    gross = Decimal(str(gross_salary))
    tier1_limit = Decimal('7000')
    tier2_limit = Decimal('36000')
    
    tier1 = min(gross, tier1_limit) * Decimal('0.06')
    tier2 = Decimal('0')
    if gross > tier1_limit:
        tier2 = (min(gross, tier2_limit) - tier1_limit) * Decimal('0.06')
    
    return tier1 + tier2

def calculate_shif(gross_salary):
    """
    Social Health Insurance Fund (SHIF): 2.75% of gross salary.
    """
    gross = Decimal(str(gross_salary))
    return gross * Decimal('0.0275')

def calculate_housing_levy(gross_salary):
    """
    Affordable Housing Levy: 1.5% of gross salary.
    """
    gross = Decimal(str(gross_salary))
    return gross * Decimal('0.015')

def calculate_paye(gross_salary, nssf_contribution):
    """
    Calculate PAYE based on Kenyan tax bands (2024).
    Taxable Pay = Gross Salary - NSSF
    Apply bands, then subtract personal relief (2,400) and SHIF relief (15% of SHIF).
    """
    gross = Decimal(str(gross_salary))
    taxable_pay = gross - nssf_contribution
    
    # Tax Bands (Monthly)
    bands = [
        (Decimal('24000'), Decimal('0.10')),
        (Decimal('8333'), Decimal('0.25')),
        (Decimal('467667'), Decimal('0.30')),
        (Decimal('300000'), Decimal('0.325')),
        (Decimal('Infinity'), Decimal('0.35'))
    ]
    
    tax = Decimal('0')
    remaining_pay = taxable_pay
    
    # Band 1: First 24,000 @ 10%
    amount = min(remaining_pay, Decimal('24000'))
    tax += amount * Decimal('0.10')
    remaining_pay -= amount
    
    if remaining_pay > 0:
        # Band 2: Next 8,333 @ 25%
        amount = min(remaining_pay, Decimal('8333'))
        tax += amount * Decimal('0.25')
        remaining_pay -= amount
        
    if remaining_pay > 0:
        # Band 3: Next 467,667 @ 30%
        amount = min(remaining_pay, Decimal('467667'))
        tax += amount * Decimal('0.30')
        remaining_pay -= amount
        
    if remaining_pay > 0:
        # Band 4: Next 300,000 @ 32.5%
        amount = min(remaining_pay, Decimal('300000'))
        tax += amount * Decimal('0.325')
        remaining_pay -= amount
        
    if remaining_pay > 0:
        # Band 5: Above 800,000 @ 35%
        tax += remaining_pay * Decimal('0.35')
        
    # Reliefs
    personal_relief = Decimal('2400')
    # Insurance relief (SHIF) is 15% of contribution
    shif_contribution = calculate_shif(gross_salary)
    insurance_relief = shif_contribution * Decimal('0.15')
    
    final_paye = max(Decimal('0'), tax - personal_relief - insurance_relief)
    return round(final_paye, 2)

def calculate_payroll_item(basic_salary):
    """
    Generates a full payroll breakdown for an employee.
    """
    gross = Decimal(str(basic_salary)) # Assuming no extra allowances for now
    nssf = calculate_nssf(gross)
    shif = calculate_shif(gross)
    housing_levy = calculate_housing_levy(gross)
    paye = calculate_paye(gross, nssf)
    
    net_pay = gross - nssf - shif - housing_levy - paye
    
    return {
        'gross_salary': gross,
        'nssf': nssf,
        'shif': shif,
        'housing_levy': housing_levy,
        'tax_paid': paye,
        'net_salary': round(net_pay, 2)
    }
