// ============================================================
// PACKCHECK AI — BIS CONTENT SCRIPT
// Official-record assistance only. No CAPTCHA/security bypass.
// ============================================================

let packData = null;
let extraction = null;
let completed = false;
let detailClicked = false;
let licenceTabClicked = false;
let licenceSearchDone = false;

function send(type, payload = {}) {
    return new Promise(resolve => {
        chrome.runtime.sendMessage({ type, ...payload }, response => resolve(response));
    });
}

function cleanText(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
}

function setNativeValue(input, value) {
    if (!input) return false;
    const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    if (descriptor?.set) descriptor.set.call(input, value);
    else input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    input.dispatchEvent(new Event("blur", { bubbles: true }));
    return true;
}

function visibleInputs() {
    return [...document.querySelectorAll("input")].filter(el => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && !el.disabled;
    });
}

function findSearchInput() {
    const inputs = visibleInputs();
    const preferred = inputs.find(input => {
        const text = cleanText([
            input.placeholder,
            input.name,
            input.id,
            input.getAttribute("aria-label"),
            input.getAttribute("formcontrolname")
        ].join(" ")).toLowerCase();
        return /standard|is number|search|keyword|code/.test(text);
    });
    return preferred || inputs.find(input => input.type === "text") || null;
}

function findButtonsByText(patterns) {
    const elements = [...document.querySelectorAll("button, a, [role='button'], input[type='button'], input[type='submit']")];
    return elements.filter(el => {
        const r = el.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) return false;
        const text = cleanText(el.innerText || el.value || el.getAttribute("aria-label") || "").toLowerCase();
        return patterns.some(pattern => pattern.test(text));
    });
}

function clickSearch() {
    const buttons = findButtonsByText([/^search$/, /search/]);
    if (buttons.length) {
        buttons[0].click();
        return true;
    }
    const input = findSearchInput();
    if (input?.form) {
        input.form.requestSubmit?.();
        return true;
    }
    return false;
}

function candidateElements(term) {
    const normalized = term.replace(/\s+/g, " ").trim().toLowerCase();
    const nodes = [...document.querySelectorAll("a, button, tr, td, li, [role='row'], [role='link']")];
    const candidates = [];

    for (const node of nodes) {
        const text = cleanText(node.innerText || node.textContent || "");
        if (!text || !text.toLowerCase().includes(normalized)) continue;
        const r = node.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) continue;
        const clickable = node.matches("a,button,[role='link']") ? node : node.querySelector("a,button,[role='link']");
        const target = clickable || node;
        if (!candidates.some(x => x === target)) candidates.push(target);
    }
    return candidates;
}

function showChoice(title, items, onChoose) {
    let box = document.getElementById("packcheck-bis-choice");
    if (box) box.remove();
    box = document.createElement("div");
    box.id = "packcheck-bis-choice";
    Object.assign(box.style, {
        position: "fixed", top: "20px", right: "20px", width: "390px", maxHeight: "80vh",
        overflow: "auto", background: "#fff", color: "#222", padding: "18px", borderRadius: "12px",
        boxShadow: "0 8px 30px rgba(0,0,0,.25)", zIndex: "2147483647", fontFamily: "Arial,sans-serif"
    });
    const heading = document.createElement("h3");
    heading.textContent = title;
    box.appendChild(heading);
    items.forEach((item, index) => {
        const button = document.createElement("button");
        button.textContent = `${index + 1}. ${cleanText(item.innerText || item.textContent).slice(0, 180)}`;
        Object.assign(button.style, { display: "block", width: "100%", margin: "8px 0", padding: "10px", textAlign: "left", cursor: "pointer" });
        button.onclick = () => { box.remove(); onChoose(item); };
        box.appendChild(button);
    });
    document.body.appendChild(box);
}

function tryOpenStandard() {
    if (detailClicked || !extraction?.is_number) return false;
    const candidates = candidateElements(extraction.is_number);
    if (candidates.length === 1) {
        detailClicked = true;
        candidates[0].click();
        return true;
    }
    if (candidates.length > 1) {
        showChoice("Select the correct BIS standard", candidates.slice(0, 10), item => {
            detailClicked = true;
            item.click();
        });
        return true;
    }
    return false;
}

function tryOpenLicenceTab() {
    if (licenceTabClicked) return false;
    const tabs = findButtonsByText([/licence/, /license/]);
    if (tabs.length) {
        const target = tabs.find(x => /licence|license/i.test(cleanText(x.innerText || x.textContent))) || tabs[0];
        target.click();
        licenceTabClicked = true;
        return true;
    }
    return false;
}

function findLicenceInput() {
    return visibleInputs().find(input => {
        const text = cleanText([
            input.placeholder, input.name, input.id, input.getAttribute("aria-label"), input.getAttribute("formcontrolname")
        ].join(" ")).toLowerCase();
        return /licence|license/.test(text);
    }) || null;
}

