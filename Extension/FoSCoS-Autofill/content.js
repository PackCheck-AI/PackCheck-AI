// ============================================================
// PACKCHECK AI — FoSCoS CONTENT SCRIPT
// ============================================================

let ocrData = null;
let verificationCompleted = false;


// ============================================================
// 1. LOAD PACKCHECK / GEMINI DATA
// ============================================================

async function loadPackCheckData() {

    return new Promise(resolve => {

        chrome.runtime.sendMessage(
            {
                type: "GET_PACKCHECK_DATA"
            },
            response => {

                if (chrome.runtime.lastError) {

                    console.error(
                        "❌ PackCheck message error:",
                        chrome.runtime.lastError.message
                    );

                    resolve(false);
                    return;
                }

                if (!response || !response.success) {

                    console.error(
                        "❌ PackCheck: No Gemini data received."
                    );

                    resolve(false);
                    return;
                }

                const extraction =
                    response.data &&
                    response.data.extraction;

                if (!extraction) {

                    console.error(
                        "❌ PackCheck: Extraction data missing."
                    );

                    resolve(false);
                    return;
                }

                ocrData = {

                    licenseNo:
                        extraction.fssai_number || "",

                    companyName:
                        extraction.manufacturer || "",

                    address:
                        extraction.manufacturer_address || ""

                };

                console.log(
                    "🤖 Gemini data:",
                    ocrData
                );

                resolve(true);
            }
        );
    });
}


// ============================================================
// 2. SET ANGULAR INPUT VALUE
// ============================================================

function setInputValue(field, value) {

    if (!field) return;

    const setter =
        Object.getOwnPropertyDescriptor(
            HTMLInputElement.prototype,
            "value"
        ).set;

    setter.call(field, value);

    field.dispatchEvent(
        new Event("input", {
            bubbles: true
        })
    );

    field.dispatchEvent(
        new Event("change", {
            bubbles: true
        })
    );
}


// ============================================================
// 3. FIND FoSCoS SEARCH FIELDS
// ============================================================

function findFields() {

    const inputs =
        document.querySelectorAll("input");

    let companyField = null;
    let licenseField = null;

    inputs.forEach(input => {

        const placeholder =
            (input.placeholder || "")
                .trim()
                .toLowerCase();

        const formControl =
            (
                input.getAttribute(
                    "formcontrolname"
                ) || ""
            )
                .trim()
                .toLowerCase();


        // Company name
        if (
            placeholder === "company name" ||
            formControl === "companyname"
        ) {

            companyField = input;
        }


        // FSSAI license number
        if (
            placeholder ===
                "license/registration no." ||
            formControl === "licenseno"
        ) {

            licenseField = input;
        }

    });

    return {
        companyField,
        licenseField
    };
}


// ============================================================
// 4. FILL FoSCoS FSSAI NUMBER
// ============================================================

function fillFoSCoS() {

    const {
        licenseField
    } = findFields();

    if (!licenseField) {

        console.log(
            "⏳ PackCheck: FSSAI input not visible yet..."
        );

        return false;
    }

    if (
        !ocrData ||
        !ocrData.licenseNo
    ) {

        console.error(
            "❌ PackCheck: No FSSAI number available."
        );

        return false;
    }

    setInputValue(
        licenseField,
        ocrData.licenseNo
    );

    console.log(
        "✅ PackCheck: FSSAI number automatically filled:",
        ocrData.licenseNo
    );

    console.log(
        "📦 Package company:",
        ocrData.companyName
    );

    console.log(
        "📦 Package address:",
        ocrData.address
    );

    return true;
}


// ============================================================
// 5. NORMALIZE TEXT
// ============================================================

function normalize(text) {

    if (!text) return "";

    return String(text)
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[.,/()-]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}


// ============================================================
// 6. COMPARE LICENSE
// ============================================================

