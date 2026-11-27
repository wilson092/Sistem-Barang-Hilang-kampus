(() => {
  const successPage = document.querySelector(".success-page");
  if (successPage) {
    try { localStorage.removeItem(successPage.dataset.draftKey); } catch (_) { /* penyimpanan lokal dapat dinonaktifkan browser */ }
    return;
  }

  const form = document.getElementById("report-form");
  if (!form) return;

  document.querySelector(".wizard-layout")?.classList.add("wizard-enhanced");
  const steps = [...form.querySelectorAll("[data-wizard-step]")];
  const progress = document.getElementById("wizard-progress");
  const progressFill = document.getElementById("wizard-progress-fill");
  const progressText = document.getElementById("wizard-progress-label");
  const stepName = document.getElementById("wizard-step-name");
  const stepNames = ["Apa yang hilang?", "Terakhir terlihat di mana, dan kapan?", "Ciri, cerita & foto", "Tinjau dan kirim"];
  const nextButton = document.getElementById("wizard-next");
  const backButton = document.getElementById("wizard-back");
  const submitButton = document.getElementById("wizard-submit");
  const draftKey = form.dataset.draftKey;
  const categorySelect = form.querySelector('[name="jenis"]');
  const nameInput = form.querySelector('[name="nama_barang"]');
  const locationInput = form.querySelector('[name="lokasi"]');
  const dateInput = form.querySelector('[name="tanggal_kehilangan"]');
  const traitsInput = form.querySelector('[name="ciri_ciri"]');
  const descriptionInput = form.querySelector('[name="deskripsi"]');
  const fileInput = form.querySelector('[name="foto"]');
  const categoryChoices = document.getElementById("category-choices");
  const locationChoices = document.getElementById("location-choices");
  const dateShortcuts = document.getElementById("date-shortcuts");
  const draftBanner = document.getElementById("draft-banner");
  const sessionBanner = document.getElementById("session-banner");
  const uploadZone = document.getElementById("upload-zone");
  const uploadPreview = document.getElementById("upload-preview");
  const uploadThumbnail = document.getElementById("upload-thumbnail");
  const uploadFilename = document.getElementById("upload-filename");
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let currentStep = 0;
  let draftTimer;
  let activeObjectUrl = null;
  let previewedFile = null;
  let submitting = false;
  let transitionToken = 0;

  form.classList.add("wizard-enabled");
  progress.hidden = false;
  document.getElementById("wizard-controls").hidden = false;
  document.getElementById("live-preview").hidden = false;
  dateInput.max = form.dataset.today;
  fileInput.accept = "image/*";

  const icons = {
    electronic: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="3" width="10" height="18" rx="2"/><path d="M10 6h4M11 18h2"/></svg>',
    document: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M6 16c1.5-2 4.5-2 6 0M14 10h3M14 14h3"/></svg>',
    accessory: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h16l-1 12H5L4 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
    clothing: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 4 4 2 4-2 5 4-3 4-2-1v9H8v-9l-2 1-3-4 5-4Z"/></svg>',
    other: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 9 5v8l-9 5-9-5V8l9-5Z"/><path d="m3 8 9 5 9-5M12 13v8"/></svg>'
  };
  const categoryIcon = (value, label) => {
    const word = `${value} ${label}`.toLowerCase();
    if (word.includes("elektronik")) return icons.electronic;
    if (word.includes("dokumen") || word.includes("identitas")) return icons.document;
    if (word.includes("pakaian")) return icons.clothing;
    if (word.includes("aksesori") || word.includes("aksesoris")) return icons.accessory;
    return icons.other;
  };

  const makeButton = (label, className, value) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.textContent = label;
    if (value !== undefined) button.dataset.value = value;
    button.setAttribute("aria-pressed", "false");
    return button;
  };

  function renderCategories() {
    categoryChoices.replaceChildren();
    [...categorySelect.options].filter(option => option.value).forEach(option => {
      const button = makeButton("", "category-chip", option.value);
      button.innerHTML = `${categoryIcon(option.value, option.text)}<span>${option.text}</span><span class="chip-check" aria-hidden="true">✓</span>`;
      button.setAttribute("aria-label", option.text);
      button.addEventListener("click", () => {
        categorySelect.value = option.value;
        categorySelect.dispatchEvent(new Event("change", { bubbles: true }));
        nameInput.focus({ preventScroll: true });
        refreshReview();
      });
      categoryChoices.append(button);
    });
    syncCategoryChips();
  }

  function syncCategoryChips() {
    categoryChoices.querySelectorAll(".category-chip").forEach(button => {
      const selected = button.dataset.value === categorySelect.value;
      button.classList.toggle("is-selected", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
  }

  const locationNames = ["Perpustakaan", "Kantin", "Gedung A", "Parkiran", "Masjid"];
  function renderLocations() {
    locationChoices.replaceChildren();
    [...locationNames, "Lainnya"].forEach(location => {
      const button = makeButton(location, "location-chip", location);
      button.addEventListener("click", () => {
        if (location === "Lainnya") {
          locationInput.value = "";
          locationInput.dispatchEvent(new Event("input", { bubbles: true }));
          locationInput.focus();
          locationInput.select();
          return;
        }
        locationInput.value = location;
        locationInput.dispatchEvent(new Event("input", { bubbles: true }));
        locationInput.focus({ preventScroll: true });
      });
      locationChoices.append(button);
    });
    syncLocationChips();
  }

  function syncLocationChips() {
    locationChoices.querySelectorAll(".location-chip").forEach(button => {
      const selected = button.dataset.value.toLowerCase() === locationInput.value.trim().toLowerCase();
      button.classList.toggle("is-selected", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
  }

  const parseLocalDate = iso => {
    const [year, month, day] = iso.split("-").map(Number);
    return new Date(year, month - 1, day);
  };
  const formatDate = iso => iso ? parseLocalDate(iso).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" }) : "";
  function localISODate(date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
  }
  function renderDateShortcuts() {
    dateShortcuts.replaceChildren();
    const today = parseLocalDate(form.dataset.today);
    const choices = [
      { label: "Hari ini", date: today },
      { label: "Kemarin", date: new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1) },
      { label: "Beberapa hari lalu", date: new Date(today.getFullYear(), today.getMonth(), today.getDate() - 3), detail: "3 hari lalu" }
    ];
    choices.forEach(choice => {
      const iso = localISODate(choice.date);
      const button = makeButton("", "date-chip", iso);
      const title = document.createElement("span");
      title.textContent = choice.label;
      button.append(title);
      if (choice.detail) {
        const detail = document.createElement("small");
        detail.textContent = `${choice.detail} · ${choice.date.toLocaleDateString("id-ID", { day: "numeric", month: "short" })}`;
        button.append(detail);
      }
      button.addEventListener("click", () => {
        dateInput.value = iso;
        dateInput.dispatchEvent(new Event("input", { bubbles: true }));
        dateInput.dispatchEvent(new Event("change", { bubbles: true }));
      });
      dateShortcuts.append(button);
    });
    const chooseDate = makeButton("Pilih tanggal", "date-chip date-chip-picker", "picker");
    chooseDate.addEventListener("click", () => {
      if (typeof dateInput.showPicker === "function") dateInput.showPicker();
      else dateInput.focus();
    });
    dateShortcuts.append(chooseDate);
    syncDateChips();
  }

  function syncDateChips() {
    dateShortcuts.querySelectorAll(".date-chip").forEach(button => {
      const selected = button.dataset.value !== "picker" && button.dataset.value === dateInput.value;
      button.classList.toggle("is-selected", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
  }

  function readableDate(iso) { return iso ? formatDate(iso) : "Belum diisi"; }
  function setPreviewImage(file) {
    if (file === previewedFile) return;
    const targets = [document.getElementById("preview-image"), document.getElementById("review-image")];
    if (activeObjectUrl) URL.revokeObjectURL(activeObjectUrl);
    activeObjectUrl = file ? URL.createObjectURL(file) : null;
    previewedFile = file || null;
    targets.forEach(target => {
      target.replaceChildren();
      if (file && activeObjectUrl) {
        const image = document.createElement("img");
        image.src = activeObjectUrl;
        image.alt = "Pratinjau foto barang";
        target.append(image);
      } else if (target.id === "preview-image") {
        target.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 7h14v13H5zM9 7l1-2h4l1 2"/><circle cx="12" cy="13" r="3"/></svg>';
      } else {
        target.textContent = "UE";
      }
    });
  }

  function refreshReview() {
    const selectedOption = categorySelect.options[categorySelect.selectedIndex];
    const type = selectedOption && selectedOption.value ? selectedOption.text : "Pilih jenis barang";
    const name = nameInput.value.trim() || "Belum diisi";
    const location = locationInput.value.trim() || "Belum diisi";
    const traits = traitsInput.value.trim() || "Belum diisi";
    const description = descriptionInput.value.trim() || "Belum diisi";
    document.getElementById("preview-type").textContent = type;
    document.getElementById("preview-name").textContent = name;
    document.getElementById("preview-location").textContent = location;
    document.getElementById("preview-date").textContent = readableDate(dateInput.value);
    document.getElementById("preview-traits").textContent = traits;
    document.getElementById("review-name").textContent = name;
    document.getElementById("review-type").textContent = type;
    document.getElementById("review-location").textContent = location;
    document.getElementById("review-date").textContent = readableDate(dateInput.value);
    document.getElementById("review-traits").textContent = traits;
    document.getElementById("review-description").textContent = description;
    syncCategoryChips();
    syncLocationChips();
    syncDateChips();
    const file = fileInput.files && fileInput.files[0];
    if (file) {
      uploadPreview.hidden = false;
      uploadFilename.textContent = file.name;
      setPreviewImage(file);
      uploadThumbnail.src = activeObjectUrl;
    } else {
      uploadPreview.hidden = true;
      uploadThumbnail.removeAttribute("src");
      setPreviewImage(null);
    }
  }

  function errorNode(key) { return form.querySelector(`[data-error-for="${key}"]`); }
  function setFieldError(key, message) {
    const error = errorNode(key);
    if (error) error.textContent = message || "";
    const field = form.querySelector(`[data-field="${key}"]`);
    if (field) field.classList.toggle("has-error", Boolean(message));
    const control = key === "jenis" ? categorySelect : form.querySelector(`[name="${key}"]`);
    if (control) {
      if (message) {
        control.setAttribute("aria-invalid", "true");
        control.setAttribute("aria-describedby", `error-${key}`);
      } else {
        control.removeAttribute("aria-invalid");
        control.removeAttribute("aria-describedby");
      }
    }
  }

  const messages = {
    jenis: "Pilih jenis barang.",
    nama_barang: "Tulis nama barangnya.",
    lokasi: "Pilih atau tulis lokasi kehilangan.",
    tanggal_kehilangan: "Pilih tanggal kehilangan.",
    ciri_ciri: "Tambahkan setidaknya satu ciri khas barang.",
    deskripsi: "Ceritakan singkat bagaimana Anda menyadari barang hilang."
  };

  function validateField(key) {
    const control = key === "jenis" ? categorySelect : form.querySelector(`[name="${key}"]`);
    if (!control) return true;
    let message = "";
    if (key === "jenis" && !control.value) message = messages.jenis;
    else if (key !== "foto" && control.required && !control.value.trim()) message = messages[key] || "Kolom ini perlu diisi.";
    else if (key === "tanggal_kehilangan" && control.value > form.dataset.today) message = "Tanggal kehilangan tidak boleh di masa depan.";
    setFieldError(key, message);
    return !message;
  }

  function validateActiveStep(index = currentStep) {
    const keys = index === 0 ? ["jenis", "nama_barang"]
      : index === 1 ? ["lokasi", "tanggal_kehilangan"]
        : index === 2 ? ["ciri_ciri", "deskripsi", "foto"] : [];
    const valid = keys.map(validateField).every(Boolean);
    if (!valid) {
      const invalidKey = keys.find(key => errorNode(key)?.textContent.trim());
      if (invalidKey === "jenis") categoryChoices.querySelector("button")?.focus();
      else form.querySelector(`[name="${invalidKey}"]`)?.focus();
    }
    return valid;
  }

  function updateProgress() {
    progress.setAttribute("aria-valuenow", String(currentStep + 1));
    progressFill.style.transform = `scaleX(${(currentStep + 1) / steps.length})`;
    progressText.textContent = `Langkah ${currentStep + 1} dari ${steps.length}`;
    stepName.textContent = stepNames[currentStep];
    progress.querySelectorAll("[data-step-indicator]").forEach(indicator => {
      const index = Number(indicator.dataset.stepIndicator);
      if (index === currentStep) indicator.setAttribute("aria-current", "step");
      else indicator.removeAttribute("aria-current");
      indicator.classList.toggle("is-complete", index < currentStep);
    });
    backButton.disabled = currentStep === 0;
    nextButton.hidden = currentStep === steps.length - 1;
    submitButton.hidden = currentStep !== steps.length - 1;
    if (currentStep === steps.length - 1) refreshReview();
  }

  function focusStep(index) {
    if (index === 0 && !categorySelect.value) categoryChoices.querySelector("button")?.focus({ preventScroll: true });
    else if (index === 0) nameInput.focus({ preventScroll: true });
    else if (index === 1) locationInput.focus({ preventScroll: true });
    else if (index === 2) traitsInput.focus({ preventScroll: true });
    else document.querySelector('[data-edit-step="0"]')?.focus({ preventScroll: true });
    steps[index].scrollIntoView({ behavior: "auto", block: "start" });
  }

  function goToStep(index, shouldFocus = true) {
    if (index < 0 || index >= steps.length || index === currentStep) return;
    const token = ++transitionToken;
    const oldStep = steps[currentStep];
    const newStep = steps[index];
    const backwards = index < currentStep;
    oldStep.classList.add("is-leaving", backwards ? "leave-back" : "leave-forward");
    const delay = prefersReducedMotion.matches ? 0 : 220;
    window.setTimeout(() => {
      if (token !== transitionToken) return;
      oldStep.classList.remove("is-active", "is-leaving", "leave-back", "leave-forward");
      newStep.classList.add("is-active", "is-entering", backwards ? "enter-back" : "enter-forward");
      currentStep = index;
      updateProgress();
      requestAnimationFrame(() => newStep.classList.remove("is-entering", "enter-back", "enter-forward"));
      if (shouldFocus) focusStep(index);
      queueDraftSave();
    }, delay);
  }

  function draftSnapshot() {
    const privateText = /(?:password|kata\s+sandi|pin\b|pola(?:\s+(?:hp|ponsel|layar))?|nomor\s+kartu|no\.?\s*kartu|nomor\s+identitas|\bnik\b)/i;
    const longNumber = /\d(?:[\s-]*\d){7,}/;
    const safeText = value => privateText.test(value) || longNumber.test(value) ? "" : value;
    return {
      nama_barang: safeText(nameInput.value),
      jenis: categorySelect.value,
      lokasi: safeText(locationInput.value),
      tanggal_kehilangan: dateInput.value,
      ciri_ciri: safeText(traitsInput.value),
      deskripsi: safeText(descriptionInput.value),
      step: currentStep,
      savedAt: Date.now()
    };
  }

  function draftHasContent(draft) {
    return Boolean(draft && [draft.nama_barang, draft.jenis, draft.lokasi, draft.tanggal_kehilangan, draft.ciri_ciri, draft.deskripsi].some(Boolean));
  }

  function persistDraft() {
    const draft = draftSnapshot();
    try {
      if (draftHasContent(draft)) localStorage.setItem(draftKey, JSON.stringify(draft));
    } catch (_) { /* form tetap dapat dipakai jika penyimpanan lokal tidak tersedia */ }
  }

  function queueDraftSave() {
    window.clearTimeout(draftTimer);
    draftTimer = window.setTimeout(persistDraft, 500);
  }

  function readDraft() {
    try {
      const stored = localStorage.getItem(draftKey);
      return stored ? JSON.parse(stored) : null;
    } catch (_) { return null; }
  }

  function applyDraft(draft) {
    nameInput.value = draft.nama_barang || "";
    categorySelect.value = draft.jenis || "";
    locationInput.value = draft.lokasi || "";
    dateInput.value = draft.tanggal_kehilangan || "";
    descriptionInput.value = draft.deskripsi || "";
    if (draft.ciri_ciri) traitsInput.value = draft.ciri_ciri;
    currentStep = 0;
    steps.forEach((step, index) => step.classList.toggle("is-active", index === 0));
    updateProgress();
    refreshReview();
    queueDraftSave();
  }

  function syncPhotoPreview() {
    const file = fileInput.files && fileInput.files[0];
    const error = file ? validatePhoto(file) : "";
    setFieldError("foto", error);
    if (error && file) {
      clearSelectedFile();
      refreshReview();
      return;
    }
    refreshReview();
    queueDraftSave();
  }

  function validatePhoto(file) {
    const validTypes = ["image/jpeg", "image/png", "image/webp"];
    const validExtensions = /\.(jpe?g|png|webp)$/i;
    if (file.size > 5 * 1024 * 1024) return "Ukuran foto maksimal 5 MB. Pilih foto yang lebih kecil.";
    if (!validTypes.includes(file.type) || !validExtensions.test(file.name)) return "Pilih foto JPG, PNG, atau WebP.";
    return "";
  }

  function clearSelectedFile() {
    try { fileInput.files = new DataTransfer().files; }
    catch (_) { fileInput.value = ""; }
    fileInput.removeAttribute("capture");
    uploadPreview.hidden = true;
    uploadThumbnail.removeAttribute("src");
    if (activeObjectUrl) URL.revokeObjectURL(activeObjectUrl);
    activeObjectUrl = null;
  }

  renderCategories();
  renderLocations();
  renderDateShortcuts();
  steps[0].classList.add("is-active");
  updateProgress();
  refreshReview();
  ["jenis", "nama_barang", "lokasi", "tanggal_kehilangan", "ciri_ciri", "deskripsi", "foto"].forEach(key => {
    const existingError = errorNode(key)?.textContent.trim();
    if (existingError) setFieldError(key, existingError);
  });

  categorySelect.addEventListener("change", () => {
    syncCategoryChips();
    setFieldError("jenis", "");
    refreshReview();
    queueDraftSave();
  });

  [[nameInput, "nama_barang"], [locationInput, "lokasi"], [dateInput, "tanggal_kehilangan"], [traitsInput, "ciri_ciri"], [descriptionInput, "deskripsi"]].forEach(([input, key]) => {
    input.addEventListener("input", () => {
      setFieldError(key, "");
      refreshReview();
      queueDraftSave();
      if (key === "lokasi") syncLocationChips();
    });
    input.addEventListener("blur", () => {
      if (steps[currentStep].contains(input)) validateField(key);
    });
  });

  fileInput.addEventListener("change", syncPhotoPreview);
  document.querySelectorAll("[data-camera]").forEach(button => button.addEventListener("click", () => {
    fileInput.setAttribute("capture", "environment");
    fileInput.click();
  }));
  document.querySelectorAll("[data-gallery]").forEach(button => button.addEventListener("click", () => {
    fileInput.removeAttribute("capture");
    fileInput.click();
  }));
  document.getElementById("remove-photo").addEventListener("click", () => {
    clearSelectedFile();
    setFieldError("foto", "");
    refreshReview();
  });
  uploadZone.addEventListener("keydown", event => {
    if (event.target === uploadZone && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      fileInput.removeAttribute("capture");
      fileInput.click();
    }
  });
  ["dragenter", "dragover"].forEach(eventName => uploadZone.addEventListener(eventName, event => {
    event.preventDefault();
    uploadZone.classList.add("is-dragging");
  }));
  ["dragleave", "drop"].forEach(eventName => uploadZone.addEventListener(eventName, event => {
    event.preventDefault();
    uploadZone.classList.remove("is-dragging");
  }));
  uploadZone.addEventListener("drop", event => {
    const file = event.dataTransfer.files[0];
    if (!file) return;
    const transfer = new DataTransfer();
    transfer.items.add(file);
    fileInput.files = transfer.files;
    fileInput.dispatchEvent(new Event("change", { bubbles: true }));
  });

  nextButton.addEventListener("click", () => {
    if (!validateActiveStep()) return;
    refreshReview();
    goToStep(currentStep + 1);
  });
  backButton.addEventListener("click", () => goToStep(currentStep - 1));
  document.querySelectorAll("[data-edit-step]").forEach(button => button.addEventListener("click", () => {
    const target = Number(button.dataset.editStep);
    goToStep(target);
  }));
  form.addEventListener("keydown", event => {
    if (event.key === "Enter" && event.target.matches("input:not([type='file']):not([type='date'])")) {
      event.preventDefault();
      nextButton.click();
    }
  });

  const existingDraft = readDraft();
  if (draftHasContent(existingDraft) && form.dataset.serverErrors !== "true") {
    draftBanner.hidden = false;
    document.getElementById("draft-continue").addEventListener("click", () => {
      applyDraft(existingDraft);
      draftBanner.hidden = true;
      const target = Math.min(Number(existingDraft.step) || 0, steps.length - 1);
      if (target === currentStep) focusStep(target);
      else goToStep(target);
    });
    document.getElementById("draft-discard").addEventListener("click", () => {
      try { localStorage.removeItem(draftKey); } catch (_) { /* abaikan */ }
      draftBanner.hidden = true;
    });
  }

  if (form.dataset.serverErrors === "true") {
    const errorOrder = ["jenis", "nama_barang", "lokasi", "tanggal_kehilangan", "ciri_ciri", "deskripsi", "foto"];
    const firstError = errorOrder.find(key => errorNode(key)?.textContent.trim());
    const stepFor = { jenis: 0, nama_barang: 0, lokasi: 1, tanggal_kehilangan: 1, ciri_ciri: 2, deskripsi: 2, foto: 2 };
    if (firstError) {
      currentStep = stepFor[firstError];
      steps.forEach((step, index) => step.classList.toggle("is-active", index === currentStep));
      updateProgress();
    }
  }

  form.addEventListener("submit", async event => {
    if (submitting) { event.preventDefault(); return; }
    event.preventDefault();
    for (let index = 0; index < steps.length - 1; index += 1) {
      if (!validateActiveStep(index)) {
        const wasCurrent = currentStep;
        currentStep = index;
        steps.forEach((step, stepIndex) => step.classList.toggle("is-active", stepIndex === index));
        updateProgress();
        if (wasCurrent !== index) focusStep(index);
        return;
      }
    }
    if (fileInput.files[0] && validatePhoto(fileInput.files[0])) {
      currentStep = 2;
      steps.forEach((step, index) => step.classList.toggle("is-active", index === 2));
      updateProgress();
      setFieldError("foto", validatePhoto(fileInput.files[0]));
      focusStep(2);
      return;
    }

    submitting = true;
    persistDraft();
    submitButton.disabled = true;
    submitButton.classList.add("is-loading");
    submitButton.querySelector(".submit-label").textContent = "Mengirim...";
    try {
      const response = await fetch(form.action || window.location.href, {
        method: "POST",
        body: new FormData(form),
        credentials: "same-origin",
        redirect: "follow",
        headers: { "X-Requested-With": "XMLHttpRequest" }
      });
      if (/\/login\//.test(response.url) || response.status === 403) {
        sessionBanner.hidden = false;
        sessionBanner.focus?.();
        submitting = false;
        submitButton.disabled = false;
        submitButton.classList.remove("is-loading");
        submitButton.querySelector(".submit-label").textContent = "Kirim laporan";
        return;
      }
      if (/\/mahasiswa\/laporan\/\d+\/berhasil\//.test(response.url)) {
        window.location.assign(response.url);
        return;
      }
      if (response.ok && response.url.includes("/mahasiswa/laporan/buat/")) {
        const html = await response.text();
        document.open();
        document.write(html);
        document.close();
        return;
      }
      throw new Error("Respons server tidak dapat dibaca.");
    } catch (_) {
      submitting = false;
      submitButton.disabled = false;
      submitButton.classList.remove("is-loading");
      submitButton.querySelector(".submit-label").textContent = "Coba kirim lagi";
      sessionBanner.hidden = false;
      sessionBanner.querySelector("strong").textContent = "Laporan belum terkirim.";
      sessionBanner.childNodes[1].textContent = " Draft tetap tersimpan. Periksa koneksi, lalu coba lagi.";
    }
  });
})();
