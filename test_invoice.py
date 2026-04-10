from src.tools.finance.invoice_parser import process_invoice

data = process_invoice("data/invoices/Invoice_5.pdf")

print(data)