function compareLicense(
    packetValue,
    officialValue
) {

    const packet =
        String(packetValue || "")
            .replace(/\D/g, "");

    const official =
        String(officialValue || "")
            .replace(/\D/g, "");

    if (!packet || !official) {

        return {
            status: "UNKNOWN",
            packet: packetValue,
            official: officialValue
        };
    }

    if (packet === official) {

        return {
            status: "MATCH",
            packet: packetValue,
            official: officialValue
        };
    }

    return {
        status: "MISMATCH",
        packet: packetValue,
        official: officialValue
    };
}


// ============================================================
// 7. TOKENIZE
// ============================================================

function tokenize(text) {

    return normalize(text)
        .split(/\s+/)
        .filter(Boolean);
}


// ============================================================
// 8. COMPARE COMPANY NAME
// ============================================================

function compareField(
    packetValue,
    officialValue
) {

    if (!packetValue || !officialValue) {

        return {
            status: "UNKNOWN",
            packet: packetValue,
            official: officialValue,
            similarity: 0
        };
    }

    const packet =
        normalize(packetValue);

    const official =
        normalize(officialValue);

    if (packet === official) {

        return {
            status: "MATCH",
            packet: packetValue,
            official: officialValue,
            similarity: 100
        };
    }

    const packetTokens =
        new Set(tokenize(packet));

    const officialTokens =
        new Set(tokenize(official));

    if (
        packetTokens.size === 0 ||
        officialTokens.size === 0
    ) {

        return {
            status: "UNKNOWN",
            packet: packetValue,
            official: officialValue,
            similarity: 0
        };
    }

    let common = 0;

    for (const token of packetTokens) {

        if (officialTokens.has(token)) {
            common++;
        }
    }

    const similarity =
        Math.round(
            (
                common /
                Math.min(
                    packetTokens.size,
                    officialTokens.size
                )
            ) * 100
        );

    let status;

    if (similarity >= 80) {

        status = "MATCH";

    } else if (similarity >= 50) {

        status = "PARTIAL MATCH";

    } else {

        status = "MISMATCH";
    }

    return {
        status,
        packet: packetValue,
        official: officialValue,
        similarity
    };
}


// ============================================================
// 9. COMPARE ADDRESS
// ============================================================

function compareAddress(
    packetValue,
    officialValue
) {

    if (!packetValue || !officialValue) {

        return {
            status: "UNKNOWN",
            packet: packetValue,
            official: officialValue,
            similarity: 0
        };
    }

    const packet =
        normalize(packetValue);

    const official =
        normalize(officialValue);

    if (packet === official) {

        return {
            status: "MATCH",
            packet: packetValue,
            official: officialValue,
            similarity: 100
        };
    }

    const packetTokens =
        new Set(tokenize(packet));

    const officialTokens =
        new Set(tokenize(official));

    if (
        packetTokens.size === 0 ||
        officialTokens.size === 0
    ) {

        return {
            status: "UNKNOWN",
            packet: packetValue,
            official: officialValue,
            similarity: 0
        };
    }

    let common = 0;

    for (const token of packetTokens) {

        if (officialTokens.has(token)) {
            common++;
        }
    }

    const similarity =
        Math.round(
            (
                common /
                Math.min(
                    packetTokens.size,
                    officialTokens.size
                )
            ) * 100
        );

    let status;

    if (similarity >= 80) {

        status = "MATCH";

    } else if (similarity >= 50) {

        status = "PARTIAL MATCH";

    } else {

        status = "MISMATCH";
    }

    return {
        status,
        packet: packetValue,
        official: officialValue,
        similarity
    };
}


// ============================================================
// 10. VERIFY PRODUCT
// ============================================================

function verifyProduct(
    packetData,
    officialData
) {

    const results = {

        licenseNo:
            compareLicense(
                packetData.licenseNo,
                officialData.licenseNo
            ),

        companyName:
            compareField(
                packetData.companyName,
                officialData.companyName
            ),

        address:
            compareAddress(
                packetData.address,
                officialData.address
            )
    };

    const values =
        Object.values(results);

    const mismatches =
        values.filter(
            result =>
                result.status === "MISMATCH"
        );

    const unknown =
        values.filter(
            result =>
                result.status === "UNKNOWN"
        );

    const partialMatches =
        values.filter(
            result =>
                result.status === "PARTIAL MATCH"
        );

    let overallStatus;

    if (mismatches.length > 0) {

        overallStatus =
            "MISMATCH";

    } else if (
        unknown.length > 0 ||
        partialMatches.length > 0
    ) {

        overallStatus =
            "REQUIRES REVIEW";

    } else {

        overallStatus =
            "VERIFIED";
    }

    return {
        overallStatus,
        results
    };
}


