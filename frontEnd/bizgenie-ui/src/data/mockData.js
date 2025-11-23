export const MOCK_RESTAURANT_DATA = {
  stats: {
    revenue: "4,250 RON",
    orders: 24,
    occupancy: "85%", 
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
  
  // --- INVENTAR (Format Nou) ---
  inventory: [
    { 
        id: 1, 
        product_name: "Făină Pizza 00", 
        category: "ingredient",
        quantity: 25, 
        unit: "kg", 
        min_threshold: 10,
        expiration_date: "2024-06-20",
        auto_buy: 1
    },
    { 
        id: 2, 
        product_name: "Mozzarella", 
        category: "refrigerated",
        quantity: 2, 
        unit: "kg", 
        min_threshold: 5,
        expiration_date: "2023-11-25",
        auto_buy: 0
    },
    { 
        id: 3, 
        product_name: "Sos Roșii", 
        category: "canned",
        quantity: 10, 
        unit: "l", 
        min_threshold: 8,
        expiration_date: "2023-12-01",
        auto_buy: 1
    }
  ],

  // --- FINANTE ---
  finance: {
    monthly_revenue: [4500, 5200, 4800, 6100, 5900, 7200],
    current_balance: "12,450 RON",
    expenses_this_month: "8,200 RON",
    profit_margin: "34%",
    recent_transactions: [
      { id: 1, to: "Furnizor Metro", date: "Azi, 10:30", amount: "-1,200 RON", type: "expense", status: "completed" },
      { id: 2, to: "Încasări POS", date: "Ieri, 23:45", amount: "+4,850 RON", type: "income", status: "completed" }
    ]
  },

  // --- LEGAL (Format Nou - Sincronizat cu Simulatorul) ---
  legal: {
    status: "Înmatriculat",
    compliance_score: 85,
    reg_number: "J40/1234/2024",
    
    checklist: [
      {
        id: 101,
        title: "Înregistrare ONRC",
        status: "completed",
        description: "Procesul obligatoriu de înregistrare a firmei la Registrul Comerțului.",
        steps: [
            { step: "Rezervare nume firmă", done: true },
            { step: "Depunere capital social", done: true },
            { step: "Depunere dosar complet", done: true },
            { step: "Ridicare certificat", done: true }
        ]
      },
      {
        id: 102,
        title: "Autorizație Funcționare Primărie",
        status: "in_progress",
        description: "Obținerea acordului de funcționare de la primăria de sector/locală.",
        steps: [
            { step: "Contract Salubritate", done: true },
            { step: "Schiță spațiu", done: true },
            { step: "Plată taxă timbru", done: false },
            { step: "Depunere cerere", done: false }
        ]
      },
      {
        id: 103,
        title: "Autorizație ISU (Incendiu)",
        status: "pending",
        description: "Documentația pentru securitatea la incendiu.",
        steps: [
            { step: "Plan releveu", done: false },
            { step: "Instalare hidranți", done: false },
            { step: "Verificare extinctoare", done: false }
        ]
      }
    ],
    
    documents: [
      { id: 1, name: "Certificat Înmatriculare (CUI)", type: "PDF", size: "1.2 MB", status: "valid" },
      { id: 2, name: "Act Constitutiv", type: "PDF", size: "4.5 MB", status: "valid" }
    ]
  }
};