const views = [...document.querySelectorAll(".view")];
const nav = [...document.querySelectorAll(".navlink")];

const bn = (number) =>
  new Intl.NumberFormat("bn-BD").format(number);

const safe = (value) =>
  String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;"
  })[character]);

const toast = document.getElementById("toast");

function notify(message) {
  toast.textContent = message;
  toast.classList.add("show");

  clearTimeout(window.toastTimer);

  window.toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 2800);
}

function showView(id) {
  views.forEach((view) => {
    view.classList.toggle("active", view.id === id);
  });

  nav.forEach((item) => {
    item.classList.toggle("active", item.dataset.view === id);
  });

  document.querySelector("nav").classList.remove("open");

  document
    .getElementById("menuBtn")
    .setAttribute("aria-expanded", "false");

  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });

  history.replaceState(null, "", `#${id}`);

  if (id === "dashboard") {
    loadDashboard();
  }

  if (id === "test" && !KishanAPI.token()) {
    openAuth();
  }
}

document
  .querySelectorAll("[data-view],[data-go]")
  .forEach((button) => {
    button.addEventListener("click", () => {
      showView(button.dataset.view || button.dataset.go);
    });
  });

const menu = document.getElementById("menuBtn");

menu.addEventListener("click", () => {
  const open = document.querySelector("nav").classList.toggle("open");
  menu.setAttribute("aria-expanded", open);
});

/* --------------------------------
   LOGIN AND REGISTRATION
-------------------------------- */

const authDialog = document.getElementById("authDialog");
const authForm = document.getElementById("authForm");
const authError = document.getElementById("authError");
const authBtn = document.getElementById("authBtn");
const profileBtn = document.getElementById("profileBtn");

let authMode = "login";

function setAuthMode(mode) {
  authMode = mode;
  authDialog.dataset.mode = mode;

  document.getElementById("authTitle").textContent =
    mode === "login"
      ? "লগইন করুন"
      : "নতুন অ্যাকাউন্ট খুলুন";

  document.querySelectorAll("[data-auth]").forEach((button) => {
    button.classList.toggle(
      "active",
      button.dataset.auth === mode
    );
  });

  authForm.elements.name.required = mode === "register";

  authForm.elements.password.autocomplete =
    mode === "register"
      ? "new-password"
      : "current-password";

  authError.textContent = "";
}

function openAuth(mode = "login") {
  setAuthMode(mode);
  authDialog.showModal();
}

authBtn.addEventListener("click", () => {
  openAuth();
});

document
  .getElementById("closeAuth")
  .addEventListener("click", () => {
    authDialog.close();
  });

document.querySelectorAll("[data-auth]").forEach((button) => {
  button.addEventListener("click", () => {
    setAuthMode(button.dataset.auth);
  });
});

profileBtn.addEventListener("click", () => {
  const shouldLogout = confirm(
    "অ্যাকাউন্ট থেকে লগআউট করবেন?"
  );

  if (shouldLogout) {
    KishanAPI.logout();
    updateAccountUI(null);
    notify("লগআউট হয়েছে");
    showView("home");
  }
});

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  authError.textContent = "";
  authForm.classList.add("loading");

  const form = new FormData(authForm);

  try {
    const payload = {
      email: form.get("email").trim(),
      password: form.get("password")
    };

    if (authMode === "register") {
      payload.name = form.get("name").trim();
      payload.phone = form.get("phone").trim() || null;

      await KishanAPI.register(payload);
    } else {
      await KishanAPI.login(payload);
    }

    const user = await KishanAPI.me();

    updateAccountUI(user);
    authDialog.close();
    authForm.reset();

    notify(
      authMode === "register"
        ? "অ্যাকাউন্ট তৈরি হয়েছে"
        : "লগইন সফল হয়েছে"
    );

    if (location.hash === "#dashboard") {
      loadDashboard();
    }
  } catch (error) {
    authError.textContent = error.message;
  } finally {
    authForm.classList.remove("loading");
  }
});

function updateAccountUI(user) {
  authBtn.hidden = Boolean(user);
  profileBtn.hidden = !user;

  if (user) {
    profileBtn.textContent = user.name.trim().slice(0, 1);

    profileBtn.title =
      `${user.name} — লগআউট করতে চাপুন`;

    document.getElementById("dash-title").textContent =
      `স্বাগতম, ${user.name}`;

    document.getElementById("accountStatus").textContent =
      "সক্রিয়";
  } else {
    document.getElementById("dash-title").textContent =
      "আপনার জমির খাতা";

    document.getElementById("accountStatus").textContent =
      "লগইন করুন";
  }
}

