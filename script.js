document.addEventListener("DOMContentLoaded", function () {
    // Button actions
    document.getElementById("auditBtn").addEventListener("click", function () {
        alert("Redirecting to Security Audit request form...");
        window.location.href = "https://aegisvault.com/security-audit";
    });

    document.getElementById("howItWorksBtn").addEventListener("click", function () {
        window.scrollTo({ top: document.querySelector(".features").offsetTop, behavior: "smooth" });
    });

    document.getElementById("basicScanBtn").addEventListener("click", function () {
        alert("Redirecting to Basic Scan sign-up...");
        window.location.href = "https://aegisvault.com/basic-scan";
    });

    document.getElementById("advancedAuditBtn").addEventListener("click", function () {
        alert("Redirecting to Advanced Audit checkout...");
        window.location.href = "https://aegisvault.com/advanced-audit";
    });

    document.getElementById("contactUsBtn").addEventListener("click", function () {
        alert("Opening Contact Form...");
        window.location.href = "mailto:support@aegisvault.com";
    });
});
