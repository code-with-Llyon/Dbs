const form = document.getElementById("uploadForm");
const feedback = document.getElementById("js-feedback");

const purposeEl = document.getElementById("purpose");
const categoryEl = document.getElementById("category");
const requiredBox = document.getElementById("requiredDocsBox");
const docsContainer = document.getElementById("docsContainer");

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

// ---------------------------
// Helpers to update UI
// ---------------------------

// Show required docs list box
function updateRequiredBox(purpose, category){
  requiredBox.classList.add("d-none");
  requiredBox.innerHTML = "";

  if(!purpose || !category) return;

  const docs = DOC_MAP[purpose]?.[category] || [];
  requiredBox.innerHTML = `
    <strong>Required Documents for this category:</strong>
    <ul class="mb-0">
      ${docs.map(d => `<li>${docLabels[d] || d}</li>`).join("")}
    </ul>
  `;
  requiredBox.classList.remove("d-none");
}

// Render one file input (and optional expiry field) per required doc
function renderDocInputs(purpose, category) {
  docsContainer.innerHTML = "";

  if (!purpose || !category) return;

  const docs = DOC_MAP[purpose]?.[category] || [];

  docs.forEach(d => {
    const wrapper = document.createElement("div");
    wrapper.className = "mb-3";

    const labelText = docLabels[d] || d;

    let extraField = "";
    if (d === "passport" || d === "gnib_card") {
      extraField = `
        <div class="mt-2">
          <label class="form-label">Expiry Date (${labelText})</label>
          <input
            type="date"
            name="expiry_${d}"
            class="form-control"
            placeholder="YYYY-MM-DD"
          />
        </div>
      `;
    }

    wrapper.innerHTML = `
      <label class="form-label">${labelText}</label>
      <input
        type="file"
        name="document_${d}"
        class="form-control"
        accept=".pdf,.jpg,.jpeg,.png"
      />
      ${extraField}
    `;

    docsContainer.appendChild(wrapper);
  });
}

// Populate categories when purpose changes
purposeEl.addEventListener("change", () => {
  const p = purposeEl.value;
  categoryEl.innerHTML = `<option value="">-- Select Category --</option>`;

  if(!p) {
    docsContainer.innerHTML = "";
    updateRequiredBox(null,null);
    return;
  }

  categoryOptions[p].forEach(([val,label])=>{
    const opt = document.createElement("option");
    opt.value = val;
    opt.textContent = label;
    categoryEl.appendChild(opt);
  });

  docsContainer.innerHTML = "";
  updateRequiredBox(null,null);
});

// Update required docs & render file inputs when category changes
categoryEl.addEventListener("change", () => {
  const p = purposeEl.value;
  const c = categoryEl.value;
  updateRequiredBox(p,c);
  renderDocInputs(p,c);
});

// FORM SUBMIT VALIDATION 
form.addEventListener("submit", (e) => {
  feedback.innerHTML = "";

  const purpose = purposeEl.value;
  const category = categoryEl.value;

  if (!purpose) {
    e.preventDefault();
    feedback.innerHTML = `<div class="alert alert-danger">Select a purpose.</div>`;
    return;
  }
  if (!category) {
    e.preventDefault();
    feedback.innerHTML = `<div class="alert alert-danger">Select a category.</div>`;
    return;
  }

  const fileInputs = docsContainer.querySelectorAll('input[type="file"]');
  if (!fileInputs.length) {
    e.preventDefault();
    feedback.innerHTML = `<div class="alert alert-danger">No document fields available. Please select a valid purpose and category.</div>`;
    return;
  }

  const allowedExt = ["pdf","jpg","jpeg","png"];
  let hasFile = false;

  for (const input of fileInputs) {
    const file = input.files[0];
    if (!file) {
      continue;
    }
    hasFile = true;

    const ext = file.name.split(".").pop().toLowerCase();
    if (!allowedExt.includes(ext)) {
      e.preventDefault();
      feedback.innerHTML = `<div class="alert alert-danger">Only PDF/JPG/PNG allowed.</div>`;
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      e.preventDefault();
      feedback.innerHTML = `<div class="alert alert-danger">Each file must be under 5MB.</div>`;
      return;
    }
  }

  if (!hasFile) {
    e.preventDefault();
    feedback.innerHTML = `<div class="alert alert-danger">Please select at least one file to upload.</div>`;
    return;
  }

});

// handles for when the page loads 
document.addEventListener("DOMContentLoaded", () => {
  const p = purposeEl.value;
  if (!p) return;

  categoryEl.innerHTML = `<option value="">-- Select Category --</option>`;

  const cats = categoryOptions[p] || [];
  cats.forEach(([val, label]) => {
    const opt = document.createElement("option");
    opt.value = val;
    opt.textContent = label;
    categoryEl.appendChild(opt);
  });

  updateRequiredBox(p, null);
});