function trySearchLicence() {
    if (licenceSearchDone || !extraction?.bis_license_number) return false;
    const input = findLicenceInput();
    if (!input) return false;
    setNativeValue(input, extraction.bis_license_number);
    const buttons = findButtonsByText([/^search$/, /search/]);
    if (buttons.length) buttons[0].click();
    else if (input.form) input.form.requestSubmit?.();
    licenceSearchDone = true;
    return true;
}

function findLicenceCandidates() {
    if (!extraction?.bis_license_number) return [];
    return candidateElements(extraction.bis_license_number);
}

function compareOfficialPage() {
    const body = cleanText(document.body.innerText || "");
    const standard = String(extraction?.is_number || "").toLowerCase();
    const licence = String(extraction?.bis_license_number || "").toLowerCase();
    const manufacturer = String(extraction?.manufacturer || "").toLowerCase();
    const brand = String(extraction?.brand || "").toLowerCase();

    const standardMatch = !standard || body.toLowerCase().includes(standard);
    const licenceMatch = !licence || body.toLowerCase().includes(licence);
    const manufacturerMatch = !manufacturer || body.toLowerCase().includes(manufacturer);
    const brandMatch = !brand || body.toLowerCase().includes(brand);

    const availableChecks = [standardMatch, licenceMatch, manufacturerMatch, brandMatch];
    const matched = availableChecks.filter(Boolean).length;
    const expected = availableChecks.length;

    let overallStatus = "REVIEW";
    if (standardMatch && licenceMatch && manufacturerMatch && brandMatch) overallStatus = "VERIFIED";
    else if (matched === expected) overallStatus = "VERIFIED";

    return {
        type: "BIS",
        overallStatus,
        results: {
            isNumber: { status: standardMatch ? "MATCH" : "REVIEW", expected: standard, official: standardMatch ? standard : "Not found on current page" },
            licenceNo: { status: licenceMatch ? "MATCH" : "REVIEW", expected: licence, official: licenceMatch ? licence : "Not found on current page" },
            manufacturer: { status: manufacturerMatch ? "MATCH" : "REVIEW", expected: manufacturer, official: manufacturerMatch ? extraction.manufacturer : "Not matched" },
            brand: { status: brandMatch ? "MATCH" : "REVIEW", expected: brand, official: brandMatch ? extraction.brand : "Not matched" }
        },
        source: "Official BIS website",
        note: "PackCheck matched visible package evidence against the current official BIS page. Inspector review remains available."
    };
}

async function saveVerification() {
    if (completed) return;
    completed = true;
    const verification = compareOfficialPage();
    const officialData = {
        source: "https://standards.bis.gov.in/website/know-your-standards",
        pageTitle: document.title,
        pageText: cleanText(document.body.innerText || "").slice(0, 12000),
        isNumber: extraction?.is_number || null,
        bisLicenseNumber: extraction?.bis_license_number || null
    };

    const response = await send("SAVE_VERIFICATION_RESULT", {
        portal: "BIS",
        officialData,
        verification,
        ocrData: extraction
    });
    console.log("📄 PackCheck BIS verification sent:", response);
}

async function start() {
    const response = await send("GET_PACKCHECK_DATA");
    if (!response?.success) return;
    packData = response.data;
    extraction = packData?.extraction;
    if (!extraction?.is_number && !extraction?.bis_license_number) return;

    let attempts = 0;
    const timer = setInterval(async () => {
        attempts++;
        if (completed) { clearInterval(timer); return; }

        // Step 1: fill IS number and search on the BIS Know Your Standards page.
        if (!detailClicked && extraction.is_number) {
            const input = findSearchInput();
            if (input) {
                setNativeValue(input, extraction.is_number);
                clickSearch();
            }
            tryOpenStandard();
        }

        // Step 2: once the detail page is open, click Licence tab if available.
        if (detailClicked) {
            tryOpenLicenceTab();
            trySearchLicence();

            const licenceCandidates = findLicenceCandidates();
            if (licenceCandidates.length === 1 && extraction.bis_license_number) {
                licenceCandidates[0].click();
            } else if (licenceCandidates.length > 1 && extraction.bis_license_number) {
                showChoice("Select the correct BIS licence", licenceCandidates.slice(0, 10), item => item.click());
            }

            // Give the page time to render the licence table before comparing.
            if (attempts > 8) await saveVerification();
        }

        // If there is no IS number but a BIS licence number is visible, inspect the current page.
        if (!extraction.is_number && extraction.bis_license_number && attempts > 8) {
            await saveVerification();
        }

        if (attempts >= 60) clearInterval(timer);
    }, 1000);
}

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
else start();