// ============================================================
// 11. EXTRACT OFFICIAL FoSCoS RESULT
// ============================================================

function extractFSSAIResult() {

    console.log(
        "🔎 Looking for official FoSCoS result..."
    );

    if (
        !ocrData ||
        !ocrData.licenseNo
    ) {

        console.log(
            "⏳ OCR FSSAI number not available."
        );

        return null;
    }

    const targetLicense =
        String(ocrData.licenseNo)
            .replace(/\D/g, "");

    const tables =
        document.querySelectorAll("table");

    console.log(
        "📊 Tables on page:",
        tables.length
    );


    // --------------------------------------------------------
    // Search every table
    // --------------------------------------------------------

    for (let i = 0; i < tables.length; i++) {

        const table = tables[i];

        const tableText =
            table.innerText || "";

        const tableLicense =
            tableText.replace(/\D/g, "");

        // Ignore unrelated tables
        if (
            !tableLicense.includes(
                targetLicense
            )
        ) {

            continue;
        }

        console.log(
            "🎯 Possible FoSCoS result table:",
            i
        );


        const rows =
            table.querySelectorAll("tr");

        for (const row of rows) {

            const cells =
                row.querySelectorAll("td");

            if (cells.length < 4) {
                continue;
            }

            const values =
                Array.from(cells).map(
                    cell =>
                        cell.innerText
                            .replace(/\s+/g, " ")
                            .trim()
                );

            console.log(
                "📊 FoSCoS row:",
                values
            );


            // ------------------------------------------------
            // Find the cell containing the FSSAI number
            // ------------------------------------------------

            const licenseCellIndex =
                values.findIndex(
                    value =>
                        value
                            .replace(/\D/g, "")
                            .includes(targetLicense)
                );

            if (
                licenseCellIndex === -1
            ) {

                continue;
            }


            console.log(
                "🎯 FSSAI license found in result row."
            );


            // ------------------------------------------------
            // Actual FoSCoS result table:
            //
            // 0 = SNo
            // 1 = FBO/Company Name
            // 2 = Premises Address
            // 3 = License No.
            // 4 = License Type
            // 5 = Status
            // 6 = View Products
            // ------------------------------------------------

            let companyName = "";
            let address = "";
            let licenseNo = "";
            let licenseType = "";
            let status = "";


            if (values.length >= 6) {

                companyName =
                    values[1] || "";

                address =
                    values[2] || "";

                licenseNo =
                    values[3] || "";

                licenseType =
                    values[4] || "";

                status =
                    values[5] || "";
            }


            // ------------------------------------------------
            // Safety fallback
            // ------------------------------------------------

            if (!licenseNo) {

                licenseNo =
                    values[licenseCellIndex] || "";
            }


            if (!licenseNo) {
                continue;
            }


            const officialData = {

                companyName,

                address,

                licenseNo,

                licenseType,

                status,

                source:
                    "Official FoSCoS"
            };


            console.log(
                "✅ OFFICIAL FoSCoS DATA FOUND:",
                officialData
            );

            return officialData;
        }
    }


    console.log(
        "⏳ Official FoSCoS result not found yet."
    );

    return null;
}


// ============================================================
// 12. SHOW VERIFICATION BOX
// ============================================================