/* --------------------------------
   SIX-STEP SOIL TEST
-------------------------------- */

const soilForm = document.getElementById("soilForm");
const stepContent = document.getElementById("stepContent");

const stepButtons = [
  ...document.querySelectorAll(".steps button")
];

const progress = document.querySelector(".progress span");
const stepLabel = document.querySelector(".step-label");
const nextBtn = document.getElementById("nextBtn");
const backBtn = document.getElementById("backBtn");

let step = 0;

let draft = {
  kit_version: "manual-v1"
};

function levelChoices(name) {
  const choices = [
    ["low", "কম"],
    ["medium", "মাঝারি"],
    ["high", "বেশি"],
    ["unknown", "জানি না"]
  ];

  return `
    <div class="choice-grid">
      ${choices.map(([value, label]) => `
        <label>
          <input
            type="radio"
            name="${name}"
            value="${value}"
            ${draft[name] === value ? "checked" : ""}
          >
          ${label}
        </label>
      `).join("")}
    </div>
  `;
}

function inputField(
  label,
  name,
  type = "text",
  extra = ""
) {
  return `
    <label>
      ${label}
      <input
        name="${name}"
        type="${type}"
        value="${safe(draft[name] ?? "")}"
        ${extra}
      >
    </label>
  `;
}

const steps = [
  () => `
    <h2>জমির পরিচয় দিন</h2>

    <p>
      এই তথ্য দিয়ে ফলটি আপনার নির্দিষ্ট জমির সঙ্গে
      সংরক্ষিত হবে।
    </p>

    <div class="form-grid">
      ${inputField(
        "জমির নাম",
        "field_name",
        "text",
        'required placeholder="যেমন: উত্তর পাশের জমি"'
      )}

      ${inputField(
        "জেলা",
        "district",
        "text",
        "required"
      )}

      ${inputField(
        "উপজেলা",
        "upazila",
        "text",
        "required"
      )}

      ${inputField(
        "জমির পরিমাণ (বিঘা)",
        "area_bigha",
        "number",
        'min="0.01" step="0.01"'
      )}

      ${inputField(
        "বর্তমান ফসল",
        "current_crop"
      )}

      ${inputField(
        "যে ফসল করতে চান",
        "target_crop"
      )}
    </div>
  `,

  () => `
    <h2>pH পরীক্ষার ফল লিখুন</h2>

    <p>
      কিটের চার্টে পাওয়া কাছাকাছি সংখ্যাটি দিন।
      না জানলে খালি রাখুন।
    </p>

    <div class="form-grid">
      <label class="full">
        pH মান (০–১৪)

        <input
          name="ph"
          type="number"
          min="0"
          max="14"
          step="0.1"
          value="${safe(draft.ph ?? "")}"
          placeholder="যেমন: ৬.৫"
        >
      </label>
    </div>

    <div class="tip">
      <span>i</span>

      <p>
        <strong>সঠিক আলো ব্যবহার করুন</strong>
        দিনের স্বাভাবিক আলোতে কিটের রঙ মিলিয়ে দেখুন।
      </p>
    </div>
  `,

  () => `
    <h2>পুষ্টির ফল বাছুন</h2>

    <p>
      কিটের N, P ও K পরীক্ষার সঙ্গে মিলিয়ে
      প্রতিটি ফল দিন।
    </p>

    <h3>নাইট্রোজেন (N)</h3>
    ${levelChoices("nitrogen")}

    <h3>ফসফরাস (P)</h3>
    ${levelChoices("phosphorus")}

    <h3>পটাশিয়াম (K)</h3>
    ${levelChoices("potassium")}
  `,

  () => `
    <h2>মাটির গঠন ও পানি নিষ্কাশন</h2>

    <p>
      হাতে পরীক্ষা করে সবচেয়ে কাছের ধরনটি
      বেছে নিন।
    </p>

    <div class="form-grid">
      <label>
        মাটির ধরন

        <select name="texture">
          <option value="unknown">জানি না</option>
          <option value="sand">বেলে</option>
          <option value="sandy_loam">বেলে দোআঁশ</option>
          <option value="loam">দোআঁশ</option>
          <option value="clay_loam">এঁটেল দোআঁশ</option>
          <option value="clay">এঁটেল</option>
        </select>
      </label>

      <label>
        পানি নিষ্কাশন

        <select name="drainage">
          <option value="unknown">জানি না</option>
          <option value="poor">ধীর/খারাপ</option>
          <option value="moderate">মাঝারি</option>
          <option value="good">ভালো</option>
        </select>
      </label>
    </div>
  `,

  () => `
    <h2>আর্দ্রতা লিখুন</h2>

    <p>
      ময়েশ্চার মিটার থাকলে শতাংশ দিন।
      না থাকলে খালি রাখুন।
    </p>

    <div class="form-grid">
      <label class="full">
        আর্দ্রতা (০–১০০%)

        <input
          name="moisture"
          type="number"
          min="0"
          max="100"
          step="0.1"
          value="${safe(draft.moisture ?? "")}"
          placeholder="যেমন: ৪০"
        >
      </label>
    </div>
  `,

  () => `
    <h2>জমা দেওয়ার আগে মিলিয়ে নিন</h2>

    <p>
      ভুল থাকলে আগের ধাপে ফিরে ঠিক করুন।
    </p>

    <div class="review-table">
      <span>জমি</span>
      <span>${safe(draft.field_name)}</span>

      <span>এলাকা</span>
      <span>
        ${safe(draft.upazila)},
        ${safe(draft.district)}
      </span>

      <span>pH</span>
      <span>${safe(draft.ph || "জানা নেই")}</span>

      <span>N / P / K</span>
      <span>
        ${safe(draft.nitrogen || "unknown")} /
        ${safe(draft.phosphorus || "unknown")} /
        ${safe(draft.potassium || "unknown")}
      </span>

      <span>লক্ষ্য ফসল</span>
      <span>
        ${safe(draft.target_crop || "উল্লেখ নেই")}
      </span>
    </div>

    <div class="tip">
      <span>!</span>

      <p>
        এটি প্রাথমিক স্ক্রিনিং। নির্দিষ্ট সার বা
        চুনের মাত্রার জন্য কৃষি কর্মকর্তা অথবা
        স্বীকৃত ল্যাবের পরামর্শ নিন।
      </p>
    </div>
  `
];

