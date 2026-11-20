// ==========================================================================
// DigiSahay Prototype - Sample Data (js/data.js)
// Contains configurations, document checklists, Ahmedabad centers, and slots.
// ==========================================================================

const DIGI_DATA = {
  // Biometric and Passport Exclusion Warning (Shown across all pages)
  BIOMETRIC_NOTE: "This website does not support biometric updates (fingerprints, iris scan, Aadhaar photo). These must be done in person at an Aadhaar Seva Kendra. Passport services are also not covered.",

  // Six Supported Government Documents
  DOCUMENTS: {
    aadhaar: {
      id: "aadhaar", title: "Aadhaar Card", badge: "Demographic Only", icon: "🆔",
      authority: "UIDAI (Unique Identification Authority of India)",
      desc: "12-digit individual demographic identity card.", centerType: "Aadhaar Seva Kendra"
    },
    pan: {
      id: "pan", title: "PAN Card", badge: "Income Tax", icon: "💳",
      authority: "Income Tax Department (Protean / UTIITSL)",
      desc: "10-digit alphanumeric permanent account number.", centerType: "PAN Center"
    },
    voter: {
      id: "voter", title: "Voter ID (EPIC)", badge: "Election Commission", icon: "🗳️",
      authority: "Election Commission of India (ECI)",
      desc: "Form 6 electoral enrollment for citizens aged 18-19.", centerType: "Election Office"
    },
    dl: {
      id: "dl", title: "Driving Licence", badge: "Transport Dept", icon: "🚗",
      authority: "RTO Gujarat / MoRTH Parivahan",
      desc: "Learner & Permanent driver licence for 18+ applicants.", centerType: "RTO Office"
    },
    caste: {
      id: "caste", title: "Caste Certificate", badge: "Revenue Dept", icon: "📜",
      authority: "Taluka Mamlatdar / Social Justice Dept",
      desc: "Official category certificate (SC / ST / SEBC / EWS).", centerType: "Mamlatdar Office"
    },
    income: {
      id: "income", title: "Income Certificate", badge: "Civic Services", icon: "💰",
      authority: "Taluka Mamlatdar / Jan Seva Kendra",
      desc: "Income certificate for college scholarships & schemes.", centerType: "Mamlatdar Office"
    }
  },

  // Required Documents Matrix by Document and Flow Option
  REQUIRED_DOCS: {
    aadhaar: {
      new: [
        "Proof of Identity (POI): Birth Certificate or School Leaving Certificate",
        "Proof of Address (POA): Electricity Bill, Water Bill, or Parent's Ration Card",
        "Proof of Date of Birth: 10th Standard Board Marksheet"
      ],
      update: [
        "Existing 12-digit Aadhaar Number (stored as last 4 digits only)",
        "Proof of Name / DOB change (Gazette notification or 10th Marksheet)",
        "Proof of Address change (Recent utility bill < 3 months old)",
        "Note: Photo, iris and fingerprint updates are NOT supported here."
      ],
      missing: [
        "Aadhaar Number or Enrollment ID (EID) reference",
        "Police Complaint / Lost Document NCR Acknowledgment",
        "Self-declaration affidavit confirming original card loss",
        "Secondary photo identity proof (College ID / Marksheet)"
      ]
    },
    pan: {
      new: [
        "Aadhaar Card (used as proof of identity, address and date of birth)",
        "Two recent passport-size colour photographs",
        "Proof of Date of Birth (Class 10 Transfer / Passing Certificate)"
      ],
      update: [
        "Copy of Existing PAN Card (or PAN allotment letter)",
        "Aadhaar Card copy for verification",
        "Document supporting requested correction (e.g. Marriage cert or Gazette)"
      ],
      missing: [
        "Copy of lost PAN card or existing PAN Number",
        "Police Lost Document Intimation (NCR / Online FIR slip)",
        "Self-declaration affidavit for reprint of lost PAN",
        "Aadhaar card copy for identity verification"
      ]
    },
    voter: {
      new: [
        "Age Proof (18-19 Years): Class 10/12 Marksheet or Birth Certificate",
        "Ordinary Residence Proof: Ration Card, Bank Passbook, or Rent Agreement",
        "One passport-size photograph with white background (Form 6)"
      ],
      update: [
        "Existing Voter EPIC Number",
        "Proof of new address in Gujarat / change of constituency (Form 8)",
        "Aadhaar card for voluntary voter linking"
      ],
      missing: [
        "Existing EPIC number or voter roll reference details",
        "Copy of Police Missing Report / Self-declaration",
        "Address and Identity proof for replacement EPIC card"
      ]
    },
    dl: {
      new: [
        "Age Proof (Minimum 18 years): 10th Marksheet or School Leaving Certificate",
        "Present Address Proof: Electricity bill / Aadhaar card",
        "Self-Declaration of Physical Fitness (Form 1)",
        "Learner Licence test slot receipt"
      ],
      update: [
        "Original Driving Licence",
        "Proof of New Address in Gujarat",
        "Valid Medical Certificate (Form 1A if applicable)"
      ],
      missing: [
        "Driving Licence Number or Learner Licence Number",
        "Police Non-Cognizable Report (NCR) for lost licence",
        "Indemnity bond and lost licence application (LLD Form)"
      ]
    },
    caste: {
      new: [
        "School Leaving Certificate of Applicant and Father",
        "Proof of Residence in Gujarat prior to cutoff year (Ration card / Land records)",
        "Caste proof of blood relative (Paternal uncle / Father's certificate)",
        "Affidavit in prescribed format"
      ],
      update: [
        "Original or copy of previously issued Caste Certificate",
        "Legal proof of spelling correction or father's updated record"
      ],
      missing: [
        "Number and date of original certificate from Mamlatdar register",
        "Police missing entry slip / Affidavit on Rs. 50 stamp paper",
        "Identity proof and current residence proof"
      ]
    },
    income: {
      new: [
        "Talati Income Panchnama / Verification Report",
        "Salary Slips (3 months) or Form 16 / ITR of earning family members",
        "Ration Card copy showing all family members",
        "Recent electricity bill of family residence"
      ],
      update: [
        "Previous Income Certificate",
        "Updated income declaration for current financial year"
      ],
      missing: [
        "Registration number of original Income Certificate",
        "Self-declaration for issuance of duplicate copy",
        "Ration Card and Aadhaar verification"
      ]
    }
  },

  // Verified Facilitation Centers Around Ahmedabad
  CENTERS: [
    { id: "ask-nav", name: "Aadhaar Seva Kendra - Navrangpura", type: "Aadhaar Seva Kendra", lat: 23.0365, lng: 72.5611, address: "City Center, Swastik Cross Rd, Navrangpura", distance: "1.2 km", waitTime: "15 mins", handles: ["aadhaar", "CSC"] },
    { id: "ask-mani", name: "Aadhaar Seva Kendra - Maninagar", type: "Aadhaar Seva Kendra", lat: 22.9980, lng: 72.6020, address: "Near Railway Crossing, Rambaug, Maninagar", distance: "4.8 km", waitTime: "25 mins", handles: ["aadhaar", "CSC"] },
    { id: "pan-ashram", name: "Protean TIN-PAN Centre - Ashram Road", type: "PAN Center", lat: 23.0300, lng: 72.5700, address: "Sakr Complex, Opp. Old High Court, Ashram Road", distance: "2.1 km", waitTime: "10 mins", handles: ["pan", "CSC"] },
    { id: "pan-sat", name: "UTIITSL PAN Citizen Centre - Satellite", type: "PAN Center", lat: 23.0290, lng: 72.5180, address: "Shivalik Plaza, Near IIM Cross Road, Satellite", distance: "3.5 km", waitTime: "20 mins", handles: ["pan", "CSC"] },
    { id: "ero-ellis", name: "Electoral Registration Office (ERO) - Ellisbridge", type: "Election Office", lat: 23.0210, lng: 72.5650, address: "Deputy Collector Office, Ellisbridge", distance: "1.8 km", waitTime: "12 mins", handles: ["voter", "CSC"] },
    { id: "ero-subhash", name: "Collector Office Voter Suvidha Kendra", type: "Election Office", lat: 23.0610, lng: 72.5800, address: "Collector Office Compound, Near Subhash Bridge", distance: "3.9 km", waitTime: "18 mins", handles: ["voter", "CSC"] },
    { id: "rto-subhash", name: "RTO Ahmedabad - Subhash Bridge", type: "RTO Office", lat: 23.0640, lng: 72.5840, address: "Old RTO Office, Subhash Bridge, Sabarmati", distance: "4.2 km", waitTime: "30 mins", handles: ["dl"] },
    { id: "rto-vastral", name: "RTO East - Vastral", type: "RTO Office", lat: 22.9990, lng: 72.6590, address: "Near Vastral Metro Station, SP Ring Road", distance: "8.1 km", waitTime: "25 mins", handles: ["dl"] },
    { id: "mam-paldi", name: "Mamlatdar Office & Jan Seva Kendra - Paldi", type: "Mamlatdar Office", lat: 23.0130, lng: 72.5620, address: "Civic Centre, Mahalaxmi Cross Road, Paldi", distance: "2.4 km", waitTime: "20 mins", handles: ["caste", "income", "CSC"] },
    { id: "mam-sabarmati", name: "Mamlatdar Office - Sabarmati", type: "Mamlatdar Office", lat: 23.0780, lng: 72.5890, address: "Taluka Seva Sadan, Sabarmati, Ahmedabad", distance: "5.1 km", waitTime: "15 mins", handles: ["caste", "income", "CSC"] },
    { id: "csc-univ", name: "Digital India CSC Centre - University Area", type: "CSC", lat: 23.0380, lng: 72.5450, address: "Opposite Gujarat University, Navrangpura", distance: "1.5 km", waitTime: "8 mins", handles: ["aadhaar", "pan", "voter", "caste", "income", "CSC"] },
    { id: "csc-bopal", name: "CSC e-Governance Citizen Counter - Bopal", type: "CSC", lat: 23.0340, lng: 72.4680, address: "TRP Mall Road, South Bopal, Ahmedabad", distance: "6.7 km", waitTime: "10 mins", handles: ["aadhaar", "pan", "voter", "caste", "income", "CSC"] }
  ],

  // Appointment Slots
  TIME_SLOTS: [
    "09:30 AM - 10:00 AM",
    "10:00 AM - 10:30 AM",
    "11:00 AM - 11:30 AM",
    "02:00 PM - 02:30 PM",
    "03:30 PM - 04:00 PM",
    "04:30 PM - 05:00 PM"
  ],

  // Sample Profile for First-time 18-19 Year Old Citizen
  SAMPLE_PROFILE: {
    name: "Aarav K. Patel",
    dob: "2007-08-14",
    gender: "Male",
    phone: "9876543210",
    email: "aarav.patel@example.com",
    photoUrl: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'><rect width='120' height='120' fill='%23EEF2FF'/><circle cx='60' cy='48' r='24' fill='%23000080'/><path d='M25 105 C25 80, 95 80, 95 105 Z' fill='%23000080'/></svg>"
  }
};
