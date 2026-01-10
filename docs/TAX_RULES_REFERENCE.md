# Tax Rules Reference

**Version:** 1.0  
**Date:** January 10, 2026  

This document serves as a reference for the tax rules implemented in the AI Tax Engine. It includes federal tax brackets, deductions, credits, filing statuses, business rules, depreciation, and audit considerations. It is intended for developers, auditors, and compliance reviewers.

---

## 1. Federal Income Tax Brackets (2026)

| Filing Status       | 10%       | 12%       | 22%       | 24%       | 32%       | 35%       | 37%       |
|--------------------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| Single             | $0-$11,000| $11,001-$44,725 | $44,726-$95,375 | $95,376-$182,100 | $182,101-$231,250 | $231,251-$578,125 | $578,126+ |
| Married Filing Joint | $0-$22,000 | $22,001-$89,450 | $89,451-$190,750 | $190,751-$364,200 | $364,201-$462,500 | $462,501-$693,750 | $693,751+ |
| Head of Household   | $0-$15,700| $15,701-$59,850 | $59,851-$95,350 | $95,351-$182,100 | $182,101-$231,250 | $231,251-$578,100 | $578,101+ |
| Married Filing Separate | $0-$11,000 | $11,001-$44,725 | $44,726-$95,375 | $95,376-$182,100 | $182,101-$231,250 | $231,251-$346,875 | $346,876+ |

> These brackets are used in `tax_engine/brackets.py`.

---

## 2. Standard Deductions

| Filing Status       | Standard Deduction 2026 |
|--------------------|------------------------|
| Single             | $13,850                |
| Married Filing Joint | $27,700               |
| Head of Household   | $20,800                |
| Married Filing Separate | $13,850            |

> Managed in `tax_engine/deductions.py`.

---

## 3. Common Tax Credits

| Credit                      | Description                                           | Max Value |
|-------------------------------|---------------------------------------------------|-----------|
| Child Tax Credit             | Credit per qualifying child under 17              | $2,000   |
| Earned Income Tax Credit (EITC) | Based on income and family size                    | Varies   |
| American Opportunity Credit  | Education-related expenses, first 4 years of college | $2,500  |
| Lifetime Learning Credit     | Education-related expenses, unlimited years       | $2,000   |
| Retirement Savings Contributions Credit | For eligible retirement contributions       | $1,000   |

> Implemented in `tax_engine/credits.py`.

---

## 4. Filing Status Rules

- **Single**: Unmarried or legally separated  
- **Married Filing Jointly**: Married at year-end and filing jointly  
- **Married Filing Separately**: Married at year-end but filing separately  
- **Head of Household**: Unmarried, pays more than 50% of household expenses, and has qualifying dependents  

> Logic in `tax_engine/filing_status.py`.

---

## 5. Business Rules

- **Business Income**: Schedule C or partnerships  
- **Business Expenses**: Deductible only if ordinary and necessary  
- **Loss Limitations**: Passive activity loss limits apply  
- **Self-Employment Tax**: Calculated on net earnings  

> Found in `tax_engine/business_rules.py`.

---

## 6. Depreciation Rules

- **Asset Classes**: 3-year, 5-year, 7-year, 10-year, 20-year property  
- **Methods**: MACRS (Modified Accelerated Cost Recovery System)  
- **Special Rules**: Section 179 expense deduction  
- **Bonus Depreciation**: Applied if eligible  

> Managed in `tax_engine/depreciation.py`.

---

## 7. Audit & Compliance Rules

- **High-Risk Items**:
  - Large charitable contributions relative to income  
  - Home office deductions exceeding limits  
  - Business meals or entertainment over 50% of cost  
- **Safety Checks**: Verify proper documentation, cross-reference W-2/1099  
- **Escalation**: Cases flagged for human review are sent via `safety/escalation.py`

---

## 8. Notes

- Rules are based on **U.S. federal tax law** and are updated annually  
- State-level taxes are **not included** in this reference  
- All calculations are **CPA-level but AI-assisted**, flagged for human review when uncertain  

---

**End of Document**