function showVerificationBox(
    verification
) {

    const oldBox =
        document.getElementById(
            "packcheck-verification-box"
        );

    if (oldBox) {
        oldBox.remove();
    }

    const box =
        document.createElement("div");

    box.id =
        "packcheck-verification-box";


    let statusIcon = "🟢";
    let statusText = "VERIFIED";


    if (
        verification.overallStatus ===
        "MISMATCH"
    ) {

        statusIcon = "🔴";
        statusText = "MISMATCH";

    } else if (
        verification.overallStatus ===
        "REQUIRES REVIEW"
    ) {

        statusIcon = "🟠";
        statusText =
            "REQUIRES REVIEW";
    }


    function resultHTML(
        title,
        result
    ) {

        let symbol =
            getStatusSymbol(
                result.status
            );

        return `

            <div style="
                margin-top:15px;
                padding-top:12px;
                border-top:1px solid #ddd;
            ">

                <div style="
                    font-weight:bold;
                    margin-bottom:6px;
                ">
                    ${title}
                </div>

                <div style="
                    font-weight:bold;
                    margin-bottom:8px;
                ">
                    ${symbol}
                    ${result.status}
                </div>

                <div style="
                    font-size:12px;
                    color:#555;
                    margin-bottom:4px;
                ">
                    <b>Package:</b>
                    ${result.packet || "Not available"}
                </div>

                <div style="
                    font-size:12px;
                    color:#555;
                ">
                    <b>Official:</b>
                    ${result.official || "Not available"}
                </div>

                ${
                    result.similarity !== undefined
                    ?
                    `
                    <div style="
                        font-size:12px;
                        margin-top:5px;
                    ">
                        Similarity:
                        ${result.similarity}%
                    </div>
                    `
                    :
                    ""
                }

            </div>
        `;
    }


    box.innerHTML = `

        <div style="
            font-size:20px;
            font-weight:bold;
            margin-bottom:10px;
        ">
            ${statusIcon}
            PACKCHECK
        </div>

        <div style="
            font-size:16px;
            font-weight:bold;
            margin-bottom:15px;
        ">
            FSSAI — ${statusText}
        </div>

        ${resultHTML(
            "FSSAI License",
            verification.results.licenseNo
        )}

        ${resultHTML(
            "Company Name",
            verification.results.companyName
        )}

        ${resultHTML(
            "Address",
            verification.results.address
        )}

        <div style="
            margin-top:18px;
            padding-top:12px;
            border-top:1px solid #ddd;
            font-size:11px;
            color:#777;
        ">
            Source: Official FoSCoS result<br>
            PackCheck provides preliminary verification
            assistance and does not replace official
            regulatory inspection.
        </div>
    `;


    Object.assign(
        box.style,
        {

            position: "fixed",

            top: "20px",

            right: "20px",

            width: "360px",

            maxHeight: "80vh",

            overflowY: "auto",

            padding: "20px",

            background: "white",

            borderRadius: "12px",

            boxShadow:
                "0 4px 20px rgba(0,0,0,0.25)",

            zIndex: "999999",

            fontFamily:
                "Arial, sans-serif",

            color: "#222"
        }
    );


    document.body.appendChild(box);


    console.log(
        "🖥️ PackCheck verification box displayed."
    );
}


// ============================================================
// 13. STATUS SYMBOL
// ============================================================

function getStatusSymbol(status) {

    if (status === "MATCH") {
        return "✓";
    }

    if (status === "MISMATCH") {
        return "✗";
    }

    if (status === "PARTIAL MATCH") {
        return "≈";
    }

    return "⚠";
}


// ============================================================
// 14. RUN VERIFICATION
// ============================================================

function runVerification() {

    console.log(
        "🔍 runVerification() called"
    );


    if (verificationCompleted) {

        console.log(
            "⏭️ PackCheck: Verification already completed."
        );

        return null;
    }


    const officialData =
        extractFSSAIResult();


    if (!officialData) {

        console.log(
            "⚠️ PackCheck: Official result unavailable."
        );

        return null;
    }


    // --------------------------------------------------------
    // Compare
    // --------------------------------------------------------

    const verification =
        verifyProduct(
            ocrData,
            officialData
        );


    verificationCompleted =
        true;


    console.log(
        "🔎 PACKCHECK VERIFICATION:",
        verification
    );


    console.table(
        verification.results
    );


    // --------------------------------------------------------
    // Display result
    // --------------------------------------------------------

    showVerificationBox(
        verification
    );


    // --------------------------------------------------------
    // Send result to local server
    // --------------------------------------------------------

    chrome.runtime.sendMessage({

        type:
            "SAVE_VERIFICATION_RESULT",

        officialData:
            officialData,

        verification:
            verification,

        ocrData:
            ocrData
    });


    console.log(
        "📄 PackCheck: Verification sent for PDF report."
    );


    return verification;
}


