{
    'name': 'Cash Journal - Professional Cash Management',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Cash Management',
    'sequence': 0,
    'license': 'LGPL-3',
    'author': 'HILATECH',
    'website': 'https://hilatech.co',
    'icon': 'static/description/icon.png',
    'support': 'support@hilatech.co',
    'images': [
        'static/description/banner.gif',
    ],

    'summary': 'Complete cash flow management with monthly reconciliations and daily closures',

    'description': """
═══════════════════════════════════════════════════════════════════════════
CASH JOURNAL - PROFESSIONAL CASH FLOW MANAGEMENT FOR ODOO 19
═══════════════════════════════════════════════════════════════════════════

Complete and professional ERP solution for integrated cash flow management.
Designed to work seamlessly with Odoo, this module offers an intuitive daily
workflow, detailed reports, and robust financial traceability.

═══════════════════════════════════════════════════════════════════════════
✨ KEY FEATURES
═══════════════════════════════════════════════════════════════════════════

📊 MONTHLY REPORTS
   • Automatic sequential numbering
   • Smart initial balance (inherited from previous month)
   • Automatic final balance calculation
   • Protection against unauthorized modifications
   • Complete audit trail

📝 DAILY OPERATIONS
   • Simple inflow/outflow recording
   • Automatic description and beneficiary tracking
   • Signed amounts (positive = inflow, negative = outflow)
   • Automatic daily balance calculation
   • Real-time operation history

🔄 INTEGRATED WORKFLOW
   • "Open Cash Register" button to enable operation recording
   • Daily operation entry
   • "Close Daily Cash Register" button to lock operations
   • Automatic daily balance calculation
   • Easy next-day cash register opening

🔒 SECURITY & CONTROL
   • Two user roles: User (entry) and Manager (closing)
   • Granular permissions by model
   • Complete audit trail
   • Data protection and immutability

═══════════════════════════════════════════════════════════════════════════
📊 DATA MODELS
═══════════════════════════════════════════════════════════════════════════

MONTHLY REPORT (cash.journal.report)
• Sequential number (auto-generated)
• Month and year
• Opening balance (inherited)
• Closing balance (auto-calculated)
• Report state (Open/Closed)
• Daily cash state (Open/Closed)
• Operations list
• Manager and company assignment

OPERATION (cash.journal.operation)
• Operation date
• Description/Reason
• Received by (Partner/Employee)
• Signed amount: +inflow, -outflow
• Lock status (automatic after daily closure)

═══════════════════════════════════════════════════════════════════════════
🎯 USE CASES
═══════════════════════════════════════════════════════════════════════════

🏨 RESTAURANTS & HOTELS
   → Daily cash management and reconciliation
   → End-of-day cash reconciliation
   → Deposit tracking and management

🏪 RETAIL STORES
   → Centralized cash recording
   → Monetary flow control
   → Regular cash audits and compliance

💼 SERVICES & CONSULTING
   → Receipt and income management
   → Financial traceability
   → Accounting reports generation

🏢 SMEs & FRANCHISES
   → Multi-location cash management
   → Consolidated reporting
   → Centralized financial oversight

═══════════════════════════════════════════════════════════════════════════
💡 BENEFITS
═══════════════════════════════════════════════════════════════════════════

✓ Easy to use - Intuitive interface, minimal learning curve
✓ Reliable - Automatic verified calculations and data protection
✓ Compliant - Meets accounting and regulatory standards
✓ Scalable - Works for SMEs and large multi-site enterprises
✓ Integrated - Seamless integration with Odoo ecosystem
✓ Multilingual - Full support for French, English, and Spanish

═══════════════════════════════════════════════════════════════════════════
📞 SUPPORT
═══════════════════════════════════════════════════════════════════════════

For assistance and inquiries:
📧 Email: support@hilatech.co
🌐 Website: https://hilatech.co

Hilatech is a consulting firm specializing in high-level Odoo ERP
implementations and custom development with over 10 years of expertise.
    """,

    'depends': [
        'base',
        'account',
        'mail',
    ],

    'data': [
        'security/cash_journal_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/cash_journal_views.xml',
        'report_template.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