function renderStep() {
  stepContent.innerHTML = steps[step]();

  if (step === 3) {
    stepContent.querySelector(
      '[name="texture"]'
    ).value = draft.texture || "unknown";

    stepContent.querySelector(
      '[name="drainage"]'
    ).value = draft.drainage || "unknown";
  }

  stepButtons.forEach((button, index) => {
    button.classList.toggle(
      "current",
      index === step
    );

    button.classList.toggle(
      "done",
      index < step
    );

    button.querySelector("b").textContent =
      index < step ? "✓" : index + 1;
  });

  progress.style.width =
    `${((step + 1) / 6) * 100}%`;

  stepLabel.textContent =
    `ধাপ ${step + 1} / ৬`;

  backBtn.disabled = step === 0;

  nextBtn.textContent =
    step === 5
      ? "ফল তৈরি করুন"
      : "পরের ধাপ →";
}

function saveVisibleInputs() {
  const data = new FormData(soilForm);

  for (const [key, value] of data.entries()) {
    draft[key] = value;
  }
}

function validateStep() {
  if (step === 0) {
    const requiredFields = [
      "field_name",
      "district",
      "upazila"
    ];

    for (const name of requiredFields) {
      const input = soilForm.elements[name];

      if (!input.value.trim()) {
        input.reportValidity();
        return false;
      }
    }
  }

  return true;
}

async function submitSoilTest() {
  if (!KishanAPI.token()) {
    openAuth();
    return;
  }

  soilForm.classList.add("loading");
  nextBtn.textContent = "ফল তৈরি হচ্ছে…";

  try {
    const createdField = await KishanAPI.createField({
      name: draft.field_name.trim(),
      district: draft.district.trim(),
      upazila: draft.upazila.trim(),

      area_bigha: draft.area_bigha
        ? Number(draft.area_bigha)
        : null,

      current_crop:
        draft.current_crop?.trim() || null,

      latitude: null,
      longitude: null
    });

    const test = await KishanAPI.createTest({
      field_id: createdField.id,

      ph: draft.ph
        ? Number(draft.ph)
        : null,

      nitrogen:
        draft.nitrogen || "unknown",

      phosphorus:
        draft.phosphorus || "unknown",

      potassium:
        draft.potassium || "unknown",

      texture:
        draft.texture || "unknown",

      moisture: draft.moisture
        ? Number(draft.moisture)
        : null,

      drainage:
        draft.drainage || "unknown",

      target_crop:
        draft.target_crop?.trim() || null,

      kit_version: "manual-v1"
    });

    const analysis =
      await KishanAPI.analyze(test.id);

    showAnalysis(analysis);

    draft = {
      kit_version: "manual-v1"
    };

    step = 0;
    renderStep();

    notify("পরীক্ষা ও ফল সংরক্ষিত হয়েছে");
  } catch (error) {
    notify(error.message);
  } finally {
    soilForm.classList.remove
