from pydantic import BaseModel

class CostConfig(BaseModel):
    # Assembly rates
    smt_cost_per_component: float = 0.35      # € per SMT component
    tht_cost_per_component: float = 0.65      # € per THT component

    # Hourly rates
    hourly_rate: float = 70.0                 # € per hour

    # Time estimates (hours)
    setup_hours: float = 3.0                  # machine setup + material prep
    qa_hours: float = 2.0                     # quality verification

    # Fixed / per-unit costs
    programming_cost_per_unit: float = 1.0    # firmware programming per SMT component
    order_processing_cost: float = 60.0       # flat order handling fee
    qa_documentation_cost: float = 0.0        # quality docs (optional)

    # Pricing
    margin_percent: float = 15.0              # profit margin %
    vat_percent: float = 19.0                 # VAT %

    # Company info
    company_name: str = "Acme Electronics GmbH"
    company_address: str = "Musterstraße 123, 12345 Berlin"
    company_email: str = "info@acme-electronics.de"
    company_website: str = "www.acme-electronics.de"
    company_phone: str = "+49 123 4567 8910"
    company_hrb: str = "HRB 123456"
    company_vat_id: str = "DE123456789"
    company_iban: str = "DE12 3456 7890 1234 5678 90"
    company_bank: str = "Musterbank"

    # Quote settings
    payment_terms: str = "Net 14 days from invoice date"
    validity_days: int = 30
    quote_number: str = "Q-2026-001"
