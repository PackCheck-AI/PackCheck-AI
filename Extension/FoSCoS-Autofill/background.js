const API = "http://localhost:8000";
const PACKCHECK = "http://localhost:8501";
const FOSCOS_URL = "https://foscos.fssai.gov.in/";
const BIS_URL = "https://standards.bis.gov.in/website/know-your-standards";

let lastAnalysisKey = null;
let packCheckTabId = null;
let activeVerificationTabId = null;
let workflowQueue = [];
let currentWorkflow = null;

async function getData() {
    const response = await fetch(`${API}/packcheck_result.json?ts=${Date.now()}`);
    if (!response.ok) throw new Error(`PackCheck API returned HTTP ${response.status}`);
    return await response.json();
}

async function openPortal(workflow, data) {
    currentWorkflow = workflow;
    const url = workflow === "BIS" ? BIS_URL : FOSCOS_URL;
    const tab = await chrome.tabs.create({ url, active: true });
    activeVerificationTabId = tab.id;
    console.log(`🌐 PackCheck opened ${workflow}:`, tab.id);
    return tab;
}

async function startWorkflows(data) {
    const extraction = data.extraction || {};
    const workflows = Array.isArray(data.verification?.workflows)
        ? data.verification.workflows.filter(x => x === "BIS" || x === "FOSCOS")
        : [];

    if (!workflows.length) return;

    workflowQueue = workflows.slice();
    currentWorkflow = null;

    if (data.verification?.open_after) {
        const remaining = Number(data.verification.open_after) - Date.now() / 1000;
        if (remaining > 0) {
            setTimeout(() => openNextWorkflow(data), Math.ceil(remaining * 1000));
            return;
        }
    }

    await openNextWorkflow(data);
}

async function openNextWorkflow(data) {
    if (!workflowQueue.length) {
        currentWorkflow = null;
        returnToPackCheck();
    } else {
        const next = workflowQueue.shift();
        await openPortal(next, data);
    }
}

async function checkPackCheckResult() {
    try {
        const result = await getData();
        const analysisId = result.analysis_id || result.verification?.analysis_id || "";
        const key = `${analysisId}:${JSON.stringify(result.verification?.workflows || [])}`;

        if (!result.extraction || !result.verification || !analysisId) return;
        if (key === lastAnalysisKey) return;

        lastAnalysisKey = key;
        packCheckTabId = null;

        const packTabs = await chrome.tabs.query({ url: `${PACKCHECK}/*` });
        if (packTabs.length) packCheckTabId = packTabs[0].id;

        await startWorkflows(result);
    } catch (error) {
        console.error("❌ PackCheck verification router:", error);
    }
}

async function returnToPackCheck() {
    try {
        const tabs = await chrome.tabs.query({ url: `${PACKCHECK}/*` });
        const url = `${PACKCHECK}/?verification=complete&t=${Date.now()}`;
        if (tabs.length) {
            await chrome.tabs.update(tabs[0].id, { url, active: true });
        } else {
            await chrome.tabs.create({ url, active: true });
        }
    } catch (error) {
        console.error("❌ Could not return to PackCheck:", error);
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (!message) return;

    if (message.type === "GET_PACKCHECK_DATA") {
        getData()
            .then(data => sendResponse({ success: true, data }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true;
    }

    if (message.type === "SAVE_VERIFICATION_RESULT") {
        const verification = {
            ...(message.verification || {}),
            type: message.portal || message.verification?.type || currentWorkflow || "FOSCOS"
        };

        fetch(`${API}/save-verification`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                officialData: message.officialData || {},
                verification,
                ocrData: message.ocrData || {}
            })
        })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(async data => {
                sendResponse({ success: true, data });

                if (activeVerificationTabId) {
                    try { await chrome.tabs.remove(activeVerificationTabId); } catch (_) {}
                    activeVerificationTabId = null;
                }

                // If the same inspection needs both FoSCoS and BIS,
                // continue with the next official workflow.
                const packData = await getData().catch(() => null);
                if (packData && workflowQueue.length) {
                    await openNextWorkflow(packData);
                } else {
                    await returnToPackCheck();
                }
            })
            .catch(error => sendResponse({ success: false, error: String(error) }));

        return true;
    }
});

chrome.tabs.onRemoved.addListener(tabId => {
    if (tabId === activeVerificationTabId) activeVerificationTabId = null;
    if (tabId === packCheckTabId) packCheckTabId = null;
});

chrome.alarms.create("packcheck-monitor", { periodInMinutes: 0.05 });
chrome.alarms.onAlarm.addListener(alarm => {
    if (alarm.name === "packcheck-monitor") checkPackCheckResult();
});

chrome.runtime.onStartup.addListener(checkPackCheckResult);
chrome.runtime.onInstalled.addListener(checkPackCheckResult);
setInterval(checkPackCheckResult, 2000);
checkPackCheckResult();
