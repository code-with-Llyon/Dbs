const form = document.getElementById("uploadForm");
const feedback = document.getElementById("js-feedback");

const purposeEl = document.getElementById("purpose");
const categoryEl = document.getElementById("category");
const docTypeEl = document.getElementById("doc_type");
const requiredBox = document.getElementById("requiredDocsBox");

// ---------------------------
// Frontend doc labels (for UI list only)
// ---------------------------
const docLabels = {
  passport: "Passport biometric page",
  gnib_card: "Current IRP / GNIB card (front & back)",
  college_letter: "College/School enrolment letter",
  fees_proof: "Proof of fees paid",
  scholarship_proof: "Scholarship funding proof",
  course_start_proof: "Proof course started",
  insurance: "Private medical insurance",
  employment_letter: "Employer letter / contract",
  payslip: "Recent payslip",
  bank_statement: "Bank statement",
  address_proof: "Proof of address"
};

// ---------------------------
// PURPOSE -> CATEGORY -> doc types (must match app.py DOC_MAP)
// ---------------------------
const DOC_MAP = {
  study: {
    masters: ["passport","college_letter","fees_proof","scholarship_proof","course_start_proof","insurance"],
    undergraduate: ["passport","college_letter","fees_proof","scholarship_proof","insurance"],
    english_language: ["passport","college_letter","fees_proof","insurance"]
  },
  work: {
    employment_permit: ["passport","employment_letter","payslip","insurance"],
    graduate_1g: ["passport","college_letter","insurance"]
  }
};

const categoryOptions = {
  study: [
    ["masters", "Masters / Higher Education"],
    ["undergraduate", "Undergraduate / Higher Education"],
    ["english_language", "English Language Student"]
  ],
  work: [
    ["employment_permit", "Employment Permit Holder (Stamp 1)"],
    ["graduate_1g", "Graduate / Stamp 1G"]
  ]
};

// Reset doc type dropdown to only required docs
function updateDocTypes(purpose, category){
  docTypeEl.innerHTML = `<option value="">-- Select Document --</option>`;
  if(!purpose || !category) return;

  const docs = DOC_MAP[purpose][category] || [];
  docs.forEach(d => {
    const opt = document.createElement("option");
    opt.value = d;
    opt.textContent = docLabels[d] || d;
    docTypeEl.appendChild(opt);
  });
}

// Show required docs list box
function updateRequiredBox(purpose, category){
  requiredBox.classList.add("d-none");
  requiredBox.innerHTML = "";

  if(!purpose || !category) return;

  const docs = DOC_MAP[purpose][category] || [];
  requiredBox.innerHTML = `
    <strong>Required Documents for this category:</strong>
    <ul class="mb-0">
      ${docs.map(d => `<li>${docLabels[d] || d}</li>`).join("")}
    </ul>
  `;
  requiredBox.classList.remove("d-none");
}

// Populate categories when purpose changes
purposeEl.addEventListener("change", () => {
  const p = purposeEl.value;
  categoryEl.innerHTML = `<option value="">-- Select Category --</option>`;

  if(!p) return;

  categoryOptions[p].forEach(([val,label])=>{
    const opt = document.createElement("option");
    opt.value = val;
    opt.textContent = label;
    categoryEl.appendChild(opt);
  });

  updateRequiredBox(null,null);
  updateDocTypes(null,null);
});

// Update required docs & doc types when category changes
categoryEl.addEventListener("change", () => {
  const p = purposeEl.value;
  const c = categoryEl.value;
  updateRequiredBox(p,c);
  updateDocTypes(p,c);
});

// ---------------------------
// FORM SUBMIT VALIDATION
// ---------------------------
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  feedback.innerHTML = "";

  const purpose = purposeEl.value;
  const category = categoryEl.value;
  const docType = docTypeEl.value;
  const expiry = document.getElementById("expiry_date").value;
  const fileInput = document.getElementById("document");

  // Client-side checks
  if (!purpose) {
    feedback.innerHTML = `<div class="alert alert-danger">Select a purpose.</div>`;
    return;
  }
  if (!category) {
    feedback.innerHTML = `<div class="alert alert-danger">Select a category.</div>`;
    return;
  }
  if (!docType) {
    feedback.innerHTML = `<div class="alert alert-danger">Select a document type.</div>`;
    return;
  }
  if (!fileInput.files.length) {
    feedback.innerHTML = `<div class="alert alert-danger">Choose a file.</div>`;
    return;
  }

  const file = fileInput.files[0];
  const allowedExt = ["pdf","jpg","jpeg","png"];
  const ext = file.name.split(".").pop().toLowerCase();

  if (!allowedExt.includes(ext)) {
    feedback.innerHTML = `<div class="alert alert-danger">Only PDF/JPG/PNG allowed.</div>`;
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    feedback.innerHTML = `<div class="alert alert-danger">File must be under 5MB.</div>`;
    return;
  }

  // If passport / gnib card selected, expiry required (client side)
  if ((docType === "passport" || docType === "gnib_card") && !expiry) {
    feedback.innerHTML = `<div class="alert alert-danger">Expiry date required for Passport/GNIB.</div>`;
    return;
  }

  // Server-side pre-validation
  try {
    const res = await fetch("/api/validate", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        purpose,
        category,
        doc_type: docType,
        expiry_date: expiry
      })
    });

    const data = await res.json();

    if (!res.ok) {
      feedback.innerHTML = `<div class="alert alert-danger">${data.errors.join("<br>")}</div>`;
      return;
    }

    feedback.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
    setTimeout(() => form.submit(), 400);

  } catch (err) {
    console.error(err);
    feedback.innerHTML = `<div class="alert alert-danger">Server error. Try again.</div>`;
  }
});