// ============================================================
// 15. WATCH FOR FoSCoS RESULT
// ============================================================

function watchForVerificationResult() {

    console.log(
        "👀 Verification watcher started"
    );


    let attempts = 0;


    const interval =
        setInterval(() => {

            attempts++;


            const result =
                extractFSSAIResult();


            if (result) {

                clearInterval(
                    interval
                );


                console.log(
                    "🏛️ Official FSSAI record detected."
                );


                runVerification();

                return;
            }


            if (attempts >= 300) {

                clearInterval(
                    interval
                );

                console.log(
                    "🛑 PackCheck: Result monitoring stopped after 5 minutes."
                );
            }

        }, 1000);
}


// ============================================================
// 16. OPEN FBO SEARCH
// ============================================================

function openFBOSearch() {

    console.log(
        "🔍 PackCheck: Searching for FBO Search..."
    );


    const elements = [

        ...document.querySelectorAll(
            "a, button, span, div"
        )

    ];


    const fboElement =
        elements.find(
            element => {

                const text =
                    (element.innerText || "")
                        .replace(/\s+/g, " ")
                        .trim()
                        .toLowerCase();

                return text ===
                    "fbo search";
            }
        );


    if (!fboElement) {

        console.log(
            "⏳ PackCheck: FBO Search not visible yet..."
        );

        return false;
    }


    console.log(
        "🚀 PackCheck: FBO Search found!",
        fboElement
    );


    fboElement.click();


    console.log(
        "✅ PackCheck: FBO Search clicked."
    );


    return true;
}


// ============================================================
// 17. START PACKCHECK
// ============================================================

async function startPackCheck() {

    console.log(
        "🚀 PackCheck started"
    );


    // --------------------------------------------------------
    // Load Gemini extraction
    // --------------------------------------------------------

    const loaded =
        await loadPackCheckData();


    if (!loaded) {

        console.error(
            "❌ PackCheck stopped: Gemini data unavailable."
        );

        return;
    }


    if (
        !ocrData ||
        !ocrData.licenseNo
    ) {

        console.error(
            "❌ PackCheck stopped: No FSSAI number extracted."
        );

        return;
    }


    console.log(
        "✅ Gemini extraction loaded."
    );


    let fboOpened = false;
    let fieldsFilled = false;

    let attempts = 0;


    const interval =
        setInterval(() => {

            attempts++;


            // ------------------------------------------------
            // Open FBO Search
            // ------------------------------------------------

            if (!fboOpened) {

                if (openFBOSearch()) {

                    fboOpened = true;

                    console.log(
                        "✅ PackCheck: FBO Search opened."
                    );
                }
            }


            // ------------------------------------------------
            // Fill FSSAI
            // ------------------------------------------------

            if (
                fboOpened &&
                !fieldsFilled
            ) {

                if (fillFoSCoS()) {

                    fieldsFilled = true;


                    console.log(
                        "✅ PackCheck: FSSAI number filled."
                    );


                    clearInterval(
                        interval
                    );


                    // Wait for manual CAPTCHA + Search
                    watchForVerificationResult();
                }
            }


            // ------------------------------------------------
            // Stop startup after 30 seconds
            // ------------------------------------------------

            if (attempts >= 30) {

                clearInterval(
                    interval
                );

                console.log(
                    "🛑 PackCheck: Startup stopped."
                );
            }

        }, 1000);
}


// ============================================================
// 18. PAGE READY
// ============================================================

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        startPackCheck
    );

} else {

    startPackCheck();
}