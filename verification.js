// ============================================================
// PACKCHECK - VERIFICATION ENGINE
// ============================================================


// ============================================================
// 1. NORMALIZE TEXT
// ============================================================

function normalize(text) {

    if (!text) return "";

    return text
        .toString()
        .toLowerCase()
        .replace(/[.,]/g, "")
        .replace(/\s+/g, " ")
        .trim();
}


// ============================================================
// 2. NORMALIZE LICENSE NUMBER
// ============================================================

function normalizeLicense(text) {

    if (!text) return "";

    return text
        .toString()
        .replace(/\D/g, "");
}


// ============================================================
// 3. COMPARE LICENSE NUMBER
// ============================================================

function compareLicense(packetValue, officialValue) {

    const packet = normalizeLicense(packetValue);
    const official = normalizeLicense(officialValue);

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
// 4. COMPARE COMPANY NAME
// ============================================================

function compareCompanyName(packetValue, officialValue) {

    const packet = normalize(packetValue);
    const official = normalize(officialValue);

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
// 5. COMPARE ADDRESS
// ============================================================

function compareAddress(packetValue, officialValue) {

    const packet = normalize(packetValue);
    const official = normalize(officialValue);

    if (!packet || !official) {

        return {
            status: "UNKNOWN",
            packet: packetValue,
            official: officialValue
        };
    }


    // Exact normalized match
    if (packet === official) {

        return {
            status: "MATCH",
            packet: packetValue,
            official: officialValue
        };
    }


    // Check whether important address parts overlap
    const packetWords = packet.split(" ");
    const officialWords = official.split(" ");

    const importantWords = packetWords.filter(word =>
        word.length >= 4
    );


    const matchedWords = importantWords.filter(word =>
        officialWords.includes(word)
    );


    const similarity =
        importantWords.length > 0
            ? matchedWords.length / importantWords.length
            : 0;


    // Strong overlap
    if (similarity >= 0.7) {

        return {
            status: "MATCH",
            packet: packetValue,
            official: officialValue,
            similarity: similarity
        };
    }


    // Partial overlap
    if (similarity >= 0.4) {

        return {
            status: "REQUIRES REVIEW",
            packet: packetValue,
            official: officialValue,
            similarity: similarity
        };
    }


    return {
        status: "MISMATCH",
        packet: packetValue,
        official: officialValue,
        similarity: similarity
    };
}


// ============================================================
// 6. VERIFY PRODUCT
// ============================================================

function verifyProduct(packetData, officialData) {

    if (!packetData || !officialData) {

        return {
            overallStatus: "REQUIRES REVIEW",
            reason: "Missing packet or official data"
        };
    }


    const results = {

        licenseNo: compareLicense(
            packetData.licenseNo,
            officialData.licenseNo
        ),

        companyName: compareCompanyName(
            packetData.companyName,
            officialData.companyName
        ),

        address: compareAddress(
            packetData.address,
            officialData.address
        ),

        licenseStatus: {

            status:
                normalize(officialData.status) === "active"
                    ? "MATCH"
                    : "MISMATCH",

            official: officialData.status
        }
    };


    const values = Object.values(results);


    const mismatches = values.filter(
        result => result.status === "MISMATCH"
    );


    const reviews = values.filter(
        result => result.status === "REQUIRES REVIEW"
    );


    const unknown = values.filter(
        result => result.status === "UNKNOWN"
    );


    let overallStatus;


    if (mismatches.length > 0) {

        overallStatus = "MISMATCH";

    } else if (
        reviews.length > 0 ||
        unknown.length > 0
    ) {

        overallStatus = "REQUIRES REVIEW";

    } else {

        overallStatus = "VERIFIED";
    }


    return {

        overallStatus,

        results
    };
}