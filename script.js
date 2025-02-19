document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript Loaded!");
    
    // Remove popups and replace with redirects
    window.redirectToAudit = function() {
        window.location.href = "https://your-security-audit-form.com";
    };
    
    window.redirectToBasicScan = function() {
        window.location.href = "https://your-basic-scan-form.com";
    };
    
    window.redirectToAdvancedAudit = function() {
        window.location.href = "https://your-advanced-audit-form.com";
    };
    
    window.redirectToContact = function() {
        window.location.href = "https://your-contact-page.com";
    };
    
    window.scrollToSection = function(sectionId) {
        document.getElementById(sectionId).scrollIntoView({ behavior: "smooth" });
    };
    
    window.scrollToTop = function() {
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    // Back to Top Button Visibility
    window.addEventListener("scroll", function() {
        document.getElementById("backToTop").style.display = window.scrollY > 300 ? "block" : "none";
    });

    // Newsletter Form
    document.getElementById("newsletter-form").addEventListener("submit", function(event) {
        event.preventDefault();
        alert("Subscribed successfully!");
    });
});
