export const MOCK_RESTAURANT_DATA = {
  stats: {
    revenue: "4,250 RON",
    orders: 24,
    occupancy: "85%", // Grad de ocupare mese
    lowStockItems: 3
  },
  urgent_actions: [
    { id: 1, title: "Autorizație ISU", desc: "Expiră în 10 zile. Legal Agent a pregătit documentele.", type: "critical" },
    { id: 2, title: "Stoc Mozzarella", desc: "Mai ai doar 2kg (necesar diseară: 5kg).", type: "warning" },
  ],
  ai_recommendations: [
    { id: 1, text: "Vremea se răcește diseară. Recomand activarea ofertei de 'Vin Fiert' în meniul digital." },
    { id: 2, text: "Ai 3 angajați noi. Vrei să generez contractele de muncă?" }
  ],
  finance: {
    monthly_revenue: [4500, 5200, 4800, 6100, 5900, 7200], // Date pentru grafic (ultimele 6 luni)
    current_balance: "12,450 RON",
    expenses_this_month: "8,200 RON",
    profit_margin: "34%",
    recent_transactions: [
      { id: 1, to: "Furnizor Metro", date: "Azi, 10:30", amount: "-1,200 RON", type: "expense", status: "completed" },
      { id: 2, to: "Încasări POS", date: "Ieri, 23:45", amount: "+4,850 RON", type: "income", status: "completed" },
      { id: 3, to: "Salarii Angajați", date: "20 Nov", amount: "-15,000 RON", type: "expense", status: "completed" },
      { id: 4, to: "Chirie Spațiu", date: "15 Nov", amount: "-1,000 EUR", type: "expense", status: "pending" },
      { id: 5, to: "Glovo Orders", date: "15 Nov", amount: "+890 RON", type: "income", status: "completed" },
    ]
  },
  legal: {
    status: "Înmatriculat",
    compliance_score: 85, // Din 100
    reg_number: "J40/1234/2024",
    checklist: [
      { id: 1, task: "Rezervare Nume Firmă", status: "completed", date: "10 Ian 2024" },
      { id: 2, task: "Redactare Act Constitutiv", status: "completed", date: "12 Ian 2024" },
      { id: 3, task: "Depunere Capital Social", status: "completed", date: "15 Ian 2024" },
      { id: 4, task: "Eliberare CUI (ONRC)", status: "completed", date: "20 Ian 2024" },
      { id: 5, task: "Înregistrare Scop TVA", status: "in_progress", agent_note: "Legal Agent a depus cererea 088." },
      { id: 6, task: "Autorizație Funcționare Primărie", status: "pending", urgent: true, agent_note: "Lipsește contract salubritate." }
    ],
    documents: [
      { id: 1, name: "Certificat Înmatriculare (CUI)", type: "PDF", size: "1.2 MB", status: "valid" },
      { id: 2, name: "Act Constitutiv", type: "PDF", size: "4.5 MB", status: "valid" },
      { id: 3, name: "Contract Închiriere Spațiu", type: "PDF", size: "2.1 MB", status: "expiring" }, // Expiră curând
      { id: 4, name: "Dovadă Sediu Social", type: "PDF", size: "0.8 MB", status: "valid" }
    ]
  },
  inventory: [
    { id: 1, name: "Făină Pizza 00", stock: 25, unit: "kg", status: "ok", expiry: "2024-06-20" },
    { id: 2, name: "Mozzarella", stock: 2, unit: "kg", status: "critical", expiry: "2023-11-25" },
    { id: 3, name: "Sos Roșii", stock: 10, unit: "l", status: "warning", expiry: "2023-12-01" },
    { id: 4, name: "Prosciutto Crudo", stock: 500, unit: "g", status: "ok", expiry: "2023-11-30" },
  ]
};